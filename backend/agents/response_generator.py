"""
Response Generator - Converts API Responses to Natural Language
Shows REAL data from API calls, no dummy responses
"""

from typing import Dict, Any, List, Optional
import json

from backend.agents.api_registry import EndpointSchema
from backend.utils.logger import logger


class ResponseGenerator:
    """
    Generates natural language responses from REAL API results
    Extracts and displays actual data returned by endpoints
    """

    def __init__(self):
        """Initialize response generator"""
        pass

    def generate_response(
        self,
        endpoint: EndpointSchema,
        api_result: Dict[str, Any],
        user_message: str,
        show_api_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate natural language response from REAL API result

        Args:
            endpoint: Endpoint that was called
            api_result: REAL result from API call
            user_message: Original user message
            show_api_details: Whether to show which API was called

        Returns:
            Dict with: response (str), suggestions (list)
        """
        logger.info(f"Generating response for {endpoint.method} {endpoint.path}")
        logger.info(f"API success: {api_result.get('success', False)}")
        logger.info(f"API data keys: {list(api_result.get('data', {}).keys()) if isinstance(api_result.get('data'), dict) else type(api_result.get('data'))}")

        # Handle errors
        if not api_result.get("success", False):
            return self._generate_error_response(api_result, endpoint)

        # Get REAL data from API
        data = api_result.get("data", {})

        # Build response with API details
        response_parts = []

        # Show which API was called
        if show_api_details:
            api_info = f"🔵 Called API: {endpoint.method} {endpoint.path}"
            response_parts.append(api_info)

        # Convert REAL API data to readable format
        data_response = self._format_real_data(data, endpoint)
        response_parts.append(data_response)

        # Add completion message
        if show_api_details:
            response_parts.append("\n✅ Process completed successfully!")

        response = "\n".join(response_parts)

        # Generate suggestions based on endpoint category
        suggestions = self._get_suggestions(endpoint.category)

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _format_real_data(self, data: Any, endpoint: EndpointSchema) -> str:
        """Format REAL API data into readable text"""

        if not data:
            return "✅ Request completed successfully (no data returned)"

        # Handle different data types
        if isinstance(data, dict):
            return self._format_dict_data(data, endpoint)
        elif isinstance(data, list):
            return self._format_list_data(data, endpoint)
        else:
            return f"✅ Result: {data}"

    def _format_dict_data(self, data: Dict, endpoint: EndpointSchema) -> str:
        """Format dictionary data from REAL API response"""
        lines = []

        # Add success emoji
        lines.append("✅")

        # Look for main message/summary fields first
        if "message" in data:
            lines.append(data["message"])
            return " ".join(lines)

        if "detail" in data:
            lines.append(data["detail"])
            return " ".join(lines)

        # Extract ALL important fields from REAL data
        important_fields = []

        # Financial fields
        for key in ["total_spent", "total_spending", "total", "amount", "balance", "income", "savings"]:
            if key in data and data[key] is not None:
                value = data[key]
                if isinstance(value, (int, float)):
                    important_fields.append(f"{key.replace('_', ' ').title()}: ${value:,.2f}")
                else:
                    important_fields.append(f"{key.replace('_', ' ').title()}: {value}")

        # Count fields
        for key in ["count", "total_count", "total_goals", "total_subscriptions", "active_goals", "documents_indexed"]:
            if key in data and data[key] is not None:
                important_fields.append(f"{key.replace('_', ' ').title()}: {data[key]}")

        # Percentage fields
        for key in ["percentage_used", "progress_percentage", "percentile"]:
            if key in data and data[key] is not None:
                important_fields.append(f"{key.replace('_', ' ').title()}: {data[key]:.1f}%")

        # Score fields
        for key in ["score", "health_score", "level", "points"]:
            if key in data and data[key] is not None:
                important_fields.append(f"{key.replace('_', ' ').title()}: {data[key]}")

        # Status fields (for health checks, etc.)
        if "status" in data and isinstance(data["status"], str):
            important_fields.append(f"Status: {data['status']}")

        # Budget status
        if "budget_status" in data and isinstance(data["budget_status"], dict):
            budget = data["budget_status"]
            if "percentage_used" in budget:
                important_fields.append(f"Budget Used: {budget['percentage_used']:.1f}%")
            if "remaining" in budget:
                important_fields.append(f"Budget Remaining: ${budget['remaining']:,.2f}")

        # Spending by category
        if "spending_by_category" in data and isinstance(data["spending_by_category"], dict):
            categories = data["spending_by_category"]
            if categories:
                top_cat = max(categories.items(), key=lambda x: x[1])
                important_fields.append(f"Top Category: {top_cat[0]} (${top_cat[1]:,.2f})")

        # Components (for health checks)
        if "components" in data and isinstance(data["components"], dict):
            for comp_name, comp_data in data["components"].items():
                if isinstance(comp_data, dict) and "status" in comp_data:
                    important_fields.append(f"{comp_name.replace('_', ' ').title()}: {comp_data['status']}")
                    # Show additional component details
                    for k, v in comp_data.items():
                        if k != "status" and not isinstance(v, (dict, list)):
                            important_fields.append(f"  - {k.replace('_', ' ').title()}: {v}")

        # Goals
        if "goals" in data and isinstance(data["goals"], list):
            important_fields.append(f"Goals: {len(data['goals'])}")

        # Subscriptions
        if "subscriptions" in data and isinstance(data["subscriptions"], list):
            important_fields.append(f"Subscriptions: {len(data['subscriptions'])}")

        # Alerts
        if "alerts" in data and isinstance(data["alerts"], list):
            important_fields.append(f"Alerts: {len(data['alerts'])}")

        # Insights
        if "insights" in data and isinstance(data["insights"], list):
            for insight in data["insights"][:2]:  # First 2 insights
                important_fields.append(f"💡 {insight}")

        # If we found important fields, use them
        if important_fields:
            lines.extend(important_fields)
            return "\n".join(lines)

        # Otherwise show ALL non-empty fields (don't skip anything except None)
        for key, value in data.items():
            if value is None:
                continue

            if isinstance(value, bool):
                lines.append(f"{key.replace('_', ' ').title()}: {'Yes' if value else 'No'}")
            elif isinstance(value, (int, float)):
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
            elif isinstance(value, str):
                # Show all string values, truncate if very long
                display_value = value if len(value) <= 200 else value[:200] + "..."
                lines.append(f"{key.replace('_', ' ').title()}: {display_value}")
            elif isinstance(value, list):
                if len(value) > 0:
                    lines.append(f"{key.replace('_', ' ').title()}: {len(value)} items")
                    # Show first few items if they're simple types
                    for i, item in enumerate(value[:3], 1):
                        if isinstance(item, (str, int, float, bool)):
                            lines.append(f"  {i}. {item}")
                        elif isinstance(item, dict):
                            # Show first field of each dict item
                            first_field = next(iter(item.items()), None)
                            if first_field:
                                lines.append(f"  {i}. {first_field[0]}: {first_field[1]}")
                else:
                    lines.append(f"{key.replace('_', ' ').title()}: 0 items")
            elif isinstance(value, dict):
                lines.append(f"{key.replace('_', ' ').title()}:")
                # Show nested dict fields
                for k, v in value.items():
                    if not isinstance(v, (dict, list)):
                        lines.append(f"  - {k.replace('_', ' ').title()}: {v}")

        if len(lines) > 1:
            return "\n".join(lines)

        # Last resort: show formatted JSON
        return f"✅ Success\n{json.dumps(data, indent=2)}"

    def _format_list_data(self, data: List, endpoint: EndpointSchema) -> str:
        """Format list data from REAL API response"""
        if not data:
            return "✅ No items found"

        lines = [f"✅ Found {len(data)} item(s)"]

        # Show first few items
        for i, item in enumerate(data[:3], 1):
            if isinstance(item, dict):
                # Extract key info from each item
                item_info = []
                for key in ["name", "title", "vendor", "category", "amount", "total"]:
                    if key in item:
                        item_info.append(f"{item[key]}")

                if item_info:
                    lines.append(f"{i}. {', '.join(item_info)}")
                else:
                    # Show first 2 fields
                    fields = list(item.items())[:2]
                    lines.append(f"{i}. {', '.join(f'{k}: {v}' for k, v in fields)}")
            else:
                lines.append(f"{i}. {item}")

        if len(data) > 3:
            lines.append(f"... and {len(data) - 3} more")

        return "\n".join(lines)

    def _generate_error_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate error response from REAL API error"""
        error_msg = api_result.get("error", "Unknown error")
        status_code = api_result.get("status_code", 500)

        logger.error(f"API Error: {status_code} - {error_msg}")

        if status_code == 404:
            response = f"❌ Not found: {error_msg}"
        elif status_code == 400:
            response = f"⚠️ Bad request: {error_msg}"
        elif status_code == 422:
            response = f"⚠️ Validation error: {error_msg}"
        elif status_code == 500:
            response = f"❌ Server error: {error_msg}"
        else:
            response = f"❌ Error ({status_code}): {error_msg}"

        return {
            "response": response,
            "suggestions": [
                "Try rephrasing your request",
                "Check if all required information is provided"
            ]
        }

    def _get_suggestions(self, category: str) -> List[str]:
        """Get suggestions based on endpoint category"""
        suggestions_map = {
            "receipt_upload": [
                "Show my spending dashboard",
                "Check budget alerts",
                "See spending patterns"
            ],
            "financial_goals": [
                "Show my goals",
                "Check goal progress",
                "Get a savings plan"
            ],
            "reports": [
                "Schedule weekly reports",
                "View report history",
                "Show dashboard"
            ],
            "spending_analysis": [
                "Get budget recommendations",
                "Check savings opportunities",
                "See spending by category"
            ],
            "user_profile": [
                "Show my profile",
                "Set up a budget",
                "Create a goal"
            ],
            "subscriptions": [
                "Find unused subscriptions",
                "See total subscription cost"
            ],
            "family_budgets": [
                "View family dashboard",
                "Compare my spending",
                "See family budget"
            ],
            "gamification": [
                "Show leaderboard",
                "View my badges",
                "Check my stats"
            ],
            "social_comparison": [
                "Get savings recommendations",
                "See category breakdown"
            ]
        }

        return suggestions_map.get(category, [
            "Ask 'what can you do?' to see all capabilities"
        ])


# Global instance
_response_generator = None


def get_response_generator() -> ResponseGenerator:
    """Get global response generator instance"""
    global _response_generator
    if _response_generator is None:
        _response_generator = ResponseGenerator()
    return _response_generator
