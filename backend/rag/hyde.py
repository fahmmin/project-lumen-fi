"""
PROJECT LUMEN - HyDE (Hypothetical Document Embeddings)
Generates hypothetical documents for improved retrieval
"""

from typing import Optional
import openai
from backend.config import settings, HYDE_PROMPT
from backend.utils.logger import logger, log_error


class HyDEGenerator:
    """Generates hypothetical documents for queries"""

    def __init__(
        self,
        model: str = settings.LLM_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 200
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set API key if using OpenAI
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY

    def generate_hypothetical_document(self, query: str) -> Optional[str]:
        """
        Generate a hypothetical document for a query

        Args:
            query: User query

        Returns:
            Hypothetical document text or None if failed
        """
        try:
            prompt = HYDE_PROMPT.format(query=query)

            if settings.LLM_PROVIDER == "openai":
                return self._generate_openai(prompt)
            else:
                # Fallback: return expanded query
                logger.warning("No LLM configured, using query expansion fallback")
                return self._fallback_expansion(query)

        except Exception as e:
            log_error(e, "HyDE generation")
            return self._fallback_expansion(query)

    def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial document generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            hypothetical_doc = response.choices[0].message.content.strip()
            logger.info(f"Generated HyDE document ({len(hypothetical_doc)} chars)")
            return hypothetical_doc

        except Exception as e:
            log_error(e, "OpenAI HyDE generation")
            raise

    def _fallback_expansion(self, query: str) -> str:
        """
        Fallback: Simple query expansion

        Args:
            query: Original query

        Returns:
            Expanded query
        """
        # Add financial context keywords
        expansions = {
            "invoice": "invoice receipt payment transaction vendor purchase",
            "tax": "tax taxation VAT GST sales tax income tax",
            "fraud": "fraud anomaly suspicious unusual irregular",
            "compliance": "compliance policy regulation rule requirement standard",
            "audit": "audit review verification check validation",
            "expense": "expense cost spending expenditure payment",
        }

        # Expand query with related terms
        expanded = query
        for keyword, expansion in expansions.items():
            if keyword.lower() in query.lower():
                expanded += f" {expansion}"

        logger.info("Using fallback query expansion for HyDE")
        return expanded


# Global HyDE generator
hyde_generator = None


def get_hyde_generator() -> HyDEGenerator:
    """Get global HyDE generator instance"""
    global hyde_generator
    if hyde_generator is None:
        hyde_generator = HyDEGenerator()
    return hyde_generator


def generate_hyde(query: str) -> str:
    """
    Generate HyDE document for query

    Args:
        query: Search query

    Returns:
        Hypothetical document
    """
    generator = get_hyde_generator()
    result = generator.generate_hypothetical_document(query)
    return result if result else query
