"""
PROJECT LUMEN - Agent Orchestrator
Coordinates all agents for comprehensive audit
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from backend.agents.audit_agent import get_audit_agent
from backend.agents.compliance_agent import get_compliance_agent
from backend.agents.fraud_agent import get_fraud_agent
from backend.agents.explainability_agent import get_explainability_agent
from backend.utils.workspace_writer import workspace
from backend.utils.logger import logger, log_operation


class AuditOrchestrator:
    """Orchestrates the multi-agent audit process"""

    def __init__(self):
        self.audit_agent = get_audit_agent()
        self.compliance_agent = get_compliance_agent()
        self.fraud_agent = get_fraud_agent()
        self.explainability_agent = get_explainability_agent()

    def run_audit(self, invoice_data: Dict, user_id: Optional[str] = None) -> Dict:
        """
        Run complete audit using all agents

        Process:
        1. Audit Agent - Check duplicates, patterns, totals
        2. Compliance Agent - Validate against policies (uses RAG)
        3. Fraud Agent - Detect anomalies
        4. Explainability Agent - Generate human-readable summary
        5. Log to workspace.md
        6. Save to MongoDB

        Args:
            invoice_data: Invoice data dictionary
            user_id: Optional user ID for MongoDB storage

        Returns:
            Complete audit report
        """
        audit_id = f"audit_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()

        logger.info(f"=== Starting Audit {audit_id} ===")
        log_operation("AUDIT_START", {
            "audit_id": audit_id,
            "vendor": invoice_data.get('vendor', 'Unknown'),
            "amount": invoice_data.get('amount', 0)
        })

        # Initialize results
        audit_report = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "invoice_data": invoice_data,
            "findings": {},
            "explanation": "",
            "context_chunks": [],
            "overall_status": "pass"
        }

        try:
            # Step 1: Audit Agent
            logger.info("Step 1/4: Running Audit Agent...")
            audit_findings = self.audit_agent.audit(invoice_data)
            audit_report["findings"]["audit"] = audit_findings

            # Update overall status based on audit
            if audit_findings.get("status") == "error":
                audit_report["overall_status"] = "error"
            elif audit_findings.get("status") == "warning":
                audit_report["overall_status"] = "warning"

            # Step 2: Compliance Agent
            logger.info("Step 2/4: Running Compliance Agent...")
            compliance_findings = self.compliance_agent.check_compliance(invoice_data)
            audit_report["findings"]["compliance"] = compliance_findings

            # Collect context chunks from compliance check
            context_chunks = compliance_findings.get("context_used", [])
            audit_report["context_chunks"] = context_chunks

            # Update overall status based on compliance
            if not compliance_findings.get("compliant", True):
                if audit_report["overall_status"] == "pass":
                    audit_report["overall_status"] = "warning"

            # Step 3: Fraud Agent
            logger.info("Step 3/4: Running Fraud Agent...")
            fraud_findings = self.fraud_agent.detect_fraud(invoice_data)
            audit_report["findings"]["fraud"] = fraud_findings

            # Update overall status based on fraud detection
            if fraud_findings.get("anomaly_detected", False):
                risk_score = fraud_findings.get("risk_score", 0.0)
                if risk_score > 0.7:
                    audit_report["overall_status"] = "error"
                elif risk_score > 0.4:
                    if audit_report["overall_status"] == "pass":
                        audit_report["overall_status"] = "warning"

            # Step 4: Explainability Agent
            logger.info("Step 4/4: Running Explainability Agent...")

            # Get actual context chunks for explanation
            context_chunk_objs = self._get_context_chunks(context_chunks)

            explanation = self.explainability_agent.explain(
                audit_report["findings"],
                context_chunk_objs
            )
            audit_report["explanation"] = explanation

            # Step 5: Log to workspace
            logger.info("Logging audit to workspace...")
            workspace.log_audit(
                audit_id=audit_id,
                invoice_data=invoice_data,
                findings=audit_report["findings"],
                context_chunks=context_chunks,
                explanation=explanation
            )

            logger.info(f"=== Audit {audit_id} Completed: {audit_report['overall_status'].upper()} ===")
            log_operation("AUDIT_COMPLETE", {
                "audit_id": audit_id,
                "status": audit_report["overall_status"],
                "issues": self._count_issues(audit_report["findings"])
            })

            # Save to MongoDB (silently, don't fail if MongoDB unavailable)
            try:
                logger.info(f"[Orchestrator] Attempting to save audit {audit_id} to MongoDB (user_id: {user_id})")
                from backend.utils.mongo_storage import get_mongo_storage
                mongo_storage = get_mongo_storage()
                amount = invoice_data.get('amount', 0.0)
                logger.debug(f"[Orchestrator] MongoDB storage initialized, amount: {amount}")
                success = mongo_storage.save_audit(
                    audit_id=audit_id,
                    audit_report=audit_report,
                    amount=amount,
                    user_id=user_id
                )
                if success:
                    logger.info(f"[Orchestrator] Successfully saved audit {audit_id} to MongoDB")
                else:
                    logger.warning(f"[Orchestrator] Failed to save audit {audit_id} to MongoDB (returned False)")
            except Exception as mongo_error:
                # Silently fail - MongoDB is optional
                logger.warning(f"[Orchestrator] MongoDB save failed (non-critical): {mongo_error}", exc_info=True)

        except Exception as e:
            logger.error(f"Error during audit {audit_id}: {e}", exc_info=True)
            audit_report["overall_status"] = "error"
            audit_report["explanation"] = f"Audit encountered an error: {str(e)}"

        return audit_report

    def run_partial_audit(self, invoice_data: Dict, agents: List[str], user_id: Optional[str] = None) -> Dict:
        """
        Run audit with selected agents only

        Args:
            invoice_data: Invoice data
            agents: List of agent names to run (e.g., ['audit', 'compliance'])
            user_id: Optional user ID for MongoDB storage

        Returns:
            Partial audit report
        """
        audit_id = f"audit_partial_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()

        logger.info(f"Running partial audit {audit_id} with agents: {agents}")

        audit_report = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "invoice_data": invoice_data,
            "findings": {},
            "agents_used": agents,
            "overall_status": "pass"
        }

        try:
            if 'audit' in agents:
                audit_findings = self.audit_agent.audit(invoice_data)
                audit_report["findings"]["audit"] = audit_findings

            if 'compliance' in agents:
                compliance_findings = self.compliance_agent.check_compliance(invoice_data)
                audit_report["findings"]["compliance"] = compliance_findings

            if 'fraud' in agents:
                fraud_findings = self.fraud_agent.detect_fraud(invoice_data)
                audit_report["findings"]["fraud"] = fraud_findings

            # Determine status
            for agent_findings in audit_report["findings"].values():
                if isinstance(agent_findings, dict):
                    if agent_findings.get("status") == "error":
                        audit_report["overall_status"] = "error"
                    elif agent_findings.get("status") == "warning" and audit_report["overall_status"] == "pass":
                        audit_report["overall_status"] = "warning"

            # Save to MongoDB (silently, don't fail if MongoDB unavailable)
            try:
                logger.info(f"[Orchestrator] Attempting to save audit {audit_id} to MongoDB (user_id: {user_id})")
                from backend.utils.mongo_storage import get_mongo_storage
                mongo_storage = get_mongo_storage()
                amount = invoice_data.get('amount', 0.0)
                logger.debug(f"[Orchestrator] MongoDB storage initialized, amount: {amount}")
                success = mongo_storage.save_audit(
                    audit_id=audit_id,
                    audit_report=audit_report,
                    amount=amount,
                    user_id=user_id
                )
                if success:
                    logger.info(f"[Orchestrator] Successfully saved audit {audit_id} to MongoDB")
                else:
                    logger.warning(f"[Orchestrator] Failed to save audit {audit_id} to MongoDB (returned False)")
            except Exception as mongo_error:
                # Silently fail - MongoDB is optional
                logger.warning(f"[Orchestrator] MongoDB save failed (non-critical): {mongo_error}", exc_info=True)

        except Exception as e:
            logger.error(f"Error during partial audit: {e}", exc_info=True)
            audit_report["overall_status"] = "error"

        return audit_report

    def _get_context_chunks(self, chunk_ids: List) -> List[Dict]:
        """
        Retrieve actual chunk objects from IDs

        Args:
            chunk_ids: List of chunk IDs

        Returns:
            List of chunk dictionaries
        """
        from backend.rag.vector_store import get_vector_store

        vector_store = get_vector_store()
        chunks = []

        for chunk_id in chunk_ids[:5]:  # Limit to 5 chunks
            if isinstance(chunk_id, int):
                chunk = vector_store.get_chunk_by_id(chunk_id)
                if chunk:
                    chunks.append(chunk)

        return chunks

    def _count_issues(self, findings: Dict) -> int:
        """
        Count total issues across all findings

        Args:
            findings: Findings dictionary

        Returns:
            Total issue count
        """
        count = 0

        audit_findings = findings.get('audit', {})
        count += len(audit_findings.get('duplicates', []))
        count += len(audit_findings.get('mismatches', []))
        count += len(audit_findings.get('total_errors', []))
        count += len(audit_findings.get('anomalies', []))

        compliance_findings = findings.get('compliance', {})
        count += len(compliance_findings.get('violations', []))

        fraud_findings = findings.get('fraud', {})
        if fraud_findings.get('anomaly_detected', False):
            count += len(fraud_findings.get('suspicious_indicators', []))

        return count


# Global orchestrator instance
orchestrator = None


def get_orchestrator() -> AuditOrchestrator:
    """Get global orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = AuditOrchestrator()
    return orchestrator


def run_audit(invoice_data: Dict, user_id: Optional[str] = None) -> Dict:
    """
    Run complete audit

    Args:
        invoice_data: Invoice data
        user_id: Optional user ID for MongoDB storage

    Returns:
        Audit report
    """
    orch = get_orchestrator()
    return orch.run_audit(invoice_data, user_id=user_id)
