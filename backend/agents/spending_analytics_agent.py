"""
PROJECT LUMEN - Spending Analytics Agent
Provides in-depth analysis of spending patterns, category breakdowns, and savings opportunities
"""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import numpy as np

from backend.rag.vector_store import get_vector_store
from backend.utils.user_storage import get_user_storage
from backend.utils.ollama_client import ollama_client
from backend.utils.logger import logger


class SpendingAnalyticsAgent:
    """Provides in-depth spending analytics and insights"""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.user_storage = get_user_storage()
        self.ollama = ollama_client

    def analyze_category_deep_dive(self, user_id: str, category: str, months: int = 3) -> Dict:
        """
        Deep dive analysis for a specific spending category

        Args:
            user_id: User ID
            category: Category to analyze
            months: Number of months to analyze

        Returns:
            Comprehensive category analysis
        """
        logger.info(f"SpendingAnalyticsAgent: Deep dive on {category} for {user_id}")

        profile = self.user_storage.ensure_profile_exists(user_id)

        # Get data for specified period
        end_date = date.today()
        start_date = end_date - relativedelta(months=months)

        receipts = self._get_user_receipts(user_id, start_date, end_date)
        category_receipts = [r for r in receipts if r.get('category') == category]

        if not category_receipts:
            return {
                "category": category,
                "message": f"No spending data found for {category}",
                "total_transactions": 0
            }

        # Calculate statistics
        total_spent = sum(r['amount'] for r in category_receipts)
        avg_transaction = total_spent / len(category_receipts)

        # Monthly breakdown
        monthly_breakdown = self._calculate_monthly_trends(category_receipts)

        # Weekly pattern
        weekly_pattern = self._calculate_weekly_pattern(category_receipts)

        # Vendor analysis
        vendor_breakdown = self._analyze_vendors(category_receipts)

        # Budget comparison
        monthly_budget = profile.budget_categories.get(category, 0)
        avg_monthly_spend = total_spent / months
        budget_status = "over" if avg_monthly_spend > monthly_budget else "under"

        # Identify trends
        trend = self._identify_trend(monthly_breakdown)

        # Recurring vs one-time
        recurring_analysis = self._analyze_recurring_expenses(category_receipts)

        # LLM-powered insights
        insights = self._generate_category_insights_llm(
            user_id,
            category,
            category_receipts,
            monthly_breakdown,
            vendor_breakdown,
            monthly_budget,
            avg_monthly_spend
        )

        return {
            "user_id": user_id,
            "category": category,
            "period_months": months,
            "summary": {
                "total_spent": round(total_spent, 2),
                "total_transactions": len(category_receipts),
                "avg_transaction": round(avg_transaction, 2),
                "avg_monthly_spend": round(avg_monthly_spend, 2),
                "monthly_budget": monthly_budget,
                "budget_status": budget_status,
                "variance_from_budget": round(avg_monthly_spend - monthly_budget, 2),
                "trend": trend
            },
            "monthly_breakdown": monthly_breakdown,
            "weekly_pattern": weekly_pattern,
            "vendor_breakdown": vendor_breakdown,
            "recurring_analysis": recurring_analysis,
            "insights": insights.get("insights", []),
            "recommendations": insights.get("recommendations", [])
        }

    def analyze_monthly_spending(self, user_id: str, year: int, month: int) -> Dict:
        """
        Comprehensive analysis of spending for a specific month

        Args:
            user_id: User ID
            year: Year
            month: Month (1-12)

        Returns:
            Detailed monthly spending analysis
        """
        logger.info(f"SpendingAnalyticsAgent: Analyzing {year}-{month:02d} for {user_id}")

        profile = self.user_storage.ensure_profile_exists(user_id)

        # Get month date range
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        if not receipts:
            return {
                "month": f"{year}-{month:02d}",
                "message": "No spending data for this month",
                "total_spent": 0
            }

        # Overall stats
        total_spent = sum(r['amount'] for r in receipts)

        # Category breakdown
        category_breakdown = self._calculate_category_breakdown(receipts)

        # Weekly breakdown (by week of month)
        weekly_breakdown = self._calculate_weekly_breakdown(receipts)

        # Day-by-day spending
        daily_spending = self._calculate_daily_spending(receipts)

        # Top expenses
        top_expenses = sorted(receipts, key=lambda x: x['amount'], reverse=True)[:10]

        # Budget performance
        budget_performance = self._calculate_budget_performance(category_breakdown, profile.budget_categories)

        # Compare to previous month
        prev_month_date = start_date - relativedelta(months=1)
        prev_month_end = start_date - timedelta(days=1)
        prev_receipts = self._get_user_receipts(user_id, prev_month_date, prev_month_end)
        prev_total = sum(r['amount'] for r in prev_receipts)

        month_over_month_change = total_spent - prev_total
        percent_change = (month_over_month_change / prev_total * 100) if prev_total > 0 else 0

        # Identify spending spikes
        spending_spikes = self._identify_spending_spikes(daily_spending)

        # LLM analysis
        monthly_insights = self._generate_monthly_insights_llm(
            user_id,
            receipts,
            category_breakdown,
            budget_performance,
            spending_spikes,
            percent_change
        )

        return {
            "user_id": user_id,
            "month": f"{year}-{month:02d}",
            "summary": {
                "total_spent": round(total_spent, 2),
                "total_transactions": len(receipts),
                "avg_transaction": round(total_spent / len(receipts), 2),
                "income": profile.salary_monthly,
                "savings": round(profile.salary_monthly - total_spent, 2),
                "savings_rate": round((profile.salary_monthly - total_spent) / profile.salary_monthly, 3) if profile.salary_monthly > 0 else 0
            },
            "vs_previous_month": {
                "previous_total": round(prev_total, 2),
                "change": round(month_over_month_change, 2),
                "percent_change": round(percent_change, 1),
                "trend": "increasing" if month_over_month_change > 0 else "decreasing"
            },
            "category_breakdown": category_breakdown,
            "weekly_breakdown": weekly_breakdown,
            "daily_spending": daily_spending,
            "top_expenses": [
                {
                    "vendor": t['vendor'],
                    "amount": t['amount'],
                    "date": t['date'],
                    "category": t['category']
                }
                for t in top_expenses
            ],
            "budget_performance": budget_performance,
            "spending_spikes": spending_spikes,
            "insights": monthly_insights.get("insights", []),
            "recommendations": monthly_insights.get("recommendations", [])
        }

    def get_savings_opportunities(self, user_id: str) -> Dict:
        """
        Identify specific savings opportunities based on spending patterns

        Args:
            user_id: User ID

        Returns:
            Detailed savings opportunities by category
        """
        logger.info(f"SpendingAnalyticsAgent: Finding savings opportunities for {user_id}")

        profile = self.user_storage.ensure_profile_exists(user_id)
        goals = self.user_storage.get_all_goals(user_id)

        # Get last 3 months of data
        end_date = date.today()
        start_date = end_date - relativedelta(months=3)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        if not receipts:
            return {
                "user_id": user_id,
                "message": "No spending data to analyze",
                "total_savings_potential": 0
            }

        # Category breakdown
        category_breakdown = self._calculate_category_breakdown(receipts)

        # Analyze each category for savings
        category_opportunities = {}
        total_savings_potential = 0

        for category, data in category_breakdown.items():
            budget = profile.budget_categories.get(category, 0)
            avg_monthly = data['amount'] / 3

            opportunity = self._analyze_category_savings(
                user_id,
                category,
                [r for r in receipts if r.get('category') == category],
                avg_monthly,
                budget
            )

            if opportunity['savings_potential'] > 0:
                category_opportunities[category] = opportunity
                total_savings_potential += opportunity['savings_potential']

        # Sort by savings potential
        sorted_opportunities = dict(
            sorted(category_opportunities.items(), key=lambda x: x[1]['savings_potential'], reverse=True)
        )

        # Calculate impact on goals
        goal_impact = self._calculate_savings_goal_impact(total_savings_potential, goals)

        # LLM-powered savings strategy
        savings_strategy = self._generate_savings_strategy_llm(
            user_id,
            sorted_opportunities,
            total_savings_potential,
            goal_impact,
            profile
        )

        return {
            "user_id": user_id,
            "analysis_period": "last_3_months",
            "total_savings_potential": round(total_savings_potential, 2),
            "annual_savings_potential": round(total_savings_potential * 12, 2),
            "opportunities_by_category": sorted_opportunities,
            "goal_impact": goal_impact,
            "strategy": savings_strategy.get("strategy", []),
            "priority_actions": savings_strategy.get("priority_actions", [])
        }

    def compare_spending_patterns(self, user_id: str, months_to_compare: int = 6) -> Dict:
        """
        Compare spending patterns over time to identify trends

        Args:
            user_id: User ID
            months_to_compare: Number of months to analyze

        Returns:
            Comparative spending analysis
        """
        logger.info(f"SpendingAnalyticsAgent: Comparing {months_to_compare} months for {user_id}")

        end_date = date.today()
        start_date = end_date - relativedelta(months=months_to_compare)

        receipts = self._get_user_receipts(user_id, start_date, end_date)

        if not receipts:
            return {
                "user_id": user_id,
                "message": "Insufficient data for comparison",
                "months_analyzed": 0
            }

        # Month-by-month totals
        monthly_totals = self._calculate_monthly_trends(receipts)

        # Category trends over time
        category_trends = self._calculate_category_trends(receipts, months_to_compare)

        # Identify seasonal patterns
        seasonal_patterns = self._identify_seasonal_patterns(monthly_totals)

        # Growth/decline analysis
        growth_analysis = self._analyze_growth_trends(monthly_totals, category_trends)

        # Volatility analysis (how consistent is spending?)
        volatility = self._calculate_spending_volatility(monthly_totals)

        return {
            "user_id": user_id,
            "months_analyzed": months_to_compare,
            "monthly_totals": monthly_totals,
            "category_trends": category_trends,
            "seasonal_patterns": seasonal_patterns,
            "growth_analysis": growth_analysis,
            "volatility": volatility
        }

    # ==================== HELPER METHODS ====================

    def _get_user_receipts(self, user_id: str, start_date: date, end_date: date) -> List[Dict]:
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
                'invoice_number': metadata.get('invoice_number')
            })

        return receipts

    def _calculate_category_breakdown(self, receipts: List[Dict]) -> Dict:
        """Calculate spending breakdown by category"""
        breakdown = {}

        for receipt in receipts:
            category = receipt['category']
            amount = receipt['amount']

            if category not in breakdown:
                breakdown[category] = {
                    'amount': 0.0,
                    'count': 0,
                    'avg_per_transaction': 0.0
                }

            breakdown[category]['amount'] += amount
            breakdown[category]['count'] += 1

        for category, data in breakdown.items():
            data['amount'] = round(data['amount'], 2)
            data['avg_per_transaction'] = round(data['amount'] / data['count'], 2)

        return breakdown

    def _calculate_monthly_trends(self, receipts: List[Dict]) -> Dict:
        """Calculate month-by-month spending"""
        monthly = defaultdict(lambda: {'total': 0.0, 'count': 0, 'categories': defaultdict(float)})

        for receipt in receipts:
            try:
                dt = datetime.strptime(receipt['date'], "%Y-%m-%d")
                month_key = dt.strftime("%Y-%m")

                monthly[month_key]['total'] += receipt['amount']
                monthly[month_key]['count'] += 1
                monthly[month_key]['categories'][receipt['category']] += receipt['amount']
            except:
                continue

        # Convert to regular dict and round values
        result = {}
        for month, data in sorted(monthly.items()):
            result[month] = {
                'total': round(data['total'], 2),
                'count': data['count'],
                'avg_per_transaction': round(data['total'] / data['count'], 2),
                'categories': {k: round(v, 2) for k, v in data['categories'].items()}
            }

        return result

    def _calculate_weekly_pattern(self, receipts: List[Dict]) -> Dict:
        """Analyze spending by day of week"""
        weekly = defaultdict(lambda: {'total': 0.0, 'count': 0})

        for receipt in receipts:
            try:
                dt = datetime.strptime(receipt['date'], "%Y-%m-%d")
                day_name = dt.strftime("%A")

                weekly[day_name]['total'] += receipt['amount']
                weekly[day_name]['count'] += 1
            except:
                continue

        result = {}
        for day, data in weekly.items():
            result[day] = {
                'total': round(data['total'], 2),
                'count': data['count'],
                'avg_per_day': round(data['total'] / data['count'], 2) if data['count'] > 0 else 0
            }

        return result

    def _analyze_vendors(self, receipts: List[Dict]) -> Dict:
        """Analyze spending by vendor"""
        vendors = defaultdict(lambda: {'total': 0.0, 'count': 0, 'transactions': []})

        for receipt in receipts:
            vendor = receipt['vendor']
            vendors[vendor]['total'] += receipt['amount']
            vendors[vendor]['count'] += 1
            vendors[vendor]['transactions'].append({
                'date': receipt['date'],
                'amount': receipt['amount']
            })

        # Top 10 vendors
        sorted_vendors = sorted(vendors.items(), key=lambda x: x[1]['total'], reverse=True)[:10]

        result = {}
        for vendor, data in sorted_vendors:
            result[vendor] = {
                'total': round(data['total'], 2),
                'count': data['count'],
                'avg_per_transaction': round(data['total'] / data['count'], 2)
            }

        return result

    def _identify_trend(self, monthly_breakdown: Dict) -> str:
        """Identify spending trend (increasing/decreasing/stable)"""
        if len(monthly_breakdown) < 2:
            return "insufficient_data"

        totals = [data['total'] for data in monthly_breakdown.values()]

        # Simple linear trend
        if len(totals) >= 3:
            recent_avg = np.mean(totals[-2:])
            older_avg = np.mean(totals[:-2])

            if recent_avg > older_avg * 1.1:
                return "increasing"
            elif recent_avg < older_avg * 0.9:
                return "decreasing"

        return "stable"

    def _analyze_recurring_expenses(self, receipts: List[Dict]) -> Dict:
        """Identify recurring vs one-time expenses"""
        # Group by vendor
        vendor_transactions = defaultdict(list)

        for receipt in receipts:
            vendor_transactions[receipt['vendor']].append({
                'date': receipt['date'],
                'amount': receipt['amount']
            })

        recurring = []
        one_time = []

        for vendor, transactions in vendor_transactions.items():
            if len(transactions) >= 3:
                # Check if amounts are similar (recurring subscription)
                amounts = [t['amount'] for t in transactions]
                avg_amount = np.mean(amounts)
                std_amount = np.std(amounts)

                if std_amount < avg_amount * 0.2:  # Low variance = likely subscription
                    recurring.append({
                        'vendor': vendor,
                        'frequency': len(transactions),
                        'avg_amount': round(avg_amount, 2),
                        'total': round(sum(amounts), 2)
                    })
                else:
                    one_time.extend([{
                        'vendor': vendor,
                        'date': t['date'],
                        'amount': t['amount']
                    } for t in transactions])
            else:
                one_time.extend([{
                    'vendor': vendor,
                    'date': t['date'],
                    'amount': t['amount']
                } for t in transactions])

        return {
            'recurring': sorted(recurring, key=lambda x: x['total'], reverse=True),
            'recurring_total': round(sum(r['total'] for r in recurring), 2),
            'one_time_count': len(one_time)
        }

    def _calculate_weekly_breakdown(self, receipts: List[Dict]) -> List[Dict]:
        """Break down month into weeks"""
        weekly = defaultdict(lambda: {'total': 0.0, 'count': 0, 'transactions': []})

        for receipt in receipts:
            try:
                dt = datetime.strptime(receipt['date'], "%Y-%m-%d")
                week_num = (dt.day - 1) // 7 + 1
                week_label = f"Week {week_num}"

                weekly[week_label]['total'] += receipt['amount']
                weekly[week_label]['count'] += 1
                weekly[week_label]['transactions'].append(receipt)
            except:
                continue

        result = []
        for week, data in sorted(weekly.items()):
            result.append({
                'week': week,
                'total': round(data['total'], 2),
                'count': data['count'],
                'avg_transaction': round(data['total'] / data['count'], 2) if data['count'] > 0 else 0
            })

        return result

    def _calculate_daily_spending(self, receipts: List[Dict]) -> List[Dict]:
        """Calculate spending by day"""
        daily = defaultdict(lambda: {'total': 0.0, 'count': 0})

        for receipt in receipts:
            date_str = receipt['date']
            daily[date_str]['total'] += receipt['amount']
            daily[date_str]['count'] += 1

        result = []
        for date_str, data in sorted(daily.items()):
            result.append({
                'date': date_str,
                'total': round(data['total'], 2),
                'count': data['count']
            })

        return result

    def _calculate_budget_performance(self, category_breakdown: Dict, budget: Dict) -> Dict:
        """Compare actual spending to budget by category"""
        performance = {}

        for category, data in category_breakdown.items():
            budget_amount = budget.get(category, 0)
            actual = data['amount']

            performance[category] = {
                'budget': budget_amount,
                'actual': actual,
                'difference': round(budget_amount - actual, 2),
                'percent_used': round((actual / budget_amount * 100), 1) if budget_amount > 0 else 0,
                'status': 'over' if actual > budget_amount else 'under'
            }

        return performance

    def _identify_spending_spikes(self, daily_spending: List[Dict]) -> List[Dict]:
        """Identify days with unusually high spending"""
        if not daily_spending:
            return []

        amounts = [d['total'] for d in daily_spending]
        avg = np.mean(amounts)
        std = np.std(amounts)

        spikes = []
        for day in daily_spending:
            if day['total'] > avg + (2 * std):  # More than 2 std devs above mean
                spikes.append({
                    'date': day['date'],
                    'amount': day['total'],
                    'vs_average': round(day['total'] - avg, 2)
                })

        return sorted(spikes, key=lambda x: x['amount'], reverse=True)

    def _analyze_category_savings(
        self,
        user_id: str,
        category: str,
        receipts: List[Dict],
        avg_monthly: float,
        budget: float
    ) -> Dict:
        """Analyze savings potential for a category"""
        # Industry averages (rough estimates)
        industry_averages = {
            'dining': 300,
            'groceries': 400,
            'entertainment': 200,
            'shopping': 250,
            'transportation': 300,
            'utilities': 150,
            'healthcare': 200,
            'travel': 400
        }

        savings_potential = 0
        strategies = []

        # Compare to budget
        if avg_monthly > budget and budget > 0:
            savings_potential += (avg_monthly - budget)
            strategies.append(f"Reduce to meet budget: save ${(avg_monthly - budget):.2f}/month")

        # Compare to industry average
        if category in industry_averages:
            if avg_monthly > industry_averages[category]:
                potential = avg_monthly - industry_averages[category]
                savings_potential += potential * 0.3  # Conservative 30% reduction
                strategies.append(f"Optimize to industry average: potential ${potential * 0.3:.2f}/month")

        # Identify recurring high-cost vendors
        vendor_totals = defaultdict(float)
        for r in receipts:
            vendor_totals[r['vendor']] += r['amount']

        top_vendor = max(vendor_totals.items(), key=lambda x: x[1]) if vendor_totals else None
        if top_vendor and top_vendor[1] > avg_monthly * 0.3:  # One vendor is 30%+ of category
            strategies.append(f"Consider alternative to {top_vendor[0]} (${top_vendor[1]:.2f})")

        return {
            'savings_potential': round(savings_potential, 2),
            'current_monthly': round(avg_monthly, 2),
            'budget': budget,
            'strategies': strategies
        }

    def _calculate_savings_goal_impact(self, monthly_savings: float, goals: List) -> Dict:
        """Calculate how savings would impact goals"""
        if not goals:
            return {
                'message': 'No active goals',
                'impact': []
            }

        impact = []
        for goal in goals:
            if goal.status != 'on_track':
                continue

            remaining = goal.target_amount - goal.current_savings
            months_with_current = remaining / goal.monthly_savings if goal.monthly_savings > 0 else 999
            months_with_savings = remaining / (goal.monthly_savings + monthly_savings) if (goal.monthly_savings + monthly_savings) > 0 else 999

            time_saved = months_with_current - months_with_savings

            impact.append({
                'goal_name': goal.name,
                'current_timeline_months': round(months_with_current, 1),
                'new_timeline_months': round(months_with_savings, 1),
                'time_saved_months': round(time_saved, 1),
                'accelerated_by': f"{int(time_saved * 30)} days"
            })

        return {
            'goals_impacted': len(impact),
            'impact': impact
        }

    def _calculate_category_trends(self, receipts: List[Dict], months: int) -> Dict:
        """Calculate trends for each category over time"""
        # Group by month and category
        monthly_category = defaultdict(lambda: defaultdict(float))

        for receipt in receipts:
            try:
                dt = datetime.strptime(receipt['date'], "%Y-%m-%d")
                month_key = dt.strftime("%Y-%m")
                category = receipt['category']

                monthly_category[month_key][category] += receipt['amount']
            except:
                continue

        # Calculate trends for each category
        category_trends = {}
        categories = set(r['category'] for r in receipts)

        for category in categories:
            values = []
            for month in sorted(monthly_category.keys()):
                values.append(monthly_category[month].get(category, 0))

            if len(values) >= 2:
                trend = "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"
                avg = np.mean(values)

                category_trends[category] = {
                    'trend': trend,
                    'avg_monthly': round(avg, 2),
                    'latest_month': round(values[-1], 2),
                    'change_from_first': round(values[-1] - values[0], 2)
                }

        return category_trends

    def _identify_seasonal_patterns(self, monthly_totals: Dict) -> Dict:
        """Identify seasonal spending patterns"""
        if len(monthly_totals) < 3:
            return {'seasonal': False, 'message': 'Insufficient data'}

        # Group by month number (1-12)
        monthly_averages = defaultdict(list)

        for month_key, data in monthly_totals.items():
            try:
                dt = datetime.strptime(month_key, "%Y-%m")
                month_num = dt.month
                monthly_averages[month_num].append(data['total'])
            except:
                continue

        # Calculate average for each month
        month_avgs = {month: np.mean(values) for month, values in monthly_averages.items()}

        if not month_avgs:
            return {'seasonal': False}

        overall_avg = np.mean(list(month_avgs.values()))
        high_months = {m: v for m, v in month_avgs.items() if v > overall_avg * 1.2}
        low_months = {m: v for m, v in month_avgs.items() if v < overall_avg * 0.8}

        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        return {
            'seasonal': len(high_months) > 0 or len(low_months) > 0,
            'high_spending_months': {month_names[m]: round(v, 2) for m, v in high_months.items()},
            'low_spending_months': {month_names[m]: round(v, 2) for m, v in low_months.items()},
            'overall_average': round(overall_avg, 2)
        }

    def _analyze_growth_trends(self, monthly_totals: Dict, category_trends: Dict) -> Dict:
        """Analyze overall growth/decline trends"""
        if len(monthly_totals) < 2:
            return {'trend': 'insufficient_data'}

        totals = [data['total'] for data in monthly_totals.values()]

        # Calculate linear regression slope
        x = np.arange(len(totals))
        if len(x) > 0:
            slope = np.polyfit(x, totals, 1)[0]
        else:
            slope = 0

        first_month = totals[0]
        last_month = totals[-1]
        total_change = last_month - first_month
        percent_change = (total_change / first_month * 100) if first_month > 0 else 0

        # Identify fastest growing categories
        growing_categories = []
        for cat, trend in category_trends.items():
            if trend['change_from_first'] > 0:
                growing_categories.append({
                    'category': cat,
                    'change': trend['change_from_first']
                })

        growing_categories = sorted(growing_categories, key=lambda x: x['change'], reverse=True)[:3]

        return {
            'overall_trend': 'increasing' if slope > 0 else 'decreasing',
            'total_change': round(total_change, 2),
            'percent_change': round(percent_change, 1),
            'monthly_change_rate': round(slope, 2),
            'fastest_growing_categories': growing_categories
        }

    def _calculate_spending_volatility(self, monthly_totals: Dict) -> Dict:
        """Calculate how volatile spending is"""
        if len(monthly_totals) < 3:
            return {'volatility': 'unknown'}

        totals = [data['total'] for data in monthly_totals.values()]
        avg = np.mean(totals)
        std = np.std(totals)

        coefficient_of_variation = (std / avg) if avg > 0 else 0

        # Classify volatility
        if coefficient_of_variation < 0.1:
            level = 'very_consistent'
            description = 'Spending is very consistent month-to-month'
        elif coefficient_of_variation < 0.2:
            level = 'consistent'
            description = 'Spending is fairly consistent'
        elif coefficient_of_variation < 0.3:
            level = 'moderate'
            description = 'Spending varies moderately'
        else:
            level = 'high'
            description = 'Spending is highly variable'

        return {
            'volatility_level': level,
            'coefficient_of_variation': round(coefficient_of_variation, 3),
            'std_deviation': round(std, 2),
            'description': description
        }

    # ==================== LLM-POWERED INSIGHTS ====================

    def _generate_category_insights_llm(
        self,
        user_id: str,
        category: str,
        receipts: List[Dict],
        monthly_breakdown: Dict,
        vendor_breakdown: Dict,
        monthly_budget: float,
        avg_monthly_spend: float
    ) -> Dict:
        """Generate insights for a specific category using LLM"""

        # Format data for LLM
        monthly_summary = "\n".join([
            f"- {month}: ${data['total']:.2f} ({data['count']} transactions)"
            for month, data in monthly_breakdown.items()
        ])

        vendor_summary = "\n".join([
            f"- {vendor}: ${data['total']:.2f} ({data['count']} visits)"
            for vendor, data in list(vendor_breakdown.items())[:5]
        ])

        prompt = f"""Analyze this user's {category} spending and provide insights and recommendations.

Category: {category}
Average Monthly Spending: ${avg_monthly_spend:.2f}
Monthly Budget: ${monthly_budget:.2f}
Budget Status: {"Over budget by ${(avg_monthly_spend - monthly_budget):.2f}" if avg_monthly_spend > monthly_budget else "Under budget by ${(monthly_budget - avg_monthly_spend):.2f}"}

Monthly Breakdown:
{monthly_summary}

Top Vendors:
{vendor_summary}

Provide:
1. 3-5 insights about spending patterns in this category
2. 3-5 specific, actionable recommendations to optimize spending

Respond in JSON format:
{{
    "insights": [
        "insight 1",
        "insight 2",
        "insight 3"
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2",
        "recommendation 3"
    ]
}}

Keep each insight and recommendation concise (1-2 sentences).
Return ONLY valid JSON."""

        system_message = "You are a financial analyst providing actionable spending insights."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.4,
                max_tokens=800
            )

            result = self.ollama.parse_json_response(response)

            if not result:
                return {
                    "insights": [f"Average monthly spending: ${avg_monthly_spend:.2f}"],
                    "recommendations": ["Track spending more closely in this category"]
                }

            return result

        except Exception as e:
            logger.error(f"Error generating category insights: {e}")
            return {
                "insights": [f"Average monthly spending: ${avg_monthly_spend:.2f}"],
                "recommendations": ["Track spending more closely in this category"]
            }

    def _generate_monthly_insights_llm(
        self,
        user_id: str,
        receipts: List[Dict],
        category_breakdown: Dict,
        budget_performance: Dict,
        spending_spikes: List[Dict],
        percent_change: float
    ) -> Dict:
        """Generate monthly insights using LLM"""

        profile = self.user_storage.ensure_profile_exists(user_id)

        category_summary = "\n".join([
            f"- {cat}: ${data['amount']:.2f} ({data['count']} transactions, avg ${data['avg_per_transaction']:.2f})"
            for cat, data in category_breakdown.items()
        ])

        over_budget = [
            f"{cat}: ${perf['actual']:.2f} vs budget ${perf['budget']:.2f} ({perf['percent_used']}% used)"
            for cat, perf in budget_performance.items() if perf['status'] == 'over'
        ]

        spikes_summary = "\n".join([
            f"- {spike['date']}: ${spike['amount']:.2f} (${spike['vs_average']:.2f} above average)"
            for spike in spending_spikes[:3]
        ]) if spending_spikes else "None"

        prompt = f"""Analyze this month's spending and provide insights.

Monthly Income: ${profile.salary_monthly:.2f}
Total Spent: ${sum(r['amount'] for r in receipts):.2f}
Change vs Previous Month: {percent_change:+.1f}%

Spending by Category:
{category_summary}

Over Budget Categories:
{chr(10).join(over_budget) if over_budget else 'None'}

Spending Spikes:
{spikes_summary}

Provide:
1. 4-6 key insights about this month's spending
2. 3-5 actionable recommendations for next month

Respond in JSON format:
{{
    "insights": [
        "insight 1",
        "insight 2"
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ]
}}

Return ONLY valid JSON."""

        system_message = "You are a financial advisor analyzing monthly spending patterns."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.5,
                max_tokens=1000
            )

            result = self.ollama.parse_json_response(response)

            if not result:
                return {
                    "insights": ["Monthly spending analysis complete"],
                    "recommendations": ["Continue tracking expenses"]
                }

            return result

        except Exception as e:
            logger.error(f"Error generating monthly insights: {e}")
            return {
                "insights": ["Monthly spending analysis complete"],
                "recommendations": ["Continue tracking expenses"]
            }

    def _generate_savings_strategy_llm(
        self,
        user_id: str,
        opportunities: Dict,
        total_savings_potential: float,
        goal_impact: Dict,
        profile
    ) -> Dict:
        """Generate comprehensive savings strategy using LLM"""

        opportunities_summary = "\n".join([
            f"- {cat}: Save ${opp['savings_potential']:.2f}/month\n  Current: ${opp['current_monthly']:.2f}, Budget: ${opp['budget']:.2f}\n  Strategies: {', '.join(opp['strategies'])}"
            for cat, opp in list(opportunities.items())[:5]
        ])

        goal_impact_summary = "\n".join([
            f"- {impact['goal_name']}: Reach goal {impact['time_saved_months']:.1f} months earlier ({impact['accelerated_by']})"
            for impact in goal_impact.get('impact', [])
        ]) if goal_impact.get('impact') else "No active goals"

        prompt = f"""Create a comprehensive savings strategy for this user.

Total Savings Potential: ${total_savings_potential:.2f}/month (${total_savings_potential * 12:.2f}/year)
Monthly Income: ${profile.salary_monthly:.2f}

Savings Opportunities:
{opportunities_summary}

Impact on Goals:
{goal_impact_summary}

Provide:
1. An overall savings strategy (3-5 strategic points)
2. 5 priority actions ranked by impact

Respond in JSON format:
{{
    "strategy": [
        "strategic point 1",
        "strategic point 2"
    ],
    "priority_actions": [
        "action 1 (highest impact)",
        "action 2",
        "action 3"
    ]
}}

Make recommendations specific, actionable, and realistic.
Return ONLY valid JSON."""

        system_message = "You are a financial planner creating personalized savings strategies."

        try:
            response = self.ollama.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=0.5,
                max_tokens=1000
            )

            result = self.ollama.parse_json_response(response)

            if not result:
                return {
                    "strategy": [f"Work toward saving ${total_savings_potential:.2f} per month"],
                    "priority_actions": ["Review and optimize spending in top categories"]
                }

            return result

        except Exception as e:
            logger.error(f"Error generating savings strategy: {e}")
            return {
                "strategy": [f"Work toward saving ${total_savings_potential:.2f} per month"],
                "priority_actions": ["Review and optimize spending in top categories"]
            }


# Global agent instance
_spending_analytics_agent = None


def get_spending_analytics_agent() -> SpendingAnalyticsAgent:
    """Get global spending analytics agent instance"""
    global _spending_analytics_agent
    if _spending_analytics_agent is None:
        _spending_analytics_agent = SpendingAnalyticsAgent()
    return _spending_analytics_agent
