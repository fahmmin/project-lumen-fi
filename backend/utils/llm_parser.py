"""
PROJECT LUMEN - LLM Parser
LLM-based document parsing for structured data extraction using Ollama
"""

import json
import re
from typing import Dict, Optional
from backend.config import settings, EXTRACTION_PROMPT, DOCUMENT_SCHEMA
from backend.utils.logger import logger, log_error
from backend.utils.ollama_client import ollama_client


class LLMParser:
    """LLM-based parser for extracting structured data from text using Ollama"""

    def __init__(
        self,
        model: str = settings.OLLAMA_MODEL,
        temperature: float = settings.LLM_TEMPERATURE,
        max_tokens: int = settings.LLM_MAX_TOKENS
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(f"LLMParser initialized with Ollama model: {self.model}")

    def parse_document(self, text: str) -> Optional[Dict]:
        """
        Parse document text into structured JSON using Ollama LLM

        Args:
            text: Extracted document text

        Returns:
            Structured document data or None if parsing fails

        Raises:
            RuntimeError: If LLM parsing fails
        """
        try:
            prompt = EXTRACTION_PROMPT.format(text=text)

            logger.info("Parsing document with Ollama LLM...")

            # Generate response from Ollama
            response = ollama_client.generate(
                prompt=prompt,
                system_message="You are a precise financial document parser. Extract vendor, amount, date, category, items, invoice_number, and payment_method. Return only valid JSON.",
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            logger.info(f"Ollama response received: {len(response)} chars")

            # Extract JSON from response
            parsed_data = ollama_client.parse_json_response(response)

            if parsed_data:
                logger.info(f"Successfully parsed document: {parsed_data.get('vendor', 'unknown')}")
                return parsed_data
            else:
                logger.warning("Failed to extract JSON from Ollama response")
                logger.debug(f"Raw response: {response[:200]}...")
                return None

        except Exception as e:
            log_error(f"Ollama parsing error: {str(e)}")
            raise RuntimeError(f"Failed to parse document with Ollama: {str(e)}")

    def extract_fields(self, text: str) -> Dict:
        """
        Extract structured fields from document text

        Args:
            text: Document text

        Returns:
            Dictionary with extracted fields
        """
        try:
            result = self.parse_document(text)

            if result:
                return result
            else:
                logger.warning("LLM parsing failed, returning empty result")
                return {
                    "vendor": None,
                    "date": None,
                    "amount": None,
                    "tax": None,
                    "category": None,
                    "items": [],
                    "invoice_number": None,
                    "payment_method": None,
                    "error": "Failed to parse with LLM"
                }

        except Exception as e:
            logger.error(f"Field extraction error: {str(e)}")
            return {
                "vendor": None,
                "date": None,
                "amount": None,
                "error": str(e)
            }


# Global parser instance
llm_parser = LLMParser()


def parse_document(text: str) -> Optional[Dict]:
    """
    Convenience function to parse document using global LLM parser

    Args:
        text: Document text to parse

    Returns:
        Parsed fields or None
    """
    return llm_parser.parse_document(text)
