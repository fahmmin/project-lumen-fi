"""
PROJECT LUMEN - Compliance Agent
Validates invoices against financial policies using RAG
"""

import json
from typing import Dict, List
import openai
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
from backend.rag.retriever import get_hybrid_retriever
from backend.config import settings, COMPLIANCE_PROMPT
from backend.utils.logger import logger, log_agent_action, log_error


class ComplianceAgent:
    """Validates compliance with financial policies"""

    def __init__(self):
        self.retriever = get_hybrid_retriever()

        # Set API key based on provider
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        elif settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY and HAS_GEMINI:
            genai.configure(api_key=settings.GEMINI_API_KEY)

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

        Raises:
            ValueError: If LLM provider is not properly configured
        """
        if settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("Compliance analysis with OpenAI requires OPENAI_API_KEY to be configured")
            return self._analyze_with_openai(invoice_data, policy_chunks)
        elif settings.LLM_PROVIDER == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("Compliance analysis with Gemini requires GEMINI_API_KEY to be configured")
            return self._analyze_with_gemini(invoice_data, policy_chunks)
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}. Use 'openai' or 'gemini'")

    def _analyze_with_openai(self, invoice_data: Dict, policy_chunks: List[Dict]) -> Dict:
        """
        Analyze compliance using OpenAI LLM

        Args:
            invoice_data: Invoice data
            policy_chunks: Policy chunks

        Returns:
            Compliance findings
        """
        # Format context
        context = "\n\n".join([f"Policy {i+1}: {chunk['text']}" for i, chunk in enumerate(policy_chunks)])

        # Format prompt
        prompt = COMPLIANCE_PROMPT.format(
            invoice_data=json.dumps(invoice_data, indent=2),
            context=context
        )

        # Call OpenAI
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

        if not result:
            raise RuntimeError("OpenAI did not return valid JSON for compliance analysis")

        # Add context information
        result['context_used'] = [chunk.get('id', i) for i, chunk in enumerate(policy_chunks)]
        logger.info("Compliance analysis completed with OpenAI LLM")
        return result

    def _analyze_with_gemini(self, invoice_data: Dict, policy_chunks: List[Dict]) -> Dict:
        """
        Analyze compliance using Gemini LLM with safety filter handling

        Args:
            invoice_data: Invoice data
            policy_chunks: Policy chunks

        Returns:
            Compliance findings
        """
        if not HAS_GEMINI:
            raise RuntimeError("Gemini SDK not installed. Install with: pip install google-generativeai")

        # Format context
        context = "\n\n".join([f"Policy {i+1}: {chunk['text']}" for i, chunk in enumerate(policy_chunks)])

        # Format prompt
        prompt = COMPLIANCE_PROMPT.format(
            invoice_data=json.dumps(invoice_data, indent=2),
            context=context
        )

        # Initialize Gemini model with safety settings
        safety_settings = {
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
        }

        model = genai.GenerativeModel(
            model_name=settings.LLM_MODEL,
            safety_settings=safety_settings
        )

        # Generate response
        response = model.generate_content(
            f"You are a financial compliance auditor. Analyze invoices against policies and return structured JSON.\n\n{prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=500,
            )
        )

        # Check if response was blocked by safety filters
        if not response.candidates or not response.candidates[0].content.parts:
            logger.warning("Gemini blocked response (safety filter), returning compliant by default")
            return {
                "compliant": True,
                "violations": [],
                "confidence": 0.5,
                "explanation": "Unable to analyze - safety filter triggered. Defaulting to compliant.",
                "context_used": [chunk.get('id', i) for i, chunk in enumerate(policy_chunks)]
            }

        result_text = response.text.strip()

        # Extract JSON
        result = self._extract_json(result_text)

        if not result:
            raise RuntimeError("Gemini did not return valid JSON for compliance analysis")

        # Add context information
        result['context_used'] = [chunk.get('id', i) for i, chunk in enumerate(policy_chunks)]
        logger.info("Compliance analysis completed with Gemini LLM")
        return result

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
