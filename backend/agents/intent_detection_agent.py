"""
Intent Detection Agent - Maps Natural Language to API Endpoints
Uses LLM + RAG + Semantic Search to determine which API endpoint to call
"""

from typing import Dict, List, Optional, Any
import json

from backend.agents.api_registry import get_api_registry, EndpointSchema
from backend.utils.ollama_client import ollama_client
from backend.utils.logger import logger


class IntentDetectionAgent:
    """
    Detects user intent and maps it to the appropriate API endpoint
    Uses multiple strategies: semantic search, LLM classification, keyword matching
    """

    def __init__(self):
        """Initialize intent detection agent"""
        self.api_registry = get_api_registry()
        self.ollama = ollama_client

    def is_conversational(self, user_message: str) -> bool:
        """
        Determine if message is casual conversation vs action request

        Returns:
            True if conversational (no API call needed)
            False if action request (should call API)
        """
        message_lower = user_message.lower().strip()

        # Casual greetings and conversation
        conversational_patterns = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "whats up", "wassup",
            "who are you", "what are you", "what can you do",
            "help", "thanks", "thank you", "bye", "goodbye",
            "nice to meet you", "pleased to meet you"
        ]

        # If message is very short and matches conversational pattern
        if len(message_lower.split()) <= 5:
            for pattern in conversational_patterns:
                if pattern in message_lower:
                    return True

        # Action keywords that indicate API call needed
        action_keywords = [
            "add", "create", "update", "delete", "remove", "set", "change",
            "show", "get", "fetch", "find", "search", "list",
            "generate", "send", "upload", "submit", "save",
            "calculate", "analyze", "check", "view", "see",
            "spend", "spent", "budget", "goal", "receipt", "transaction",
            "subscription", "report", "alert", "notification"
        ]

        # If message contains action keywords, it's not conversational
        for keyword in action_keywords:
            if keyword in message_lower:
                return False

        # Default: if short message without action words, treat as conversational
        if len(message_lower.split()) <= 10:
            return True

        return False

    def generate_conversational_response(self, user_message: str) -> str:
        """
        Generate friendly conversational response using LLM

        Args:
            user_message: User's conversational message

        Returns:
            Natural language response
        """
        try:
            prompt = f"""You are a friendly financial assistant chatbot for Project Lumen.

User said: "{user_message}"

Respond in a warm, helpful way. If they're greeting you, greet them back and mention you can help with:
- Tracking expenses and receipts
- Setting financial goals
- Analyzing spending patterns
- Generating financial reports
- Managing subscriptions
- And much more!

If they ask what you can do, give examples like:
- "I spent $50 at Starbucks"
- "Create a goal to save $10000"
- "Show my spending dashboard"
- "Generate a weekly report"

Keep your response concise (2-3 sentences max).

Response:"""

            response = self.ollama.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=150
            )

            return response.strip()

        except Exception as e:
            logger.error(f"Error generating conversational response: {e}")
            # Fallback responses
            message_lower = user_message.lower()
            if any(word in message_lower for word in ["hi", "hello", "hey"]):
                return "Hello! I'm your financial assistant. I can help you track expenses, set goals, analyze spending, and more. What would you like to do?"
            elif "what can you do" in message_lower or "help" in message_lower:
                return "I can help you with:\n• Track receipts and expenses\n• Set and monitor financial goals\n• Analyze your spending patterns\n• Generate financial reports\n• Manage subscriptions\n\nJust tell me what you'd like to do in plain English!"
            else:
                return "I'm here to help with your finances! You can ask me to track expenses, create goals, analyze spending, or generate reports. What would you like to do?"

    def detect_intent(
        self,
        user_message: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect user intent and return matching endpoint

        Args:
            user_message: User's natural language input
            user_context: Optional context (user_id, previous messages, etc.)

        Returns:
            Dict with: endpoint, method, confidence, reasoning, alternatives
        """
        logger.info(f"Detecting intent for message: '{user_message[:100]}...'")

        # Step 1: Semantic search for candidate endpoints
        candidates = self.api_registry.search_endpoints(user_message, top_k=5)

        if not candidates:
            return {
                "success": False,
                "error": "No matching endpoints found",
                "confidence": 0.0
            }

        # Step 2: Use LLM to refine selection and determine HTTP method
        best_match = self._llm_refine_selection(user_message, candidates, user_context)

        # Step 3: Validate and return
        if best_match:
            logger.info(f"Intent detected: {best_match['method']} {best_match['endpoint']['path']} (confidence: {best_match['confidence']:.2f})")
            return {
                "success": True,
                **best_match,
                "alternatives": candidates[1:3] if len(candidates) > 1 else []
            }
        else:
            # Return top semantic search result as fallback
            return {
                "success": True,
                **candidates[0],
                "alternatives": candidates[1:3] if len(candidates) > 1 else []
            }

    def _llm_refine_selection(
        self,
        user_message: str,
        candidates: List[Dict],
        user_context: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Use LLM to refine endpoint selection"""
        try:
            # Build prompt for LLM
            prompt = self._build_classification_prompt(user_message, candidates, user_context)

            # Get LLM response
            response = self.ollama.generate(
                prompt=prompt,
                temperature=0.1,
                max_tokens=500
            )

            # Parse LLM response
            result = self._parse_llm_response(response, candidates)
            return result

        except Exception as e:
            logger.error(f"Error in LLM refinement: {e}")
            # Fallback to top semantic search result
            return candidates[0] if candidates else None

    def _build_classification_prompt(
        self,
        user_message: str,
        candidates: List[Dict],
        user_context: Optional[Dict] = None
    ) -> str:
        """Build prompt for LLM classification"""

        # Format candidates
        candidates_text = ""
        for i, candidate in enumerate(candidates, 1):
            endpoint = candidate["endpoint"]
            candidates_text += f"""
{i}. {endpoint['method']} {endpoint['path']}
   Description: {endpoint['summary']}
   Examples: {', '.join(endpoint['examples'][:3])}
   Category: {endpoint['category']}
"""

        # Add context if available
        context_text = ""
        if user_context:
            context_text = f"\nUser Context: {json.dumps(user_context, indent=2)}"

        prompt = f"""You are an API routing assistant. Your job is to determine which API endpoint the user wants to call based on their message.

User Message: "{user_message}"
{context_text}

Candidate Endpoints:
{candidates_text}

Analyze the user's message and determine:
1. Which endpoint best matches their intent
2. The confidence level (0.0 to 1.0)
3. Brief reasoning for your choice

Consider:
- Exact keyword matches in the message
- The user's likely intent (create, read, update, delete, analyze)
- Common phrasing patterns
- Context from previous interactions

Respond in EXACTLY this JSON format:
{{
  "selected_index": <1-5>,
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>",
  "detected_action": "<create|read|update|delete|analyze>"
}}

IMPORTANT: Return ONLY the JSON object, no other text.
"""

        return prompt

    def _parse_llm_response(
        self,
        llm_response: str,
        candidates: List[Dict]
    ) -> Optional[Dict]:
        """Parse LLM response and return selected endpoint"""
        try:
            # Extract JSON from response
            llm_response = llm_response.strip()

            # Try to find JSON in response
            start_idx = llm_response.find('{')
            end_idx = llm_response.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON found in LLM response")
                return None

            json_str = llm_response[start_idx:end_idx]
            result = json.loads(json_str)

            # Get selected candidate
            selected_index = result.get("selected_index", 1)
            if selected_index < 1 or selected_index > len(candidates):
                logger.warning(f"Invalid selected_index: {selected_index}")
                return None

            selected_candidate = candidates[selected_index - 1]

            # Update confidence and reasoning
            return {
                "endpoint": selected_candidate["endpoint"],
                "confidence": result.get("confidence", selected_candidate["confidence"]),
                "reasoning": result.get("reasoning", selected_candidate["reasoning"]),
                "method": selected_candidate["endpoint"]["method"],
                "detected_action": result.get("detected_action", "unknown")
            }

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM JSON response: {e}")
            logger.debug(f"LLM response was: {llm_response}")
            return None
        except Exception as e:
            logger.error(f"Error in parse_llm_response: {e}")
            return None

    def detect_http_method(self, user_message: str, endpoint_path: str) -> str:
        """
        Detect HTTP method from user message

        Args:
            user_message: User's message
            endpoint_path: API endpoint path

        Returns:
            HTTP method (GET, POST, PUT, DELETE)
        """
        message_lower = user_message.lower()

        # Create/Add keywords -> POST
        create_keywords = ["add", "create", "new", "make", "upload", "send", "parse", "generate", "schedule"]
        if any(keyword in message_lower for keyword in create_keywords):
            return "POST"

        # Update/Change keywords -> PUT
        update_keywords = ["update", "change", "edit", "modify", "set"]
        if any(keyword in message_lower for keyword in update_keywords):
            return "PUT"

        # Delete/Remove keywords -> DELETE
        delete_keywords = ["delete", "remove", "cancel", "unsubscribe"]
        if any(keyword in message_lower for keyword in delete_keywords):
            return "DELETE"

        # Default to GET for queries
        return "GET"

    def categorize_intent(self, user_message: str) -> str:
        """
        Categorize high-level user intent

        Returns:
            Category: receipt, goal, report, spending, profile, etc.
        """
        message_lower = user_message.lower()

        # Receipt-related
        if any(word in message_lower for word in ["spent", "receipt", "upload", "bought", "purchased"]):
            return "receipt"

        # Goal-related
        if any(word in message_lower for word in ["goal", "save for", "target", "saving"]):
            return "goal"

        # Report-related
        if any(word in message_lower for word in ["report", "summary", "email me"]):
            return "report"

        # Spending analysis
        if any(word in message_lower for word in ["spent", "spending", "expenses", "budget", "dashboard"]):
            return "spending"

        # Profile
        if any(word in message_lower for word in ["profile", "account", "salary", "income"]):
            return "profile"

        # Subscription
        if any(word in message_lower for word in ["subscription", "recurring", "cancel"]):
            return "subscription"

        # Family
        if any(word in message_lower for word in ["family", "household", "shared"]):
            return "family"

        # Gamification
        if any(word in message_lower for word in ["points", "level", "badge", "leaderboard"]):
            return "gamification"

        return "general"


# Global instance
_intent_detection_agent = None


def get_intent_detection_agent() -> IntentDetectionAgent:
    """Get global intent detection agent instance"""
    global _intent_detection_agent
    if _intent_detection_agent is None:
        _intent_detection_agent = IntentDetectionAgent()
    return _intent_detection_agent
