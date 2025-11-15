"""
Response Generator - Converts API Responses to Natural Language
Creates friendly, conversational responses with suggestions
"""

from typing import Dict, Any, List, Optional

from backend.agents.api_registry import EndpointSchema
from backend.utils.logger import logger


class ResponseGenerator:
    """
    Generates natural language responses from API results
    Creates friendly, conversational output with emojis and suggestions
    """

    def __init__(self):
        """Initialize response generator"""
        pass

    def generate_response(
        self,
        endpoint: EndpointSchema,
        api_result: Dict[str, Any],
        user_message: str
    ) -> Dict[str, Any]:
        """
        Generate natural language response from API result

        Args:
            endpoint: Endpoint that was called
            api_result: Result from API call
            user_message: Original user message

        Returns:
            Dict with: response (str), suggestions (list)
        """
        if not api_result.get("success", False):
            return self._generate_error_response(api_result, endpoint)

        # Generate success response based on endpoint category
        category = endpoint.category

        if category == "receipt_upload":
            return self._generate_receipt_response(api_result, endpoint)
        elif category == "financial_goals":
            return self._generate_goal_response(api_result, endpoint)
        elif category == "reports":
            return self._generate_report_response(api_result, endpoint)
        elif category == "spending_analysis":
            return self._generate_spending_response(api_result, endpoint)
        elif category == "user_profile":
            return self._generate_profile_response(api_result, endpoint)
        elif category == "subscriptions":
            return self._generate_subscription_response(api_result, endpoint)
        elif category == "family_budgets":
            return self._generate_family_response(api_result, endpoint)
        elif category == "gamification":
            return self._generate_gamification_response(api_result, endpoint)
        elif category == "social_comparison":
            return self._generate_social_response(api_result, endpoint)
        else:
            return self._generate_generic_response(api_result, endpoint)

    def _generate_error_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate error response"""
        error_msg = api_result.get("error", "An error occurred")
        status_code = api_result.get("status_code", 500)

        if status_code == 404:
            response = f"❌ Sorry, I couldn't find what you're looking for. {error_msg}"
        elif status_code == 400:
            response = f"⚠️ There was an issue with the request. {error_msg}"
        elif status_code == 422:
            response = f"⚠️ Some information is missing or invalid. {error_msg}"
        else:
            response = f"❌ Oops! Something went wrong. {error_msg}"

        return {
            "response": response,
            "suggestions": [
                "Try rephrasing your request",
                "Ask me 'what can you do?' to see my capabilities"
            ]
        }

    def _generate_receipt_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate response for receipt upload"""
        data = api_result.get("data", {})

        if endpoint.method == "POST":
            # Receipt uploaded
            extracted = data.get("extracted_fields", {})
            vendor = extracted.get("vendor", "unknown")
            amount = extracted.get("amount", 0)

            response = f"✅ Great! I've added your ${amount:.2f} receipt from {vendor} to your expenses!"

            suggestions = [
                "Want to see your spending dashboard?",
                "Check if you have any budget alerts",
                "See your spending patterns"
            ]
        else:
            response = "✅ Receipt processed successfully!"
            suggestions = []

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _generate_goal_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate response for goal operations"""
        data = api_result.get("data", {})

        if endpoint.method == "POST":
            # Goal created
            name = data.get("name", "your goal")
            target = data.get("target_amount", 0)

            response = f"🎯 Awesome! I've created your goal: '{name}' with a target of ${target:,.2f}!"

            suggestions = [
                "Want to see a savings plan?",
                "Check your goal progress",
                "View all your goals"
            ]

        elif endpoint.method == "GET" and "plan" in endpoint.path:
            # Goal plan
            response = "📊 Here's your personalized savings plan!"
            suggestions = ["Track your progress", "Update your goal"]

        elif endpoint.method == "GET":
            # List goals
            goals = data.get("goals", [])
            total = len(goals)

            response = f"🎯 You have {total} financial goal{'s' if total != 1 else ''}!"
            suggestions = ["Create a new goal", "Check goal progress", "See dashboard"]

        else:
            response = "✅ Goal updated successfully!"
            suggestions = []

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _generate_report_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate response for report operations"""
        data = api_result.get("data", {})

        if "generate-now" in endpoint.path:
            email = data.get("details", {}).get("email", "you")
            report_type = data.get("details", {}).get("report_type", "financial")

            response = f"📧 Perfect! I'm generating your {report_type} report now. I'll email it to {email} shortly!"

            suggestions = [
                "Schedule weekly reports",
                "View report history",
                "See your dashboard"
            ]

        elif "schedule/weekly" in endpoint.path:
            day = data.get("schedule", {}).get("day_name", "the scheduled day")

            response = f"✅ Done! You'll receive weekly financial reports every {day}!"

            suggestions = [
                "Generate a report now",
                "View your schedule",
                "See dashboard"
            ]

        elif "schedule/monthly" in endpoint.path:
            day = data.get("schedule", {}).get("day_of_month", 1)

            response = f"✅ Perfect! You'll receive monthly reports on day {day} of each month!"

            suggestions = ["Generate a report now", "View dashboard"]

        else:
            response = "📊 Report ready!"
            suggestions = []

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _generate_spending_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate response for spending analysis"""
        data = api_result.get("data", {})

        if "dashboard" in endpoint.path:
            total_spent = data.get("total_spent", 0)
            budget_status = data.get("budget_status", {})

            response = f"📊 This period you've spent ${total_spent:,.2f}."

            if budget_status:
                budget_pct = budget_status.get("percentage_used", 0)
                response += f" You're at {budget_pct:.1f}% of your budget."

            suggestions = [
                "See spending breakdown by category",
                "Get budget recommendations",
                "Check for savings opportunities"
            ]

        elif "health-score" in endpoint.path:
            score = data.get("score", 0)

            if score >= 80:
                emoji = "🌟"
                message = "Excellent"
            elif score >= 60:
                emoji = "👍"
                message = "Good"
            elif score >= 40:
                emoji = "😐"
                message = "Fair"
            else:
                emoji = "⚠️"
                message = "Needs improvement"

            response = f"{emoji} Your financial health score is {score}/100 - {message}!"

            suggestions = [
                "Get personalized insights",
                "See spending patterns",
                "Check budget recommendations"
            ]

        else:
            response = "✅ Here's your financial analysis!"
            suggestions = []

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _generate_profile_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate response for profile operations"""
        data = api_result.get("data", {})

        if endpoint.method == "POST" and "salary" in endpoint.path:
            salary = data.get("salary_monthly", 0)
            response = f"✅ Updated! Your monthly salary is now set to ${salary:,.2f}."

            suggestions = [
                "Set up a budget",
                "Create savings goals",
                "View dashboard"
            ]

        elif endpoint.method == "POST":
            # Profile created
            response = "✅ Welcome! Your profile has been created successfully!"

            suggestions = [
                "Set your monthly salary",
                "Create your first goal",
                "Set up budget categories"
            ]

        else:
            response = "✅ Profile updated!"
            suggestions = []

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _generate_subscription_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate response for subscription operations"""
        data = api_result.get("data", {})

        if "unused" in endpoint.path:
            unused = data.get("unused_subscriptions", [])
            potential_savings = data.get("potential_savings", 0)

            count = len(unused)

            if count > 0:
                response = f"💡 I found {count} unused subscription{'s' if count != 1 else ''}! You could save ${potential_savings:,.2f}/month by canceling them."
            else:
                response = "✅ Great news! You're using all your subscriptions efficiently!"

            suggestions = [
                "See all subscriptions",
                "View spending patterns",
                "Get more savings tips"
            ]

        else:
            subs = data.get("subscriptions", [])
            total = data.get("total_subscriptions", len(subs))

            response = f"📱 You have {total} active subscription{'s' if total != 1 else ''}."

            suggestions = [
                "Find unused subscriptions",
                "See total subscription cost",
                "View spending breakdown"
            ]

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _generate_family_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate response for family operations"""
        data = api_result.get("data", {})

        if "create" in endpoint.path:
            family_name = data.get("name", "your family")
            invite_code = data.get("invite_code", "")

            response = f"👨‍👩‍👧‍👦 Family '{family_name}' created! Share code: {invite_code}"

            suggestions = [
                "View family dashboard",
                "Set shared budget",
                "Invite family members"
            ]

        elif "join" in endpoint.path:
            family_name = data.get("name", "the family")

            response = f"✅ Welcome! You've joined '{family_name}'!"

            suggestions = [
                "View family dashboard",
                "Compare your spending",
                "See family budget"
            ]

        else:
            response = "✅ Family operation completed!"
            suggestions = []

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _generate_gamification_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate response for gamification"""
        data = api_result.get("data", {})

        if "stats" in endpoint.path:
            level = data.get("level", 1)
            points = data.get("total_points", 0)
            badges = data.get("badges_earned", 0)

            response = f"🎮 You're Level {level} with {points} points! You've earned {badges} badge{'s' if badges != 1 else ''}!"

            suggestions = [
                "View leaderboard",
                "See your badges",
                "Check achievements"
            ]

        elif "leaderboard" in endpoint.path:
            response = "🏆 Here's the leaderboard!"
            suggestions = ["See your stats", "Earn more points"]

        else:
            response = "✅ Points awarded!"
            suggestions = []

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _generate_social_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate response for social comparison"""
        data = api_result.get("data", {})

        if "percentile" in endpoint.path:
            percentile = data.get("overall_percentile", 50)

            if percentile < 25:
                response = f"🌟 Excellent! You're in the top 25% - you spend less than {100 - percentile:.0f}% of users!"
            elif percentile < 50:
                response = f"👍 Good! You spend less than {100 - percentile:.0f}% of users."
            elif percentile < 75:
                response = f"😐 You spend more than {percentile:.0f}% of users. There's room for improvement!"
            else:
                response = f"⚠️ You're in the top {100 - percentile:.0f}% of spenders. Consider cutting back!"

            suggestions = [
                "Get savings recommendations",
                "See category breakdown",
                "Compare to peers"
            ]

        else:
            response = "✅ Here's your social comparison!"
            suggestions = []

        return {
            "response": response,
            "suggestions": suggestions
        }

    def _generate_generic_response(
        self,
        api_result: Dict[str, Any],
        endpoint: EndpointSchema
    ) -> Dict[str, Any]:
        """Generate generic success response"""
        return {
            "response": "✅ Done! Your request was completed successfully.",
            "suggestions": [
                "Ask me 'what can you do?' to see my capabilities",
                "Say 'help' for assistance"
            ]
        }


# Global instance
_response_generator = None


def get_response_generator() -> ResponseGenerator:
    """Get global response generator instance"""
    global _response_generator
    if _response_generator is None:
        _response_generator = ResponseGenerator()
    return _response_generator
