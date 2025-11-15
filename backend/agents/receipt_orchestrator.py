"""
PROJECT LUMEN - Receipt Ingestion Orchestrator
Coordinates all agents when a receipt is added to provide comprehensive analysis
"""

from typing import Dict, List, Optional
from datetime import datetime, date

from backend.agents.audit_agent import get_audit_agent
from backend.agents.personal_finance_agent import get_personal_finance_agent
from backend.agents.goal_planner_agent import get_goal_planner_agent
from backend.agents.savings_opportunity_agent import get_savings_opportunity_agent
from backend.agents.pattern_agent import get_pattern_agent
from backend.rag.vector_store import get_vector_store
from backend.utils.email_parser import EmailReceiptParser
from backend.utils.logger import logger


class ReceiptIngestionOrchestrator:
    """
    Orchestrates the complete receipt ingestion flow:
    1. Duplicate check
    2. Parse and extract data
    3. Budget alert
    4. Goal impact analysis
    5. Savings suggestions
    6. Pattern detection
    7. Store with enriched metadata
    """

    def __init__(self):
        self.audit_agent = get_audit_agent()
        self.finance_agent = get_personal_finance_agent()
        self.goal_agent = get_goal_planner_agent()
        self.savings_agent = get_savings_opportunity_agent()
        self.pattern_agent = get_pattern_agent()
        self.vector_store = get_vector_store()
        self.email_parser = EmailReceiptParser()

    def ingest_receipt(
        self,
        receipt_text: str,
        user_id: str,
        source: str = "email"
    ) -> Dict:
        """
        Complete receipt ingestion flow with all agent analysis

        Args:
            receipt_text: Raw receipt text (email body, OCR output, etc.)
            user_id: User ID
            source: Source of receipt (email, manual, ocr)

        Returns:
            Complete analysis result with all agent insights
        """
        logger.info(f"ReceiptOrchestrator: Starting ingestion for user {user_id}")

        result = {
            "user_id": user_id,
            "source": source,
            "ingested_at": datetime.now().isoformat(),
            "steps": {},
            "alerts": [],
            "recommendations": []
        }

        # ========== STEP 1: PARSE RECEIPT ==========
        logger.info("Step 1: Parsing receipt with LLM")
        try:
            parsed = self.email_parser.parse_receipt(receipt_text)

            if not parsed or parsed.get('confidence', 0) < 0.5:
                return {
                    **result,
                    "status": "failed",
                    "error": "Could not parse receipt with sufficient confidence",
                    "steps": {"parse": {"success": False}}
                }

            receipt_data = {
                "vendor": parsed.get('vendor', 'Unknown'),
                "amount": parsed.get('amount', 0),
                "date": parsed.get('date', date.today().isoformat()),
                "category": parsed.get('category', 'other'),
                "items": parsed.get('items', []),
                "invoice_number": parsed.get('invoice_number'),
                "payment_method": parsed.get('payment_method'),
                "confidence": parsed.get('confidence', 0)
            }

            result["steps"]["parse"] = {
                "success": True,
                "data": receipt_data
            }

        except Exception as e:
            logger.error(f"Parse failed: {e}")
            return {
                **result,
                "status": "failed",
                "error": f"Parse error: {str(e)}",
                "steps": {"parse": {"success": False, "error": str(e)}}
            }

        # ========== STEP 2: DUPLICATE CHECK ==========
        logger.info("Step 2: Checking for duplicates")
        try:
            # Use AuditAgent to check duplicates
            audit_result = self.audit_agent.check_invoice({
                "vendor": receipt_data['vendor'],
                "amount": receipt_data['amount'],
                "date": receipt_data['date'],
                "invoice_number": receipt_data.get('invoice_number')
            })

            is_duplicate = any(
                finding.get('type') == 'duplicate'
                for finding in audit_result.get('findings', [])
            )

            if is_duplicate:
                return {
                    **result,
                    "status": "duplicate",
                    "message": "Receipt already exists in system",
                    "steps": {
                        "parse": result["steps"]["parse"],
                        "duplicate_check": {
                            "success": True,
                            "is_duplicate": True
                        }
                    }
                }

            result["steps"]["duplicate_check"] = {
                "success": True,
                "is_duplicate": False
            }

        except Exception as e:
            logger.warning(f"Duplicate check failed: {e}")
            # Continue anyway
            result["steps"]["duplicate_check"] = {
                "success": False,
                "error": str(e),
                "is_duplicate": False
            }

        # ========== STEP 3: BUDGET ALERT ==========
        logger.info("Step 3: Generating budget alert")
        try:
            budget_alert = self.finance_agent.check_budget_alert_on_receipt(
                user_id,
                receipt_data
            )

            result["steps"]["budget_alert"] = {
                "success": True,
                "alert": budget_alert
            }

            # Add to alerts if should notify
            if budget_alert.get('alert', {}).get('should_notify'):
                result["alerts"].append({
                    "type": "budget",
                    "level": budget_alert['alert']['alert_level'],
                    "message": budget_alert['alert']['message'],
                    "advice": budget_alert['alert']['advice']
                })

        except Exception as e:
            logger.error(f"Budget alert failed: {e}")
            result["steps"]["budget_alert"] = {
                "success": False,
                "error": str(e)
            }

        # ========== STEP 4: GOAL IMPACT ANALYSIS ==========
        logger.info("Step 4: Analyzing goal impact")
        try:
            goal_impact = self.goal_agent.analyze_receipt_impact_on_goals(
                user_id,
                receipt_data
            )

            result["steps"]["goal_impact"] = {
                "success": True,
                "analysis": goal_impact
            }

            # Add to alerts if significant impact
            impact_level = goal_impact.get('impact_analysis', {}).get('impact_level')
            if impact_level in ['high', 'medium']:
                result["alerts"].append({
                    "type": "goal_impact",
                    "level": "warning" if impact_level == "high" else "info",
                    "message": goal_impact.get('impact_analysis', {}).get('recommendation', ''),
                    "details": goal_impact.get('impact_analysis', {})
                })

        except Exception as e:
            logger.error(f"Goal impact analysis failed: {e}")
            result["steps"]["goal_impact"] = {
                "success": False,
                "error": str(e)
            }

        # ========== STEP 5: SAVINGS OPPORTUNITIES ==========
        logger.info("Step 5: Finding savings opportunities")
        try:
            savings_analysis = self.savings_agent.analyze_receipt_for_savings(
                receipt_data,
                user_id
            )

            result["steps"]["savings"] = {
                "success": True,
                "analysis": savings_analysis
            }

            # Add to recommendations if can save
            if savings_analysis.get('analysis', {}).get('can_save'):
                result["recommendations"].append({
                    "type": "savings",
                    "amount": savings_analysis['analysis'].get('savings_amount', 0),
                    "alternatives": savings_analysis['analysis'].get('alternatives', []),
                    "strategy": savings_analysis['analysis'].get('strategy', '')
                })

        except Exception as e:
            logger.error(f"Savings analysis failed: {e}")
            result["steps"]["savings"] = {
                "success": False,
                "error": str(e)
            }

        # ========== STEP 6: PATTERN DETECTION ==========
        logger.info("Step 6: Detecting patterns")
        try:
            pattern_analysis = self.pattern_agent.detect_recurring_patterns(user_id)

            result["steps"]["patterns"] = {
                "success": True,
                "analysis": pattern_analysis
            }

            # Add pattern insights to recommendations
            patterns = pattern_analysis.get('patterns', [])
            if patterns:
                result["recommendations"].append({
                    "type": "pattern",
                    "insights": patterns[:2]  # Top 2 patterns
                })

        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
            result["steps"]["patterns"] = {
                "success": False,
                "error": str(e)
            }

        # ========== STEP 7: ENRICH METADATA & STORE ==========
        logger.info("Step 7: Enriching metadata and storing")
        try:
            # Enrich with temporal and contextual data
            receipt_dt = datetime.strptime(receipt_data['date'], "%Y-%m-%d")

            enriched_metadata = {
                **receipt_data,
                "user_id": user_id,
                "source": source,
                "document_id": f"receipt_{user_id}_{datetime.now().timestamp()}",

                # Temporal enrichment
                "day_of_week": receipt_dt.strftime("%A"),
                "is_weekend": receipt_dt.weekday() >= 5,
                "time_of_month": "early" if receipt_dt.day <= 10 else "mid" if receipt_dt.day <= 20 else "late",

                # Budget context (from budget alert)
                "budget_category": receipt_data['category'],
                "budget_remaining": result["steps"].get("budget_alert", {}).get("alert", {}).get("remaining", 0),
                "budget_percent_used": result["steps"].get("budget_alert", {}).get("alert", {}).get("percent_used", 0),
                "is_over_budget": result["steps"].get("budget_alert", {}).get("alert", {}).get("alert_level") == "critical",

                # Goal context (from goal impact)
                "affects_goals": result["steps"].get("goal_impact", {}).get("analysis", {}).get("impact_analysis", {}).get("affects_goals", False),
                "goal_impact_level": result["steps"].get("goal_impact", {}).get("analysis", {}).get("impact_analysis", {}).get("impact_level", "none"),
                "is_discretionary": result["steps"].get("goal_impact", {}).get("analysis", {}).get("impact_analysis", {}).get("is_discretionary", False),

                # Savings context
                "savings_potential": result["steps"].get("savings", {}).get("analysis", {}).get("analysis", {}).get("savings_amount", 0),

                # Ingestion metadata
                "ingested_at": result["ingested_at"],
                "processing_version": "v2_orchestrated"
            }

            # Store in vector database with full text and enriched metadata
            from backend.rag.chunk_document import chunk_document

            chunks = chunk_document(
                receipt_text,
                enriched_metadata,
                chunk_size=500,
                chunk_overlap=50
            )

            self.vector_store.add_chunks(chunks)

            result["steps"]["storage"] = {
                "success": True,
                "document_id": enriched_metadata['document_id'],
                "chunks_stored": len(chunks)
            }

            result["receipt"] = {
                "document_id": enriched_metadata['document_id'],
                "vendor": receipt_data['vendor'],
                "amount": receipt_data['amount'],
                "category": receipt_data['category'],
                "date": receipt_data['date']
            }

        except Exception as e:
            logger.error(f"Storage failed: {e}")
            result["steps"]["storage"] = {
                "success": False,
                "error": str(e)
            }

        # ========== FINAL STATUS ==========
        result["status"] = "success"
        result["summary"] = self._generate_summary(result)

        logger.info(f"ReceiptOrchestrator: Ingestion complete for user {user_id}")
        return result

    def _generate_summary(self, result: Dict) -> str:
        """Generate human-readable summary of analysis"""
        receipt = result.get("receipt", {})
        alerts = result.get("alerts", [])
        recommendations = result.get("recommendations", [])

        summary_parts = []

        # Receipt recorded
        summary_parts.append(
            f"✓ Receipt recorded: {receipt.get('vendor', 'Unknown')} - ${receipt.get('amount', 0):.2f}"
        )

        # Alerts
        for alert in alerts:
            if alert['type'] == 'budget':
                summary_parts.append(f"⚠️ {alert['message']}")
            elif alert['type'] == 'goal_impact':
                summary_parts.append(f"🎯 {alert['message']}")

        # Recommendations
        for rec in recommendations[:2]:  # Top 2 recommendations
            if rec['type'] == 'savings':
                summary_parts.append(
                    f"💡 Savings tip: {rec.get('strategy', 'Consider alternatives')} (save ${rec.get('amount', 0):.2f})"
                )

        return "\n".join(summary_parts)


# Global orchestrator instance
_receipt_orchestrator = None


def get_receipt_orchestrator() -> ReceiptIngestionOrchestrator:
    """Get global receipt orchestrator instance"""
    global _receipt_orchestrator
    if _receipt_orchestrator is None:
        _receipt_orchestrator = ReceiptIngestionOrchestrator()
    return _receipt_orchestrator
