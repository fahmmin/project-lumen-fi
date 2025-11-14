"""
PROJECT LUMEN - Compliance Agent
Validates invoices against financial policies using RAG
"""

import json
from typing import Dict, List
import openai
from backend.rag.retriever import get_hybrid_retriever
from backend.config import settings, COMPLIANCE_PROMPT
from backend.utils.logger import logger, log_agent_action, log_error


class ComplianceAgent:
    """Validates compliance with financial policies"""

    def __init__(self):
        self.retriever = get_hybrid_retriever()

        # Set API key if using OpenAI
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY

    def check_compliance(self, invoice_data: Dict) -> Dict:
        """
        Check invoice compliance against policies

        Args:
            invoice_data: Invoice data dictionary

        Returns:
            Compliance findings
        """
        logger.info(f"Compliance Agent: Checking compliance for {invoice_data.get('vendor', 'Unknown')}")

        # Build compliance query
        query = self._build_compliance_query(invoice_data)

        # Retrieve relevant policies
        policy_chunks = self.retriever.retrieve(query, use_hyde=True)

        if not policy_chunks:
            logger.warning("No policy documents found for compliance check")
            return {
                "compliant": True,
                "violations": [],
                "confidence": 0.0,
                "explanation": "No policy documents available for compliance verification",
                "context_used": []
            }

        # Analyze compliance
        findings = self._analyze_compliance(invoice_data, policy_chunks)

        log_agent_action("ComplianceAgent", "check_compliance", {
            "compliant": findings["compliant"],
            "violations": len(findings["violations"])
        })

        return findings

    def _build_compliance_query(self, invoice_data: Dict) -> str:
        """
        Build query for policy retrieval

        Args:
            invoice_data: Invoice data

        Returns:
            Compliance query string
        """
        vendor = invoice_data.get('vendor', '')
        amount = invoice_data.get('amount', 0)
        category = invoice_data.get('category', '')

        query_parts = []

        if category:
            query_parts.append(f"financial policy for {category}")

        if amount > 10000:
            query_parts.append("large purchase approval requirements")

        if amount > 50000:
            query_parts.append("high value transaction policies")

        query_parts.append("invoice compliance rules")
        query_parts.append("expense policy")

        return " ".join(query_parts)

    def _analyze_compliance(self, invoice_data: Dict, policy_chunks: List[Dict]) -> Dict:
        """
        Analyze compliance using LLM

        Args:
            invoice_data: Invoice data
            policy_chunks: Retrieved policy chunks

        Returns:
            Compliance findings
        """
        try:
            if settings.LLM_PROVIDER == "openai":
                return self._analyze_with_llm(invoice_data, policy_chunks)
            else:
                return self._analyze_rule_based(invoice_data, policy_chunks)

        except Exception as e:
            log_error(e, "Compliance analysis")
            return self._analyze_rule_based(invoice_data, policy_chunks)

    def _analyze_with_llm(self, invoice_data: Dict, policy_chunks: List[Dict]) -> Dict:
        """
        Analyze compliance using LLM

        Args:
            invoice_data: Invoice data
            policy_chunks: Policy chunks

        Returns:
            Compliance findings
        """
        try:
            # Format context
            context = "\n\n".join([f"Policy {i+1}: {chunk['text']}" for i, chunk in enumerate(policy_chunks)])

            # Format prompt
            prompt = COMPLIANCE_PROMPT.format(
                invoice_data=json.dumps(invoice_data, indent=2),
                context=context
            )

            # Call LLM
            response = openai.ChatCompletion.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a financial compliance auditor. Analyze invoices against policies and return structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

            result_text = response.choices[0].message.content.strip()

            # Extract JSON
            result = self._extract_json(result_text)

            if result:
                # Add context information
                result['context_used'] = [chunk.get('id', i) for i, chunk in enumerate(policy_chunks)]
                logger.info("Compliance analysis completed with LLM")
                return result
            else:
                logger.warning("LLM did not return valid JSON for compliance")
                return self._analyze_rule_based(invoice_data, policy_chunks)

        except Exception as e:
            log_error(e, "LLM compliance analysis")
            return self._analyze_rule_based(invoice_data, policy_chunks)

    def _analyze_rule_based(self, invoice_data: Dict, policy_chunks: List[Dict]) -> Dict:
        """
        Rule-based compliance analysis fallback

        Args:
            invoice_data: Invoice data
            policy_chunks: Policy chunks

        Returns:
            Compliance findings
        """
        logger.info("Using rule-based compliance analysis")

        violations = []
        amount = invoice_data.get('amount', 0)
        category = invoice_data.get('category', '')

        # Simple rule-based checks
        if amount > 10000 and not invoice_data.get('approval_id'):
            violations.append("Large purchases over $10,000 require approval (no approval ID found)")

        if amount > 50000:
            violations.append("High-value transaction over $50,000 requires additional review")

        if category == "Uncategorized":
            violations.append("Invoice must have a valid category")

        # Check for specific policy mentions in retrieved chunks
        policy_text = " ".join([chunk['text'].lower() for chunk in policy_chunks])

        if "approval required" in policy_text and not invoice_data.get('approval_id'):
            violations.append("Policy indicates approval required, but no approval found")

        if "receipt mandatory" in policy_text and not invoice_data.get('receipt_attached'):
            violations.append("Policy requires receipt attachment")

        compliant = len(violations) == 0

        return {
            "compliant": compliant,
            "violations": violations,
            "confidence": 0.6 if not compliant else 0.8,
            "explanation": "Rule-based compliance check performed. " + (
                "No violations found." if compliant else f"Found {len(violations)} violation(s)."
            ),
            "context_used": [chunk.get('id', i) for i, chunk in enumerate(policy_chunks)]
        }

    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from LLM response"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract from code blocks
        import re
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        return None


# Global compliance agent instance
compliance_agent = None


def get_compliance_agent() -> ComplianceAgent:
    """Get global compliance agent instance"""
    global compliance_agent
    if compliance_agent is None:
        compliance_agent = ComplianceAgent()
    return compliance_agent
