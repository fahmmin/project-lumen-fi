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
        Parse document text into structured JSON

        Args:
            text: Extracted document text

        Returns:
            Structured document data or None if parsing fails
        """
        try:
            if settings.LLM_PROVIDER == "openai":
                return self._parse_openai(text)
            elif settings.LLM_PROVIDER == "gemini":
                return self._parse_gemini(text)
            else:
                logger.warning("No LLM configured, using rule-based fallback")
                return self._parse_fallback(text)

        except Exception as e:
            log_error(e, "Document parsing")
            return self._parse_fallback(text)

    def _parse_openai(self, text: str) -> Optional[Dict]:
        """Parse using OpenAI API"""
        try:
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

            if parsed_data:
                logger.info("Successfully parsed document with LLM")
                return self._validate_and_clean(parsed_data)
            else:
                logger.warning("LLM did not return valid JSON")
                return self._parse_fallback(text)

        except Exception as e:
            log_error(e, "OpenAI parsing")
            return self._parse_fallback(text)

    def _parse_gemini(self, text: str) -> Optional[Dict]:
        """Parse using Google Gemini API"""
        try:
            if not HAS_GEMINI:
                logger.warning("Gemini SDK not installed, using fallback")
                return self._parse_fallback(text)

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

            if parsed_data:
                logger.info("Successfully parsed document with Gemini")
                return self._validate_and_clean(parsed_data)
            else:
                logger.warning("Gemini did not return valid JSON")
                return self._parse_fallback(text)

        except Exception as e:
            log_error(e, "Gemini parsing")
            return self._parse_fallback(text)

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

    def _parse_fallback(self, text: str) -> Dict:
        """
        Fallback rule-based parsing

        Args:
            text: Document text

        Returns:
            Extracted data (best effort)
        """
        logger.info("Using rule-based fallback parser")

        data = {
            "vendor": self._extract_vendor(text),
            "date": self._extract_date(text),
            "amount": self._extract_amount(text),
            "tax": self._extract_tax(text),
            "category": "Uncategorized",
            "invoice_number": self._extract_invoice_number(text)
        }

        return data

    def _extract_vendor(self, text: str) -> str:
        """Extract vendor name (first line heuristic)"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 3 and not line.isdigit():
                return line
        return "Unknown Vendor"

    def _extract_date(self, text: str) -> str:
        """Extract date using regex"""
        # Common date patterns
        patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',  # YYYY-MM-DD
            r'\b(\d{2}/\d{2}/\d{4})\b',  # MM/DD/YYYY
            r'\b(\d{2}-\d{2}-\d{4})\b',  # DD-MM-YYYY
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                # Convert to YYYY-MM-DD format
                if '/' in date_str:
                    parts = date_str.split('/')
                    if len(parts[2]) == 4:
                        return f"{parts[2]}-{parts[0]}-{parts[1]}"
                return date_str

        return "Unknown"

    def _extract_amount(self, text: str) -> float:
        """Extract total amount"""
        # Look for "total" followed by amount
        patterns = [
            r'total[:\s]*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'amount[:\s]*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]

        amounts = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1).replace(',', '')
                try:
                    amounts.append(float(amount_str))
                except ValueError:
                    pass

        return max(amounts) if amounts else 0.0

    def _extract_tax(self, text: str) -> float:
        """Extract tax amount"""
        patterns = [
            r'tax[:\s]*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'vat[:\s]*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'gst[:\s]*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                tax_str = match.group(1).replace(',', '')
                try:
                    return float(tax_str)
                except ValueError:
                    pass

        return 0.0

    def _extract_invoice_number(self, text: str) -> str:
        """Extract invoice/receipt number"""
        patterns = [
            r'invoice\s*#?\s*[:\-]?\s*([A-Z0-9\-]+)',
            r'receipt\s*#?\s*[:\-]?\s*([A-Z0-9\-]+)',
            r'ref\s*#?\s*[:\-]?\s*([A-Z0-9\-]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return "N/A"

    def _validate_and_clean(self, data: Dict) -> Dict:
        """
        Validate and clean parsed data

        Args:
            data: Parsed data dictionary

        Returns:
            Cleaned and validated data
        """
        # Ensure required fields exist
        required_fields = ['vendor', 'date', 'amount']
        for field in required_fields:
            if field not in data or data[field] is None:
                data[field] = "Unknown" if field != 'amount' else 0.0

        # Ensure numeric fields are numbers
        if isinstance(data.get('amount'), str):
            try:
                data['amount'] = float(data['amount'].replace(',', '').replace('$', ''))
            except ValueError:
                data['amount'] = 0.0

        if isinstance(data.get('tax'), str):
            try:
                data['tax'] = float(data['tax'].replace(',', '').replace('$', ''))
            except ValueError:
                data['tax'] = 0.0

        # Default optional fields
        if 'category' not in data:
            data['category'] = "Uncategorized"

        if 'invoice_number' not in data:
            data['invoice_number'] = "N/A"

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
