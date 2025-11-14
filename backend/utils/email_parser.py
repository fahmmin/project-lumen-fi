"""
Email Receipt Parser - Extract receipts from emails using Ollama LLM
"""

from typing import Dict, List, Optional
import re
import json
from datetime import datetime
from backend.utils.logger import logger
from backend.config import settings
from backend.utils.ollama_client import ollama_client


class EmailReceiptParser:
    """Parses receipt information from email text using Ollama LLM"""

    def __init__(self):
        self.provider = "ollama"
        logger.info("EmailReceiptParser initialized with Ollama LLM")

        # Fallback regex patterns (used if Ollama is unavailable)
        self.vendor_patterns = [
            r'From:\s*([A-Z][a-zA-Z\s&]+)(?:\s*<|$)',
            r'Thank you for (?:shopping at|ordering from)\s+([A-Z][a-zA-Z\s&]+)',
            r'Your (?:order|purchase) from\s+([A-Z][a-zA-Z\s&]+)',
            r'([A-Z][a-zA-Z]+)\s+(?:Order|Receipt|Invoice)',
            r'(?:swiggy|zomato|bigbasket|flipkart|amazon)',  # Common Indian vendors
        ]

        self.amount_patterns = [
            r'Total:?\s*[₹$]?(\d+\.?\d{0,2})',
            r'Amount:?\s*[₹$]?(\d+\.?\d{0,2})',
            r'Charged:?\s*[₹$]?(\d+\.?\d{0,2})',
            r'Order Total:?\s*[₹$]?(\d+\.?\d{0,2})',
            r'Grand Total:?\s*[₹$]?(\d+\.?\d{0,2})',
        ]

        self.date_patterns = [
            r'Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\w+ \d{1,2}, \d{4})',  # "December 10, 2024"
        ]

    def parse_email(self, email_text: str, subject: str = "") -> Dict:
        """Parse receipt information from email text using Ollama LLM"""
        try:
            # Try Ollama LLM parsing first
            logger.info("Parsing email with Ollama LLM")
            llm_result = self._parse_with_ollama(email_text, subject)

            if llm_result and llm_result.get("confidence", 0) > 0.5:
                logger.info(f"Ollama parsing successful: {llm_result.get('vendor', 'unknown')} - ${llm_result.get('amount', 0)}")
                return llm_result
            else:
                logger.warning("Ollama parsing failed or low confidence, falling back to regex")
                return self._parse_with_regex(email_text)

        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            # Fallback to regex on any error
            return self._parse_with_regex(email_text)

    def _parse_with_ollama(self, email_text: str, subject: str) -> Optional[Dict]:
        """Parse email using Ollama LLM"""
        try:
            # Create prompt for LLM
            prompt = f"""Extract receipt information from this email. Return ONLY valid JSON.

IMPORTANT INSTRUCTIONS:
- Extract the TOTAL amount as a number (no currency symbols)
- If amount is written as "Rs450" or "₹450", extract as 450.0 (not 4.5 or 450)
- If amount has comma like "Rs1,250", extract as 1250.0
- Date format must be YYYY-MM-DD
- Common Indian vendors: Zomato, Swiggy, BigBasket, Flipkart, Amazon, Paytm

Return JSON in this EXACT format:
{{
  "vendor": "vendor name",
  "amount": 450.0,
  "date": "2024-12-10",
  "category": "dining",
  "items": ["item1", "item2"],
  "confidence": 0.95
}}

Email Subject: {subject}

Email Body:
{email_text}

Return ONLY the JSON object, no additional text or explanation."""

            response = ollama_client.generate(
                prompt=prompt,
                system_message="You are a financial receipt extraction expert specializing in Indian vendors and currency formats (₹, Rs). Extract exact amounts without misinterpreting numbers. Always return valid JSON only.",
                temperature=0.1,
                max_tokens=500
            )

            # Extract JSON from response
            extracted = ollama_client.parse_json_response(response)

            if extracted:
                extracted["method"] = "ollama"
                return extracted

            return None

        except Exception as e:
            logger.error(f"Ollama parsing error: {str(e)}")
            return None

    def _parse_with_regex(self, email_text: str) -> Dict:
        """Fallback regex extraction"""
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
        for pattern in self.vendor_patterns:
            match = re.search(pattern, email_text, re.IGNORECASE)
            if match:
                extracted["vendor"] = match.group(1) if match.lastindex >= 1 else match.group(0)
                extracted["vendor"] = extracted["vendor"].strip()
                extracted["confidence"] += 0.2
                break

        # Extract amount
        for pattern in self.amount_patterns:
            match = re.search(pattern, email_text, re.IGNORECASE)
            if match:
                try:
                    extracted["amount"] = float(match.group(1))
                    extracted["confidence"] += 0.3
                    break
                except:
                    pass

        # Extract date
        for pattern in self.date_patterns:
            match = re.search(pattern, email_text)
            if match:
                extracted["date"] = datetime.now().isoformat()
                extracted["confidence"] += 0.1
                break

        # Simple category inference
        text_lower = email_text.lower()
        if any(word in text_lower for word in ['zomato', 'swiggy', 'restaurant', 'food']):
            extracted["category"] = "dining"
            extracted["confidence"] += 0.1
        elif any(word in text_lower for word in ['bigbasket', 'grocery', 'vegetables']):
            extracted["category"] = "groceries"
            extracted["confidence"] += 0.1
        elif any(word in text_lower for word in ['amazon', 'flipkart', 'shopping']):
            extracted["category"] = "shopping"
            extracted["confidence"] += 0.1

        return extracted


# Global parser instance
email_parser = EmailReceiptParser()
