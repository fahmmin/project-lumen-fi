"""
PROJECT LUMEN - Query Enhancement
Enhances search queries using LLM for better retrieval
"""

from typing import Optional
import openai
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
from backend.config import settings, HYDE_PROMPT
from backend.utils.logger import logger, log_error


class QueryEnhancer:
    """Enhances search queries using LLM"""

    def __init__(
        self,
        model: str = settings.LLM_MODEL,
        temperature: float = 0.3,
        max_tokens: int = 100
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set API key based on provider
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        elif settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY and HAS_GEMINI:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    def enhance_query(self, query: str) -> str:
        """
        Enhance a search query by adding relevant financial/policy terms

        Args:
            query: Original search query

        Returns:
            Enhanced query string

        Raises:
            ValueError: If no LLM provider is configured
        """
        # Simple prompt that won't trigger safety filters
        prompt = f"Expand this financial search query with 3-5 relevant keywords: {query}"

        if settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("Query enhancement with OpenAI requires OPENAI_API_KEY to be configured")
            return self._enhance_with_openai(prompt, query)
        elif settings.LLM_PROVIDER == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("Query enhancement with Gemini requires GEMINI_API_KEY to be configured")
            return self._enhance_with_gemini(prompt, query)
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}. Use 'openai' or 'gemini'")

    def _enhance_with_openai(self, prompt: str, original_query: str) -> str:
        """Enhance query using OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a search query expert. Return only the expanded query keywords."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            enhanced = response.choices[0].message.content.strip()
            combined_query = f"{original_query} {enhanced}"
            logger.info(f"Enhanced query with OpenAI: {original_query} -> {combined_query}")
            return combined_query
        except Exception as e:
            logger.warning(f"Query enhancement failed, using original: {e}")
            return original_query

    def _enhance_with_gemini(self, prompt: str, original_query: str) -> str:
        """Enhance query using Gemini API with safety filter handling"""
        if not HAS_GEMINI:
            logger.warning("Gemini SDK not installed, using original query")
            return original_query

        try:
            # Initialize Gemini model with safety settings
            safety_settings = {
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE',
            }

            model = genai.GenerativeModel(
                model_name=self.model,
                safety_settings=safety_settings
            )

            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )

            # Check if response was blocked
            if not response.candidates or not response.candidates[0].content.parts:
                logger.warning(f"Gemini blocked response (safety filter), using original query")
                return original_query

            enhanced = response.text.strip()
            combined_query = f"{original_query} {enhanced}"
            logger.info(f"Enhanced query with Gemini: {original_query} -> {combined_query}")
            return combined_query

        except Exception as e:
            logger.warning(f"Query enhancement failed, using original: {e}")
            return original_query


# Global query enhancer
query_enhancer = None


def get_query_enhancer() -> QueryEnhancer:
    """Get global query enhancer instance"""
    global query_enhancer
    if query_enhancer is None:
        query_enhancer = QueryEnhancer()
    return query_enhancer


def generate_hyde(query: str) -> str:
    """
    Enhance query for better retrieval (replaces HyDE)

    Args:
        query: Search query

    Returns:
        Enhanced query
    """
    enhancer = get_query_enhancer()
    return enhancer.enhance_query(query)
