"""
PROJECT LUMEN - Agentic RAG Report Generation Agent
Coordinates all agents to generate comprehensive financial reports using RAG
"""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import json

from backend.rag.vector_store import get_vector_store
from backend.rag.retriever import get_hybrid_retriever
from backend.utils.user_storage import get_user_storage
from backend.utils.mongo_storage import get_mongo_storage
from backend.utils.logger import logger
from backend.config import settings

# Import all agents
from backend.agents.personal_finance_agent import PersonalFinanceAgent
from backend.agents.goal_planner_agent import GoalPlannerAgent
from backend.agents.savings_opportunity_agent import SavingsOpportunityAgent
from backend.agents.fraud_agent import FraudAgent
from backend.agents.pattern_agent import PatternAgent
from backend.agents.behavioral_agent import BehavioralAgent
from backend.agents.compliance_agent import ComplianceAgent
from backend.agents.audit_agent import AuditAgent


class AgenticReportGenerator:
    """
    Comprehensive report generator that uses RAG and coordinates all agents
    to analyze financial data and generate actionable insights
    """

    def __init__(self):
        """Initialize all agents and data sources"""
        self.vector_store = get_vector_store()
        self.retriever = get_hybrid_retriever()
        self.user_storage = get_user_storage()
        self.mongo_storage = get_mongo_storage()

        # Initialize all agents
        self.personal_finance_agent = PersonalFinanceAgent()
        self.goal_planner_agent = GoalPlannerAgent()
        self.savings_agent = SavingsOpportunityAgent()
        self.fraud_agent = FraudAgent()
        self.pattern_agent = PatternAgent()
        self.behavioral_agent = BehavioralAgent()
        self.compliance_agent = ComplianceAgent()
        self.audit_agent = AuditAgent()

    def generate_comprehensive_report(
        self,
        user_id: str,
        report_type: str = "weekly",
        include_attachments: bool = True
    ) -> Dict:
        """
        Generate comprehensive financial report using all agents and RAG

        Args:
            user_id: User ID
            report_type: "weekly", "monthly", "quarterly", or "yearly"
            include_attachments: Whether to include PDF/HTML attachments

        Returns:
            Dictionary containing complete report data
        """
        logger.info(f"AgenticReportGenerator: Generating {report_type} report for {user_id}")

        # Determine date range based on report type
        end_date = date.today()
        if report_type == "weekly":
            start_date = end_date - timedelta(days=7)
            period_name = f"Week of {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        elif report_type == "monthly":
            start_date = end_date - relativedelta(months=1)
            period_name = f"{start_date.strftime('%B %Y')}"
        elif report_type == "quarterly":
            start_date = end_date - relativedelta(months=3)
            period_name = f"Q{(end_date.month-1)//3 + 1} {end_date.year}"
        elif report_type == "yearly":
            start_date = end_date - relativedelta(years=1)
            period_name = f"Year {end_date.year}"
        else:
            start_date = end_date - timedelta(days=7)
            period_name = "Last 7 Days"

        # Step 1: Retrieve all relevant data using RAG
        logger.info(f"Step 1: Retrieving data via RAG for period {start_date} to {end_date}")
        rag_data = self._retrieve_financial_data_via_rag(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        # Step 2: Get personal finance analysis
        logger.info("Step 2: Running Personal Finance Agent")
        finance_analysis = self._get_finance_analysis(user_id, report_type)

        # Step 3: Analyze goal progress
        logger.info("Step 3: Running Goal Planner Agent")
        goal_analysis = self._get_goal_analysis(user_id)

        # Step 4: Identify savings opportunities
        logger.info("Step 4: Running Savings Opportunity Agent")
        savings_analysis = self._get_savings_opportunities(user_id, rag_data)

        # Step 5: Fraud and anomaly detection
        logger.info("Step 5: Running Fraud Detection Agent")
        fraud_analysis = self._get_fraud_analysis(user_id)

        # Step 6: Pattern detection
        logger.info("Step 6: Running Pattern Detection Agent")
        pattern_analysis = self._get_pattern_analysis(user_id)

        # Step 7: Behavioral insights
        logger.info("Step 7: Running Behavioral Agent")
        behavioral_analysis = self._get_behavioral_insights(user_id)

        # Step 8: Compliance check
        logger.info("Step 8: Running Compliance Agent")
        compliance_analysis = self._get_compliance_analysis(user_id, rag_data)

        # Step 9: Audit summary
        logger.info("Step 9: Running Audit Agent")
        audit_analysis = self._get_audit_summary(user_id)

        # Step 10: Synthesize all insights
        logger.info("Step 10: Synthesizing comprehensive report")
        comprehensive_report = {
            "report_metadata": {
                "user_id": user_id,
                "report_type": report_type,
                "period": period_name,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "generated_at": datetime.now().isoformat()
            },
            "executive_summary": self._create_executive_summary(
                finance_analysis,
                goal_analysis,
                savings_analysis,
                fraud_analysis
            ),
            "financial_overview": finance_analysis,
            "goal_progress": goal_analysis,
            "savings_opportunities": savings_analysis,
            "fraud_alerts": fraud_analysis,
            "spending_patterns": pattern_analysis,
            "behavioral_insights": behavioral_analysis,
            "compliance_status": compliance_analysis,
            "audit_summary": audit_analysis,
            "rag_insights": rag_data.get("insights", {}),
            "recommendations": self._generate_recommendations(
                finance_analysis,
                goal_analysis,
                savings_analysis,
                fraud_analysis,
                pattern_analysis
            )
        }

        logger.info(f"Comprehensive report generated successfully for {user_id}")
        return comprehensive_report

    def _retrieve_financial_data_via_rag(
        self,
        user_id: str,
        start_date: date,
        end_date: date
    ) -> Dict:
        """Use RAG to retrieve and analyze all financial data"""
        try:
            # Query for spending patterns
            spending_query = f"All transactions and spending for user {user_id} between {start_date} and {end_date}"
            spending_results = self.retriever.retrieve(spending_query, top_k=50)

            # Query for budget information
            budget_query = f"Budget allocations and limits for user {user_id}"
            budget_results = self.retriever.retrieve(budget_query, top_k=20)

            # Query for goals
            goals_query = f"Financial goals and savings targets for user {user_id}"
            goals_results = self.retriever.retrieve(goals_query, top_k=20)

            # Extract insights from retrieved chunks
            insights = {
                "spending_insights": self._analyze_chunks(spending_results),
                "budget_insights": self._analyze_chunks(budget_results),
                "goal_insights": self._analyze_chunks(goals_results),
                "total_chunks_analyzed": len(spending_results) + len(budget_results) + len(goals_results)
            }

            return {
                "status": "success",
                "insights": insights,
                "spending_data": spending_results,
                "budget_data": budget_results,
                "goal_data": goals_results
            }

        except Exception as e:
            logger.error(f"Error retrieving data via RAG: {e}")
            return {
                "status": "error",
                "error": str(e),
                "insights": {}
            }

    def _analyze_chunks(self, chunks: List[Dict]) -> Dict:
        """Analyze retrieved chunks to extract key information"""
        if not chunks:
            return {"summary": "No data found"}

        # Extract metadata from chunks
        categories = set()
        total_amount = 0.0
        vendors = set()

        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            if "category" in metadata:
                categories.add(metadata["category"])
            if "amount" in metadata:
                total_amount += float(metadata.get("amount", 0))
            if "vendor" in metadata:
                vendors.add(metadata["vendor"])

        return {
            "categories": list(categories),
            "total_amount": total_amount,
            "unique_vendors": len(vendors),
            "transaction_count": len(chunks)
        }

    def _get_finance_analysis(self, user_id: str, period: str) -> Dict:
        """Get comprehensive financial analysis from Personal Finance Agent"""
        try:
            # Convert period to what the agent expects
            if period == "weekly":
                agent_period = "month"  # Use month data for weekly reports
            else:
                agent_period = period

            dashboard = self.personal_finance_agent.analyze_dashboard(user_id, agent_period)

            return {
                "total_spending": dashboard.get("total_spent", 0),
                "budget_status": dashboard.get("budget_status", {}),
                "top_categories": dashboard.get("spending_by_category", []),
                "monthly_average": dashboard.get("monthly_average", 0),
                "spending_trend": dashboard.get("trend", "stable"),
                "forecast": dashboard.get("forecast", {}),
                "insights": dashboard.get("insights", [])
            }

        except Exception as e:
            logger.error(f"Error getting finance analysis: {e}")
            return {"error": str(e)}

    def _get_goal_analysis(self, user_id: str) -> Dict:
        """Get goal progress from Goal Planner Agent"""
        try:
            # Get all goals
            goals = self.user_storage.get_goals(user_id)

            goal_progress = []
            for goal in goals:
                progress_pct = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
                goal_progress.append({
                    "id": goal.id,
                    "name": goal.name,
                    "type": goal.goal_type,
                    "target": goal.target_amount,
                    "current": goal.current_amount,
                    "progress_percentage": round(progress_pct, 2),
                    "deadline": goal.deadline.isoformat() if goal.deadline else None,
                    "status": "on_track" if progress_pct >= 50 else "behind"
                })

            return {
                "total_goals": len(goals),
                "active_goals": len([g for g in goals if g.status == "active"]),
                "completed_goals": len([g for g in goals if g.status == "completed"]),
                "goals": goal_progress
            }

        except Exception as e:
            logger.error(f"Error getting goal analysis: {e}")
            return {"error": str(e)}

    def _get_savings_opportunities(self, user_id: str, rag_data: Dict) -> Dict:
        """Identify savings opportunities using Savings Agent"""
        try:
            # Get user profile
            profile = self.user_storage.get_profile(user_id)

            # Analyze spending patterns for savings
            opportunities = self.savings_agent.identify_opportunities(
                user_id=user_id,
                spending_data=rag_data.get("spending_data", [])
            )

            return {
                "opportunities_found": len(opportunities),
                "total_potential_savings": sum(o.get("potential_savings", 0) for o in opportunities),
                "opportunities": opportunities[:5]  # Top 5
            }

        except Exception as e:
            logger.error(f"Error getting savings opportunities: {e}")
            return {"error": str(e), "opportunities": []}

    def _get_fraud_analysis(self, user_id: str) -> Dict:
        """Run fraud detection analysis"""
        try:
            # Get recent transactions from MongoDB
            recent_transactions = self.mongo_storage.get_user_receipts(
                user_id=user_id,
                limit=100
            )

            if not recent_transactions:
                return {
                    "status": "no_data",
                    "alerts": [],
                    "anomalies_detected": 0
                }

            # Analyze for fraud
            fraud_results = self.fraud_agent.detect_anomalies(
                user_id=user_id,
                transactions=recent_transactions
            )

            return {
                "status": "analyzed",
                "anomalies_detected": len(fraud_results.get("anomalies", [])),
                "alerts": fraud_results.get("alerts", []),
                "risk_score": fraud_results.get("risk_score", 0)
            }

        except Exception as e:
            logger.error(f"Error in fraud analysis: {e}")
            return {"error": str(e), "alerts": []}

    def _get_pattern_analysis(self, user_id: str) -> Dict:
        """Detect spending patterns"""
        try:
            patterns = self.pattern_agent.detect_patterns(user_id)

            return {
                "patterns_detected": len(patterns),
                "recurring_expenses": patterns.get("recurring", []),
                "trends": patterns.get("trends", []),
                "seasonality": patterns.get("seasonality", {})
            }

        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}")
            return {"error": str(e)}

    def _get_behavioral_insights(self, user_id: str) -> Dict:
        """Get behavioral spending insights"""
        try:
            insights = self.behavioral_agent.analyze_behavior(user_id)

            return {
                "spending_personality": insights.get("personality", "balanced"),
                "habits": insights.get("habits", []),
                "impulse_score": insights.get("impulse_score", 0),
                "recommendations": insights.get("recommendations", [])
            }

        except Exception as e:
            logger.error(f"Error in behavioral analysis: {e}")
            return {"error": str(e)}

    def _get_compliance_analysis(self, user_id: str, rag_data: Dict) -> Dict:
        """Check compliance with financial policies"""
        try:
            # Get recent transactions
            spending_data = rag_data.get("spending_data", [])

            if not spending_data:
                return {
                    "status": "no_data",
                    "compliant": True,
                    "violations": []
                }

            compliance_results = []
            for transaction in spending_data[:10]:  # Check top 10
                metadata = transaction.get("metadata", {})
                result = self.compliance_agent.check_compliance(
                    invoice_data=metadata,
                    user_id=user_id
                )
                if not result.get("compliant", True):
                    compliance_results.append(result)

            return {
                "status": "analyzed",
                "compliant": len(compliance_results) == 0,
                "violations": compliance_results,
                "violation_count": len(compliance_results)
            }

        except Exception as e:
            logger.error(f"Error in compliance analysis: {e}")
            return {"error": str(e)}

    def _get_audit_summary(self, user_id: str) -> Dict:
        """Generate audit summary"""
        try:
            audit_results = self.audit_agent.audit_user_data(user_id)

            return {
                "status": "completed",
                "data_quality_score": audit_results.get("quality_score", 0),
                "issues_found": audit_results.get("issues", []),
                "recommendations": audit_results.get("recommendations", [])
            }

        except Exception as e:
            logger.error(f"Error in audit: {e}")
            return {"error": str(e)}

    def _create_executive_summary(
        self,
        finance: Dict,
        goals: Dict,
        savings: Dict,
        fraud: Dict
    ) -> Dict:
        """Create executive summary of key findings"""

        # Calculate key metrics
        total_spending = finance.get("total_spending", 0)
        budget_status = finance.get("budget_status", {})
        budget_usage = budget_status.get("percentage_used", 0) if budget_status else 0

        active_goals = goals.get("active_goals", 0)
        potential_savings = savings.get("total_potential_savings", 0)
        fraud_alerts = len(fraud.get("alerts", []))

        # Determine overall financial health
        health_score = self._calculate_health_score(finance, goals, fraud)

        summary = {
            "financial_health_score": health_score,
            "total_spending": total_spending,
            "budget_usage_percentage": budget_usage,
            "active_goals": active_goals,
            "potential_savings": potential_savings,
            "fraud_alerts": fraud_alerts,
            "key_highlights": []
        }

        # Add highlights
        if budget_usage > 90:
            summary["key_highlights"].append({
                "type": "warning",
                "message": f"Budget usage at {budget_usage:.1f}% - Consider reducing spending"
            })

        if potential_savings > 0:
            summary["key_highlights"].append({
                "type": "opportunity",
                "message": f"Potential savings of ${potential_savings:.2f} identified"
            })

        if fraud_alerts > 0:
            summary["key_highlights"].append({
                "type": "alert",
                "message": f"{fraud_alerts} fraud alerts require attention"
            })

        if active_goals > 0:
            summary["key_highlights"].append({
                "type": "info",
                "message": f"Tracking {active_goals} active financial goals"
            })

        return summary

    def _calculate_health_score(self, finance: Dict, goals: Dict, fraud: Dict) -> float:
        """Calculate overall financial health score (0-100)"""
        score = 100.0

        # Deduct for budget overuse
        budget_status = finance.get("budget_status", {})
        budget_usage = budget_status.get("percentage_used", 0) if budget_status else 0
        if budget_usage > 100:
            score -= min(30, (budget_usage - 100) * 2)
        elif budget_usage > 90:
            score -= (budget_usage - 90)

        # Deduct for fraud alerts
        fraud_alerts = len(fraud.get("alerts", []))
        score -= min(20, fraud_alerts * 5)

        # Bonus for active goals
        active_goals = goals.get("active_goals", 0)
        score += min(10, active_goals * 2)

        return max(0, min(100, score))

    def _generate_recommendations(
        self,
        finance: Dict,
        goals: Dict,
        savings: Dict,
        fraud: Dict,
        patterns: Dict
    ) -> List[Dict]:
        """Generate actionable recommendations based on all analyses"""
        recommendations = []

        # Budget recommendations
        budget_usage = finance.get("budget_status", {}).get("percentage_used", 0)
        if budget_usage > 90:
            recommendations.append({
                "category": "budget",
                "priority": "high",
                "title": "Budget Alert",
                "description": "Your spending is approaching your budget limit. Consider reviewing discretionary expenses.",
                "action": "Review and reduce non-essential spending"
            })

        # Savings recommendations
        if savings.get("opportunities_found", 0) > 0:
            top_opportunity = savings.get("opportunities", [{}])[0]
            recommendations.append({
                "category": "savings",
                "priority": "medium",
                "title": "Savings Opportunity",
                "description": top_opportunity.get("description", "Potential savings identified"),
                "action": top_opportunity.get("action", "Review savings opportunities")
            })

        # Goal recommendations
        if goals.get("active_goals", 0) == 0:
            recommendations.append({
                "category": "goals",
                "priority": "medium",
                "title": "Set Financial Goals",
                "description": "You don't have any active financial goals. Setting goals can help you stay motivated.",
                "action": "Create at least one savings or investment goal"
            })

        # Fraud recommendations
        if fraud.get("anomalies_detected", 0) > 0:
            recommendations.append({
                "category": "security",
                "priority": "high",
                "title": "Unusual Activity Detected",
                "description": "Some transactions appear unusual. Please review for unauthorized charges.",
                "action": "Review recent transactions for suspicious activity"
            })

        # Pattern-based recommendations
        recurring = patterns.get("recurring_expenses", [])
        if len(recurring) > 0:
            recommendations.append({
                "category": "patterns",
                "priority": "low",
                "title": "Recurring Expenses Detected",
                "description": f"You have {len(recurring)} recurring expenses. Consider if all subscriptions are still needed.",
                "action": "Review and cancel unused subscriptions"
            })

        return recommendations


# Global instance
_report_generator = None


def get_report_generator() -> AgenticReportGenerator:
    """Get global report generator instance"""
    global _report_generator
    if _report_generator is None:
        _report_generator = AgenticReportGenerator()
    return _report_generator
