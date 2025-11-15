"""
PROJECT LUMEN - Savings Opportunity Agent
Uses LLM to analyze receipts and provide intelligent savings suggestions
"""

from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from backend.utils.ollama_client import ollama_client
from backend.rag.vector_store import get_vector_store
from backend.utils.user_storage import get_user_storage
from backend.utils.logger import logger


class SavingsOpportunityAgent:
    """Analyzes spending and generates LLM-powered savings opportunities"""

    def __init__(self):
        self.ollama = ollama_client
        self.vector_store = get_vector_store()
        self.user_storage = get_user_storage()

    def analyze_receipt_for_savings(
        self,
        receipt: Dict,
        user_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze a single receipt and find savings opportunities using LLM

        Args:
            receipt: Receipt data with vendor, amount, category, etc.
            user_id: User ID
            user_context: Optional context about user's goals and budget

        Returns:
            Savings analysis with LLM-generated suggestions
        """
        logger.info(f"SavingsOpportunityAgent: Analyzing receipt for savings - {receipt.get('vendor')}")

        # Get user profile for context
        profile = self.user_storage.ensure_profile_exists(user_id)

        # Get user's goals for motivation context
        goals = self.user_storage.get_all_goals(user_id)

        # Build context for LLM
        context = {
            "receipt": receipt,
            "monthly_income": profile.salary_monthly,
            "budget": profile.budget_categories,
            "active_goals": [{"name": g.name, "target": g.target_amount} for g in goals if g.status == "on_track"]
        }

        # Create LLM prompt
        prompt = f"""Analyze this purchase and provide intelligent savings suggestions.

Purchase Details:
- Vendor: {receipt.get('vendor', 'Unknown')}
- Amount: ${receipt.get('amount', 0):.2f}
- Category: {receipt.get('category', 'other')}
- Date: {receipt.get('date', 'Unknown')}
- Items: {receipt.get('items', [])}

User Financial Context:
- Monthly Income: ${profile.salary_monthly:.2f}
- Budget for {receipt.get('category', 'this category')}: ${profile.budget_categories.get(receipt.get('category', 'other'), 0):.2f}
- Active Goals: {', '.join([g['name'] for g in context['active_goals']]) if context['active_goals'] else 'None'}

Analyze this purchase and provide:
1. Could this expense have been avoided or reduced?
2. Specific cheaper alternatives or strategies
3. How much could be saved
4. Impact on user's goals if they save this amount

Respond in JSON format:
{{
    "can_save": true/false,
    "savings_amount": <amount in dollars>,
    "alternatives": ["specific alternative 1", "specific alternative 2"],
    "strategy": "brief strategy description",
    "goal_impact": "how savings help with goals",
    "priority": "high/medium/low",
    "reasoning": "why this suggestion makes sense"
}}

Return ONLY valid JSON, no other text."""

        system_message = "You are a financial advisor who helps people save money through practical, specific suggestions. Be encouraging and specific."

        try:
            # Get LLM response
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=800
            )

            # Parse JSON response
            result = self.ollama.parse_json_response(response)

            if not result:
                logger.warning("Failed to parse LLM response, using fallback")
                return self._fallback_analysis(receipt, profile, context['active_goals'])

            return {
                "receipt_id": receipt.get('document_id'),
                "vendor": receipt.get('vendor'),
                "amount": receipt.get('amount'),
                "category": receipt.get('category'),
                "analysis": result,
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in LLM savings analysis: {e}")
            return self._fallback_analysis(receipt, profile, context['active_goals'])

    def find_subscription_waste(self, user_id: str) -> Dict:
        """
        Detect unused subscriptions using LLM analysis

        Args:
            user_id: User ID

        Returns:
            Subscription waste analysis
        """
        logger.info(f"SavingsOpportunityAgent: Finding subscription waste for {user_id}")

        # Get receipts from last 3 months
        end_date = date.today()
        start_date = end_date - relativedelta(months=3)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        # Filter for recurring/subscription-like purchases
        recurring_purchases = self._identify_recurring(receipts)

        if not recurring_purchases:
            return {
                "subscriptions_found": 0,
                "potential_waste": 0.0,
                "recommendations": [],
                "message": "No recurring subscriptions detected in last 3 months"
            }

        # Create LLM prompt for subscription analysis
        subscription_list = "\n".join([
            f"- {item['vendor']}: ${item['avg_amount']:.2f}/month ({item['frequency']} times in 3 months)"
            for item in recurring_purchases
        ])

        prompt = f"""Analyze these recurring purchases to identify potential subscription waste.

Recurring Purchases (last 3 months):
{subscription_list}

For each recurring purchase:
1. Is this likely a subscription or recurring service?
2. Based on frequency, does usage seem low or wasteful?
3. What's the potential savings if cancelled or downgraded?
4. Specific recommendation (cancel, downgrade, or keep)

Respond in JSON format:
{{
    "subscriptions": [
        {{
            "vendor": "vendor name",
            "monthly_cost": <amount>,
            "usage_level": "low/medium/high",
            "recommendation": "cancel/downgrade/keep",
            "potential_savings": <amount>,
            "reasoning": "why this recommendation"
        }}
    ],
    "total_potential_savings": <total amount>,
    "summary": "brief summary of findings"
}}

Return ONLY valid JSON."""

        system_message = "You are a subscription optimization expert. Help users identify and eliminate wasteful recurring expenses."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.2,
                max_tokens=1000
            )

            result = self.ollama.parse_json_response(response)

            if not result:
                return self._fallback_subscription_analysis(recurring_purchases)

            return result

        except Exception as e:
            logger.error(f"Error in subscription analysis: {e}")
            return self._fallback_subscription_analysis(recurring_purchases)

    def analyze_bulk_buying_opportunities(self, user_id: str) -> Dict:
        """
        Identify items user buys frequently that could be bought in bulk using LLM

        Args:
            user_id: User ID

        Returns:
            Bulk buying recommendations
        """
        logger.info(f"SavingsOpportunityAgent: Analyzing bulk buying for {user_id}")

        # Get last 2 months of receipts
        end_date = date.today()
        start_date = end_date - relativedelta(months=2)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        # Focus on groceries and essential items
        essential_receipts = [
            r for r in receipts
            if r.get('category') in ['groceries', 'household', 'healthcare']
        ]

        if len(essential_receipts) < 5:
            return {
                "opportunities_found": 0,
                "potential_savings": 0.0,
                "recommendations": [],
                "message": "Not enough grocery/essential purchases to analyze bulk buying"
            }

        # Group by vendor and summarize
        vendor_summary = {}
        for receipt in essential_receipts:
            vendor = receipt.get('vendor', 'Unknown')
            amount = receipt.get('amount', 0)

            if vendor not in vendor_summary:
                vendor_summary[vendor] = {'count': 0, 'total': 0, 'category': receipt.get('category')}

            vendor_summary[vendor]['count'] += 1
            vendor_summary[vendor]['total'] += amount

        summary_text = "\n".join([
            f"- {vendor}: {data['count']} purchases, ${data['total']:.2f} total ({data['category']})"
            for vendor, data in vendor_summary.items()
        ])

        prompt = f"""Analyze these grocery/essential purchases to find bulk buying opportunities.

Recent Purchases (last 2 months):
{summary_text}

For frequently purchased items/vendors:
1. Which items are good candidates for bulk buying?
2. Estimated savings from bulk purchase (typically 15-30% for bulk)
3. Specific recommendations for where to buy in bulk
4. Storage considerations

Respond in JSON format:
{{
    "opportunities": [
        {{
            "item_category": "category name",
            "current_monthly_spend": <amount>,
            "bulk_buying_suggestion": "specific suggestion",
            "estimated_savings": <amount per month>,
            "where_to_buy": "specific store/platform",
            "notes": "any important notes"
        }}
    ],
    "total_monthly_savings": <total amount>,
    "summary": "overall recommendation"
}}

Return ONLY valid JSON."""

        system_message = "You are a smart shopping advisor who helps people save money through strategic bulk buying."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=1000
            )

            result = self.ollama.parse_json_response(response)

            if not result:
                return {"opportunities_found": 0, "message": "Could not analyze bulk buying opportunities"}

            return result

        except Exception as e:
            logger.error(f"Error in bulk buying analysis: {e}")
            return {"opportunities_found": 0, "error": str(e)}

    # ==================== HELPER METHODS ====================

    def _get_user_receipts(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Get user's receipts within date range"""
        all_chunks = self.vector_store.get_all_chunks()

        receipts = []
        seen_ids = set()

        for chunk in all_chunks:
            metadata = chunk.get('metadata', {})

            if metadata.get('user_id') != user_id:
                continue

            receipt_date_str = metadata.get('date')
            if not receipt_date_str:
                continue

            try:
                receipt_date = datetime.strptime(receipt_date_str, "%Y-%m-%d").date()
            except:
                continue

            if not (start_date <= receipt_date <= end_date):
                continue

            doc_id = metadata.get('document_id')
            if doc_id in seen_ids:
                continue

            seen_ids.add(doc_id)

            receipts.append({
                'document_id': doc_id,
                'vendor': metadata.get('vendor', 'Unknown'),
                'date': receipt_date_str,
                'amount': metadata.get('amount', 0),
                'category': metadata.get('category', 'other'),
                'items': metadata.get('items', [])
            })

        return receipts

    def _identify_recurring(self, receipts: List[Dict]) -> List[Dict]:
        """Identify recurring purchases (same vendor, regular frequency)"""
        vendor_purchases = {}

        for receipt in receipts:
            vendor = receipt.get('vendor', 'Unknown')

            if vendor not in vendor_purchases:
                vendor_purchases[vendor] = []

            vendor_purchases[vendor].append(receipt)

        # Find vendors with 2+ purchases
        recurring = []
        for vendor, purchases in vendor_purchases.items():
            if len(purchases) >= 2:
                avg_amount = sum(p['amount'] for p in purchases) / len(purchases)
                recurring.append({
                    'vendor': vendor,
                    'frequency': len(purchases),
                    'avg_amount': avg_amount,
                    'total': sum(p['amount'] for p in purchases),
                    'category': purchases[0].get('category', 'other')
                })

        return recurring

    def _fallback_analysis(self, receipt: Dict, profile, goals: List) -> Dict:
        """Fallback analysis when LLM fails"""
        amount = receipt.get('amount', 0)
        category = receipt.get('category', 'other')

        # Simple rule-based fallback
        can_save = amount > 100 and category in ['dining', 'entertainment', 'shopping']
        savings = amount * 0.3 if can_save else 0

        return {
            "receipt_id": receipt.get('document_id'),
            "vendor": receipt.get('vendor'),
            "amount": amount,
            "category": category,
            "analysis": {
                "can_save": can_save,
                "savings_amount": savings,
                "alternatives": ["Consider more budget-friendly options"],
                "strategy": "Review necessity of this expense",
                "goal_impact": f"Saving ${savings:.2f} helps reach your goals faster",
                "priority": "medium",
                "reasoning": "Fallback analysis - LLM unavailable"
            },
            "analyzed_at": datetime.now().isoformat()
        }

    def _fallback_subscription_analysis(self, recurring: List[Dict]) -> Dict:
        """Fallback for subscription analysis"""
        total = sum(item['avg_amount'] for item in recurring)

        return {
            "subscriptions_found": len(recurring),
            "potential_waste": total * 0.2,
            "recommendations": [f"Review {item['vendor']} subscription" for item in recurring[:3]],
            "message": "Basic analysis - review recurring expenses manually"
        }


# Global agent instance
_savings_opportunity_agent = None


def get_savings_opportunity_agent() -> SavingsOpportunityAgent:
    """Get global savings opportunity agent instance"""
    global _savings_opportunity_agent
    if _savings_opportunity_agent is None:
        _savings_opportunity_agent = SavingsOpportunityAgent()
    return _savings_opportunity_agent
