"""
PROJECT LUMEN - Explainability Agent
Generates human-readable explanations of audit findings
"""

from typing import Dict, List
import openai
from backend.config import settings, EXPLANATION_PROMPT
from backend.utils.logger import logger, log_agent_action, log_error


class ExplainabilityAgent:
    """Generates natural language explanations"""

    def __init__(self):
        # Set API key if using OpenAI
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY

    def explain(self, findings: Dict, context_chunks: List[Dict]) -> str:
        """
        Generate explanation of audit findings

        Args:
            findings: Combined findings from all agents
            context_chunks: RAG context chunks used

        Returns:
            Human-readable explanation
        """
        logger.info("Explainability Agent: Generating explanation")

        try:
            if settings.LLM_PROVIDER == "openai":
                explanation = self._explain_with_llm(findings, context_chunks)
            else:
                explanation = self._explain_template(findings, context_chunks)

            log_agent_action("ExplainabilityAgent", "explain", {"length": len(explanation)})
            return explanation

        except Exception as e:
            log_error(e, "Explanation generation")
            return self._explain_template(findings, context_chunks)

    def _explain_with_llm(self, findings: Dict, context_chunks: List[Dict]) -> str:
        """
        Generate explanation using LLM

        Args:
            findings: Audit findings
            context_chunks: Context chunks

        Returns:
            Explanation text
        """
        try:
            # Format findings
            import json
            findings_text = json.dumps(findings, indent=2)

            # Format context
            context_text = "\n\n".join([
                f"Context {i+1}: {chunk['text'][:200]}..."
                for i, chunk in enumerate(context_chunks[:3])
            ])

            # Generate explanation
            prompt = EXPLANATION_PROMPT.format(
                findings=findings_text,
                context=context_text
            )

            response = openai.ChatCompletion.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are an AI financial analyst providing clear, professional audit explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )

            explanation = response.choices[0].message.content.strip()
            logger.info("Generated explanation with LLM")
            return explanation

        except Exception as e:
            log_error(e, "LLM explanation generation")
            return self._explain_template(findings, context_chunks)

    def _explain_template(self, findings: Dict, context_chunks: List[Dict]) -> str:
        """
        Template-based explanation fallback

        Args:
            findings: Audit findings
            context_chunks: Context chunks

        Returns:
            Explanation text
        """
        logger.info("Using template-based explanation")

        explanation_parts = []

        # Introduction
        explanation_parts.append("## Audit Analysis Summary\n")

        # Audit findings
        audit_findings = findings.get('audit', {})
        if audit_findings:
            explanation_parts.append("### Audit Results")

            status = audit_findings.get('status', 'unknown')
            if status == 'pass':
                explanation_parts.append("✓ The invoice passed standard audit checks.")
            elif status == 'warning':
                explanation_parts.append("⚠ The invoice has minor issues that require attention.")
            elif status == 'error':
                explanation_parts.append("✗ The invoice has significant errors that must be corrected.")

            # Duplicates
            duplicates = audit_findings.get('duplicates', [])
            if duplicates:
                explanation_parts.append(f"\n**Duplicate Detection:** {len(duplicates)} potential duplicate(s) found:")
                for dup in duplicates[:3]:
                    explanation_parts.append(f"- {dup}")

            # Mismatches
            mismatches = audit_findings.get('mismatches', [])
            if mismatches:
                explanation_parts.append(f"\n**Pattern Mismatches:** {len(mismatches)} anomaly(ies) detected:")
                for mismatch in mismatches[:3]:
                    explanation_parts.append(f"- {mismatch}")

            # Total errors
            total_errors = audit_findings.get('total_errors', [])
            if total_errors:
                explanation_parts.append(f"\n**Calculation Errors:** {len(total_errors)} error(s) found:")
                for error in total_errors:
                    explanation_parts.append(f"- {error}")

            # Anomalies
            anomalies = audit_findings.get('anomalies', [])
            if anomalies:
                explanation_parts.append(f"\n**Amount Anomalies:** {len(anomalies)} unusual pattern(s):")
                for anomaly in anomalies[:3]:
                    explanation_parts.append(f"- {anomaly}")

            explanation_parts.append("")

        # Compliance findings
        compliance_findings = findings.get('compliance', {})
        if compliance_findings:
            explanation_parts.append("### Compliance Assessment")

            compliant = compliance_findings.get('compliant', True)
            confidence = compliance_findings.get('confidence', 0.0)

            if compliant:
                explanation_parts.append(f"✓ The invoice complies with financial policies (confidence: {confidence:.0%}).")
            else:
                explanation_parts.append(f"✗ The invoice has compliance violations (confidence: {confidence:.0%}).")

            violations = compliance_findings.get('violations', [])
            if violations:
                explanation_parts.append(f"\n**Violations:** {len(violations)} policy violation(s):")
                for violation in violations:
                    explanation_parts.append(f"- {violation}")

            comp_explanation = compliance_findings.get('explanation', '')
            if comp_explanation:
                explanation_parts.append(f"\n{comp_explanation}")

            explanation_parts.append("")

        # Fraud findings
        fraud_findings = findings.get('fraud', {})
        if fraud_findings:
            explanation_parts.append("### Fraud Detection Analysis")

            anomaly_detected = fraud_findings.get('anomaly_detected', False)
            risk_score = fraud_findings.get('risk_score', 0.0)

            if anomaly_detected:
                risk_level = "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.4 else "LOW"
                explanation_parts.append(f"⚠ Anomaly detected with {risk_level} risk (score: {risk_score:.2f})")
            else:
                explanation_parts.append(f"✓ No fraud indicators detected (risk score: {risk_score:.2f})")

            indicators = fraud_findings.get('suspicious_indicators', [])
            if indicators:
                explanation_parts.append(f"\n**Suspicious Indicators:** {len(indicators)} pattern(s):")
                for indicator in indicators[:5]:
                    explanation_parts.append(f"- {indicator}")

            methods = fraud_findings.get('methods_used', [])
            if methods:
                explanation_parts.append(f"\n**Detection Methods:** {', '.join(methods)}")

            explanation_parts.append("")

        # Context information
        if context_chunks:
            explanation_parts.append(f"### Analysis Context")
            explanation_parts.append(f"This analysis utilized {len(context_chunks)} relevant policy documents and historical data points.")

        # Recommendations
        explanation_parts.append("\n### Recommended Actions")

        has_issues = False
        if audit_findings.get('status') in ['warning', 'error']:
            has_issues = True
        if not compliance_findings.get('compliant', True):
            has_issues = True
        if fraud_findings.get('anomaly_detected', False):
            has_issues = True

        if has_issues:
            explanation_parts.append("1. Review flagged issues with the vendor")
            explanation_parts.append("2. Request supporting documentation for anomalies")
            explanation_parts.append("3. Obtain necessary approvals before processing")
            explanation_parts.append("4. Update records to correct identified errors")
        else:
            explanation_parts.append("✓ The invoice appears valid and can proceed to payment processing.")

        return "\n".join(explanation_parts)


# Global explainability agent instance
explainability_agent = None


def get_explainability_agent() -> ExplainabilityAgent:
    """Get global explainability agent instance"""
    global explainability_agent
    if explainability_agent is None:
        explainability_agent = ExplainabilityAgent()
    return explainability_agent
