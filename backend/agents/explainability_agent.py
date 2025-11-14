"""
PROJECT LUMEN - Explainability Agent
Generates human-readable explanations of audit findings
"""

from typing import Dict, List
import openai
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
from backend.config import settings, EXPLANATION_PROMPT
from backend.utils.logger import logger, log_agent_action, log_error


class ExplainabilityAgent:
    """Generates natural language explanations"""

    def __init__(self):
        # Set API key based on provider
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        elif settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY and HAS_GEMINI:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    def explain(self, findings: Dict, context_chunks: List[Dict]) -> str:
        """
        Generate explanation of audit findings using LLM

        Args:
            findings: Combined findings from all agents
            context_chunks: RAG context chunks used

        Returns:
            Human-readable explanation

        Raises:
            ValueError: If LLM provider is not properly configured
        """
        logger.info("Explainability Agent: Generating explanation with LLM")

        if settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("Explainability with OpenAI requires OPENAI_API_KEY to be configured")
            explanation = self._explain_with_openai(findings, context_chunks)
        elif settings.LLM_PROVIDER == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("Explainability with Gemini requires GEMINI_API_KEY to be configured")
            explanation = self._explain_with_gemini(findings, context_chunks)
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}. Use 'openai' or 'gemini'")

        log_agent_action("ExplainabilityAgent", "explain", {"length": len(explanation)})
        return explanation

    def _explain_with_openai(self, findings: Dict, context_chunks: List[Dict]) -> str:
        """
        Generate explanation using OpenAI LLM

        Args:
            findings: Audit findings
            context_chunks: Context chunks

        Returns:
            Explanation text
        """
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

        if not explanation:
            raise RuntimeError("OpenAI returned empty explanation")

        logger.info("Generated explanation with OpenAI LLM")
        return explanation

    def _explain_with_gemini(self, findings: Dict, context_chunks: List[Dict]) -> str:
        """
        Generate explanation using Gemini LLM with safety filter handling

        Args:
            findings: Audit findings
            context_chunks: Context chunks

        Returns:
            Explanation text
        """
        if not HAS_GEMINI:
            raise RuntimeError("Gemini SDK not installed. Install with: pip install google-generativeai")

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
            f"You are an AI financial analyst providing clear, professional audit explanations.\n\n{prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=800,
            )
        )

        # Check if response was blocked by safety filters
        if not response.candidates or not response.candidates[0].content.parts:
            logger.warning("Gemini blocked response (safety filter), generating basic explanation")
            audit_status = findings.get('audit', {}).get('status', 'unknown')
            return f"Audit completed with status: {audit_status}. Detailed explanation unavailable due to safety filter."

        explanation = response.text.strip()

        if not explanation:
            raise RuntimeError("Gemini returned empty explanation")

        logger.info("Generated explanation with Gemini LLM")
        return explanation


# Global explainability agent instance
explainability_agent = None


def get_explainability_agent() -> ExplainabilityAgent:
    """Get global explainability agent instance"""
    global explainability_agent
    if explainability_agent is None:
        explainability_agent = ExplainabilityAgent()
    return explainability_agent
