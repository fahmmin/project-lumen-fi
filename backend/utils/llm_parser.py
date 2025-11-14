"""
PROJECT LUMEN - LLM Parser
LLM-based document parsing for structured data extraction
"""

import json
import re
from typing import Dict, Optional
import openai
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
from backend.config import settings, EXTRACTION_PROMPT, DOCUMENT_SCHEMA
from backend.utils.logger import logger, log_error


class LLMParser:
    """LLM-based parser for extracting structured data from text"""

    def __init__(
        self,
        model: str = settings.LLM_MODEL,
        temperature: float = settings.LLM_TEMPERATURE,
        max_tokens: int = settings.LLM_MAX_TOKENS
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Set API keys based on provider
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        elif settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY and HAS_GEMINI:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    def parse_document(self, text: str) -> Optional[Dict]:
        """
        Parse document text into structured JSON using LLM

        Args:
            text: Extracted document text

        Returns:
            Structured document data or None if parsing fails

        Raises:
            ValueError: If no LLM provider is configured
            RuntimeError: If LLM parsing fails
        """
        if settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI provider selected but OPENAI_API_KEY is not configured")
            return self._parse_openai(text)
        elif settings.LLM_PROVIDER == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("Gemini provider selected but GEMINI_API_KEY is not configured")
            return self._parse_gemini(text)
        else:
            raise ValueError(f"Invalid LLM provider: {settings.LLM_PROVIDER}. Must be 'openai' or 'gemini'")

    def _parse_openai(self, text: str) -> Dict:
        """Parse using OpenAI API - requires valid API key"""
        prompt = EXTRACTION_PROMPT.format(text=text)

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise financial document parser. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        result_text = response.choices[0].message.content.strip()

        # Extract JSON from response
        parsed_data = self._extract_json(result_text)

        if not parsed_data:
            raise RuntimeError("LLM did not return valid JSON. Unable to parse document.")

        logger.info("Successfully parsed document with OpenAI LLM")
        return self._validate_and_clean(parsed_data)

    def _parse_gemini(self, text: str) -> Dict:
        """Parse using Google Gemini API - requires valid API key and SDK"""
        if not HAS_GEMINI:
            raise RuntimeError("Gemini SDK not installed. Install with: pip install google-generativeai")

        prompt = EXTRACTION_PROMPT.format(text=text)

        # Initialize Gemini model
        model = genai.GenerativeModel(self.model)

        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
        )

        result_text = response.text.strip()

        # Extract JSON from response
        parsed_data = self._extract_json(result_text)

        if not parsed_data:
            raise RuntimeError("Gemini LLM did not return valid JSON. Unable to parse document.")

        logger.info("Successfully parsed document with Gemini LLM")
        return self._validate_and_clean(parsed_data)

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text that may contain markdown or other formatting"""
        try:
            # Try direct JSON parse first
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON in code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object directly
        json_pattern = r'\{[^{}]*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _validate_and_clean(self, data: Dict) -> Dict:
        """
        Validate and clean parsed data - enforces required fields from LLM

        Args:
            data: Parsed data dictionary

        Returns:
            Cleaned and validated data

        Raises:
            ValueError: If required fields are missing
        """
        # Ensure required fields exist
        required_fields = ['vendor', 'date', 'amount']
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"LLM failed to extract required fields: {', '.join(missing_fields)}")

        # Ensure numeric fields are numbers
        if isinstance(data.get('amount'), str):
            try:
                data['amount'] = float(data['amount'].replace(',', '').replace('$', ''))
            except ValueError:
                raise ValueError(f"Invalid amount value from LLM: {data.get('amount')}")

        if data.get('tax') is not None and isinstance(data.get('tax'), str):
            try:
                data['tax'] = float(data['tax'].replace(',', '').replace('$', ''))
            except ValueError:
                raise ValueError(f"Invalid tax value from LLM: {data.get('tax')}")
        elif data.get('tax') is None:
            data['tax'] = 0.0

        # Validate optional fields - LLM should provide these
        if 'category' not in data or not data['category']:
            raise ValueError("LLM must provide a category for the expense")

        if 'invoice_number' not in data or not data['invoice_number']:
            raise ValueError("LLM must provide an invoice number or identifier")

        return data


# Global parser instance
llm_parser = None


def get_llm_parser() -> LLMParser:
    """Get global LLM parser instance"""
    global llm_parser
    if llm_parser is None:
        llm_parser = LLMParser()
    return llm_parser


def parse_document(text: str) -> Dict:
    """
    Parse document text into structured data

    Args:
        text: Document text

    Returns:
        Structured data dictionary
    """
    parser = get_llm_parser()
    result = parser.parse_document(text)
    return result if result else {}
