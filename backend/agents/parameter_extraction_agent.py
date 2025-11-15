"""
Parameter Extraction Agent - Extracts API Parameters from Natural Language
Uses LLM to intelligently extract and format parameters based on endpoint schema
"""

from typing import Dict, List, Optional, Any
import json
import re
from datetime import datetime, date, timedelta
from dateutil import parser as date_parser

from backend.agents.api_registry import EndpointSchema
from backend.utils.ollama_client import ollama_client
from backend.utils.logger import logger


class ParameterExtractionAgent:
    """
    Extracts API parameters from natural language using LLM
    Validates against endpoint schema and handles type conversion
    """

    def __init__(self):
        """Initialize parameter extraction agent"""
        self.ollama = ollama_client

    def extract_parameters(
        self,
        user_message: str,
        endpoint: EndpointSchema,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract parameters from user message for a specific endpoint

        Args:
            user_message: User's natural language input
            endpoint: Target API endpoint schema
            user_context: User context (user_id, etc.)

        Returns:
            Dict with:
              - success: bool
              - parameters: Dict of extracted params
              - missing_required: List of missing required params
              - follow_up_question: Optional question to ask user
        """
        logger.info(f"Extracting parameters for {endpoint.method} {endpoint.path}")

        # Step 1: Try pattern-based extraction first (faster)
        pattern_params = self._pattern_extraction(user_message, endpoint)

        # Step 2: Use LLM for intelligent extraction
        llm_params = self._llm_extraction(user_message, endpoint, user_context)

        # Step 3: Merge results (LLM takes precedence)
        extracted_params = {**pattern_params, **llm_params}

        # Step 4: Add context parameters (user_id, etc.)
        if user_context:
            extracted_params = self._add_context_parameters(
                extracted_params,
                endpoint,
                user_context
            )

        # Step 5: Validate against schema
        validation_result = self._validate_parameters(extracted_params, endpoint)

        # Step 6: Determine if we need to ask follow-up questions
        follow_up = None
        if validation_result["missing_required"]:
            follow_up = self._generate_follow_up_question(
                validation_result["missing_required"],
                endpoint
            )

        return {
            "success": len(validation_result["missing_required"]) == 0,
            "parameters": extracted_params,
            "missing_required": validation_result["missing_required"],
            "follow_up_question": follow_up,
            "validation_errors": validation_result.get("errors", [])
        }

    def _pattern_extraction(
        self,
        user_message: str,
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Extract parameters using regex patterns"""
        params = {}

        # Extract amounts (money)
        amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', user_message)
        if amount_match and "amount" in endpoint.parameters:
            amount_str = amount_match.group(1).replace(',', '')
            params["amount"] = float(amount_str)

        # Extract dates
        date_patterns = [
            (r'yesterday', lambda: (date.today() - timedelta(days=1)).isoformat()),
            (r'today', lambda: date.today().isoformat()),
            (r'tomorrow', lambda: (date.today() + timedelta(days=1)).isoformat()),
        ]

        for pattern, date_func in date_patterns:
            if re.search(pattern, user_message, re.IGNORECASE):
                if "date" in endpoint.parameters:
                    params["date"] = date_func()
                if "target_date" in endpoint.parameters:
                    params["target_date"] = date_func()
                break

        # Extract email addresses
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_message)
        if email_match and "email" in endpoint.parameters:
            params["email"] = email_match.group(0)

        # Extract report types
        report_types = ["weekly", "monthly", "quarterly", "yearly"]
        for report_type in report_types:
            if report_type in user_message.lower() and "report_type" in endpoint.parameters:
                params["report_type"] = report_type
                break

        # Extract goal priority
        priorities = ["low", "medium", "high", "critical"]
        for priority in priorities:
            if priority in user_message.lower() and "priority" in endpoint.parameters:
                params["priority"] = priority
                break

        return params

    def _llm_extraction(
        self,
        user_message: str,
        endpoint: EndpointSchema,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Use LLM to extract parameters"""
        try:
            prompt = self._build_extraction_prompt(user_message, endpoint, user_context)

            response = self.ollama.generate(
                prompt=prompt,
                temperature=0.1,
                max_tokens=500
            )

            # Parse LLM response
            params = self._parse_extraction_response(response)
            return params

        except Exception as e:
            logger.error(f"Error in LLM extraction: {e}")
            return {}

    def _build_extraction_prompt(
        self,
        user_message: str,
        endpoint: EndpointSchema,
        user_context: Optional[Dict] = None
    ) -> str:
        """Build prompt for LLM parameter extraction"""

        # Build parameter schema description
        param_descriptions = []
        for param_name, param_info in endpoint.parameters.items():
            required = "REQUIRED" if param_info.get("required", False) else "OPTIONAL"
            param_type = param_info.get("type", "string")
            location = param_info.get("location", "unknown")

            param_descriptions.append(
                f"- {param_name} ({param_type}, {required}, {location})"
            )

        params_text = "\n".join(param_descriptions) if param_descriptions else "No parameters required"

        # Add context
        context_text = ""
        if user_context:
            context_text = f"\nAvailable Context:\n{json.dumps(user_context, indent=2)}"

        prompt = f"""Extract API parameters from the user's message.

User Message: "{user_message}"

API Endpoint: {endpoint.method} {endpoint.path}
Description: {endpoint.summary}

Required Parameters:
{params_text}
{context_text}

Extract the following from the user's message:
1. Explicit values mentioned (amounts, dates, names, etc.)
2. Implicit information (e.g., "yesterday" = specific date)
3. Inferred values based on context

Special Instructions:
- For dates: Convert "yesterday", "today", "tomorrow", "next week" to ISO format (YYYY-MM-DD)
- For amounts: Extract numeric values and remove currency symbols
- For emails: Extract valid email addresses
- For names/descriptions: Extract quoted text or key phrases
- Use context values when not explicitly mentioned in message

Return ONLY a JSON object with the extracted parameters:
{{
  "parameter_name": "value",
  ...
}}

If a parameter cannot be determined, omit it from the JSON.
Return empty JSON object if no parameters can be extracted.

IMPORTANT: Return ONLY the JSON object, no explanations.
"""

        return prompt

    def _parse_extraction_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM extraction response"""
        try:
            # Clean response
            llm_response = llm_response.strip()

            # Find JSON in response
            start_idx = llm_response.find('{')
            end_idx = llm_response.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                return {}

            json_str = llm_response[start_idx:end_idx]
            params = json.loads(json_str)

            # Convert types
            params = self._convert_param_types(params)

            return params

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing extraction JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error in parse_extraction_response: {e}")
            return {}

    def _convert_param_types(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert parameter types to correct formats"""
        converted = {}

        for key, value in params.items():
            if value is None:
                continue

            # Convert string numbers to float/int
            if isinstance(value, str):
                # Try to parse as number
                try:
                    if '.' in value:
                        converted[key] = float(value)
                    else:
                        # Try int first
                        try:
                            converted[key] = int(value)
                        except:
                            # Keep as float if int fails
                            converted[key] = float(value)
                    continue
                except ValueError:
                    pass

            converted[key] = value

        return converted

    def _add_context_parameters(
        self,
        extracted_params: Dict[str, Any],
        endpoint: EndpointSchema,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add parameters from user context"""
        params = extracted_params.copy()

        # Add user_id if required and not present
        if "user_id" in endpoint.parameters and "user_id" not in params:
            if "user_id" in user_context:
                params["user_id"] = user_context["user_id"]

        # Add email from context if needed
        if "email" in endpoint.parameters and "email" not in params:
            if "email" in user_context:
                params["email"] = user_context["email"]

        return params

    def _validate_parameters(
        self,
        params: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Validate extracted parameters against schema"""
        missing_required = []
        errors = []

        for param_name, param_info in endpoint.parameters.items():
            required = param_info.get("required", False)

            if required and param_name not in params:
                missing_required.append(param_name)

        return {
            "missing_required": missing_required,
            "errors": errors
        }

    def _generate_follow_up_question(
        self,
        missing_params: List[str],
        endpoint: EndpointSchema
    ) -> str:
        """Generate follow-up question for missing parameters"""
        if not missing_params:
            return None

        # Get info about first missing parameter
        param_name = missing_params[0]
        param_info = endpoint.parameters.get(param_name, {})

        # Generate friendly question
        questions = {
            "user_id": "I need your user ID to proceed. What is your user ID?",
            "email": "What email address should I use?",
            "amount": "How much is the amount?",
            "target_amount": "What's your target amount?",
            "date": "What date was this?",
            "target_date": "By when would you like to achieve this goal?",
            "name": "What would you like to call this?",
            "goal_name": "What's the name of your goal?",
            "vendor": "Which vendor or store was this from?",
            "category": "What category does this belong to?",
            "report_type": "What type of report would you like? (weekly, monthly, quarterly, yearly)",
            "period": "What time period? (month, quarter, year)",
        }

        question = questions.get(param_name, f"What is the {param_name.replace('_', ' ')}?")

        # If multiple missing, add note
        if len(missing_params) > 1:
            question += f" (I'll also need: {', '.join(missing_params[1:])})"

        return question

    def merge_with_follow_up(
        self,
        previous_params: Dict[str, Any],
        follow_up_message: str,
        missing_param: str
    ) -> Dict[str, Any]:
        """Merge parameters from follow-up response"""
        params = previous_params.copy()

        # Try to extract the missing parameter from follow-up
        value = self._extract_single_parameter(follow_up_message, missing_param)
        if value is not None:
            params[missing_param] = value

        return params

    def _extract_single_parameter(self, message: str, param_name: str) -> Any:
        """Extract a single parameter value from message"""
        message = message.strip()

        # Amount/numeric
        if "amount" in param_name or "salary" in param_name or "target" in param_name:
            match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{2})?)', message)
            if match:
                return float(match.group(1).replace(',', ''))

        # Email
        if "email" in param_name:
            match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
            if match:
                return match.group(0)

        # Date
        if "date" in param_name:
            try:
                parsed_date = date_parser.parse(message, fuzzy=True)
                return parsed_date.date().isoformat()
            except:
                pass

        # Default: return the message as is (cleaned)
        return message.strip()


# Global instance
_parameter_extraction_agent = None


def get_parameter_extraction_agent() -> ParameterExtractionAgent:
    """Get global parameter extraction agent instance"""
    global _parameter_extraction_agent
    if _parameter_extraction_agent is None:
        _parameter_extraction_agent = ParameterExtractionAgent()
    return _parameter_extraction_agent
