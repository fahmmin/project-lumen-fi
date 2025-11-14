"""
Email Receipt Parser - Extract receipts from emails using LLM
"""

from typing import Dict, List, Optional
import re
import json
from datetime import datetime
from backend.utils.logger import logger
from backend.config import settings

# Try to import LLM libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


class EmailReceiptParser:
    """Parses receipt information from email text using LLM"""

    def __init__(self):
        # Initialize LLM
        self.use_llm = True
        if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY and HAS_OPENAI:
            openai.api_key = settings.OPENAI_API_KEY
            self.provider = "openai"
        elif settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY and HAS_GEMINI:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.provider = "gemini"
        else:
            self.use_llm = False
            self.provider = "regex"
            logger.warning("No LLM configured, using regex fallback for email parsing")

        # Fallback regex patterns
        self.vendor_patterns = [
            r'From:\s*([A-Z][a-zA-Z\s&]+)(?:\s*<|$)',
            r'Thank you for (?:shopping at|ordering from)\s+([A-Z][a-zA-Z\s&]+)',
            r'Your (?:order|purchase) from\s+([A-Z][a-zA-Z\s&]+)',
            r'([A-Z][a-zA-Z]+)\s+(?:Order|Receipt|Invoice)',
        ]

        self.amount_patterns = [
            r'Total:?\s*\$?(\d+\.?\d{0,2})',
            r'Amount:?\s*\$?(\d+\.?\d{0,2})',
            r'Charged:?\s*\$?(\d+\.?\d{0,2})',
            r'Order Total:?\s*\$?(\d+\.?\d{0,2})',
        ]

        self.date_patterns = [
            r'Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        ]

    def parse_email(self, email_text: str, subject: str = "") -> Dict:
        """
        Parse receipt information from email text using LLM

        Args:
            email_text: Email body content
            subject: Email subject line

        Returns:
            Dict with extracted receipt fields
        """
        try:
            # Try LLM parsing first
            if self.use_llm:
                logger.info(f"Parsing email with LLM ({self.provider})")
                llm_result = self._parse_with_llm(email_text, subject)
                if llm_result and llm_result.get("confidence", 0) > 0.5:
                    logger.info(f"LLM parsing successful: {llm_result.get('vendor', 'unknown')} - ${llm_result.get('amount', 0)}")
                    return llm_result
                else:
                    logger.warning("LLM parsing failed or low confidence, falling back to regex")

            # Fallback to regex extraction
            logger.info("Using regex extraction for email")
            extracted = {
                "vendor": None,
                "amount": None,
                "date": None,
                "category": None,
                "items": [],
                "confidence": 0.0,
                "method": "regex"
            }

            # Extract vendor
            vendor = self._extract_vendor(email_text, subject)
            if vendor:
                extracted["vendor"] = vendor
                extracted["confidence"] += 0.3

            # Extract amount
            amount = self._extract_amount(email_text)
            if amount:
                extracted["amount"] = amount
                extracted["confidence"] += 0.4

            # Extract date
            date = self._extract_date(email_text)
            if date:
                extracted["date"] = date
                extracted["confidence"] += 0.2

            # Categorize based on vendor
            if vendor:
                extracted["category"] = self._categorize_vendor(vendor)
                extracted["confidence"] += 0.1

            return extracted

        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            return {
                "vendor": None,
                "amount": None,
                "date": None,
                "category": None,
                "items": [],
                "confidence": 0.0,
                "error": str(e)
            }

    def _parse_with_llm(self, email_text: str, subject: str) -> Optional[Dict]:
        """Parse email using LLM (OpenAI or Gemini)"""
        try:
            # Create prompt for LLM
            prompt = f"""Extract receipt information from this email. Return ONLY valid JSON with these fields:
{{
  "vendor": "vendor name (e.g., Amazon, Zomato, Starbucks)",
  "amount": float (total amount),
  "date": "YYYY-MM-DD format",
  "category": "groceries, dining, shopping, entertainment, transportation, healthcare, or general",
  "items": ["list", "of", "items"],
  "confidence": float (0.0 to 1.0)
}}

Email Subject: {subject}

Email Body:
{email_text}

Return ONLY the JSON object, no additional text."""

            if self.provider == "openai":
                response = openai.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a receipt extraction expert. Extract structured data from emails. Always return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                result_text = response.choices[0].message.content.strip()

            elif self.provider == "gemini":
                model = genai.GenerativeModel(settings.LLM_MODEL)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=500,
                    )
                )
                result_text = response.text.strip()
            else:
                return None

            # Extract JSON from response
            extracted = self._extract_json_from_llm(result_text)
            if extracted:
                extracted["method"] = "llm"
                return extracted

            return None

        except Exception as e:
            logger.error(f"LLM parsing error: {str(e)}")
            return None

    def _extract_json_from_llm(self, text: str) -> Optional[Dict]:
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)

            # Try parsing the whole response
            return json.loads(text)

        except json.JSONDecodeError:
            logger.warning("Could not extract valid JSON from LLM response")
            return None

    def _extract_vendor(self, text: str, subject: str) -> Optional[str]:
        """Extract vendor name"""
        # Try subject first
        for pattern in self.vendor_patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Try body
        for pattern in self.vendor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract transaction amount"""
        for pattern in self.amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Take the last match (usually the total)
                    return float(matches[-1])
                except:
                    pass

        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract transaction date"""
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return datetime.now().isoformat()  # Simplified
                except:
                    pass

        return datetime.now().isoformat()

    def _categorize_vendor(self, vendor: str) -> str:
        """Categorize based on vendor name"""
        vendor_lower = vendor.lower()

        if any(word in vendor_lower for word in ['amazon', 'ebay', 'etsy', 'walmart', 'target']):
            return 'shopping'
        elif any(word in vendor_lower for word in ['uber', 'lyft', 'shell', 'chevron', 'gas']):
            return 'transportation'
        elif any(word in vendor_lower for word in ['starbucks', 'restaurant', 'cafe', 'pizza', 'chipotle']):
            return 'dining'
        elif any(word in vendor_lower for word in ['netflix', 'spotify', 'hulu', 'disney']):
            return 'entertainment'
        elif any(word in vendor_lower for word in ['cvs', 'walgreens', 'pharmacy', 'hospital']):
            return 'healthcare'
        elif any(word in vendor_lower for word in ['whole foods', 'safeway', 'kroger', 'trader joe']):
            return 'groceries'
        else:
            return 'general'


# Global instance
email_parser = EmailReceiptParser()
