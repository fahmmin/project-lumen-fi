"""
PROJECT LUMEN - Workspace Memory Writer
Manages the persistent workspace.md memory file
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from backend.config import settings
from backend.utils.logger import logger, log_error

# Import fcntl only on Unix-like systems (not available on Windows)
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False


class WorkspaceWriter:
    """Manages workspace.md with thread-safe operations"""

    def __init__(self, workspace_path: Path = settings.WORKSPACE_FILE):
        self.workspace_path = workspace_path
        self._initialize_workspace()

    def _initialize_workspace(self):
        """Initialize workspace.md if it doesn't exist"""
        if not self.workspace_path.exists():
            header = f"""# PROJECT LUMEN WORKSPACE

**Initialized**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This file serves as persistent memory for Project LUMEN.
All document ingestion and audit operations are logged here.

---

"""
            try:
                self.workspace_path.write_text(header, encoding='utf-8')
                logger.info(f"Initialized workspace at {self.workspace_path}")
            except Exception as e:
                log_error(e, "Workspace initialization")

    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def append_entry(self, content: str) -> bool:
        """
        Append content to workspace with file locking

        Args:
            content: Content to append

        Returns:
            Success status
        """
        try:
            # Use file locking on Unix-like systems
            with open(self.workspace_path, 'a', encoding='utf-8') as f:
                # Try to lock file (Unix only)
                if HAS_FCNTL:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    except (AttributeError, OSError):
                        pass

                f.write(content)
                f.write('\n\n')

                # Unlock
                if HAS_FCNTL:
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except (AttributeError, OSError):
                        pass

            logger.info("Workspace entry added successfully")
            return True

        except Exception as e:
            log_error(e, "Workspace write")
            return False

    def log_ingestion(
        self,
        filename: str,
        extracted_fields: Dict[str, Any],
        document_id: str
    ) -> bool:
        """
        Log document ingestion to workspace

        Args:
            filename: Name of ingested file
            extracted_fields: Extracted structured data
            document_id: Unique document identifier

        Returns:
            Success status
        """
        entry = f"""### NEW DOCUMENT INGESTED
**Document ID**: {document_id}
**Filename**: {filename}
**Timestamp**: {self._get_timestamp()}
**Extracted Fields**:
- Vendor: {extracted_fields.get('vendor', 'N/A')}
- Date: {extracted_fields.get('date', 'N/A')}
- Amount: {extracted_fields.get('amount', 'N/A')}
- Tax: {extracted_fields.get('tax', 'N/A')}
- Category: {extracted_fields.get('category', 'N/A')}
- Invoice Number: {extracted_fields.get('invoice_number', 'N/A')}

---"""
        return self.append_entry(entry)

    def log_audit(
        self,
        audit_id: str,
        invoice_data: Dict[str, Any],
        findings: Dict[str, Any],
        context_chunks: list,
        explanation: str
    ) -> bool:
        """
        Log audit execution to workspace

        Args:
            audit_id: Unique audit identifier
            invoice_data: Invoice data that was audited
            findings: Audit findings from all agents
            context_chunks: RAG context chunk IDs used
            explanation: Natural language explanation

        Returns:
            Success status
        """
        # Format findings
        audit_findings = findings.get('audit', {})
        compliance_findings = findings.get('compliance', {})
        fraud_findings = findings.get('fraud', {})

        entry = f"""### [AUDIT RUN]
**Audit ID**: {audit_id}
**Timestamp**: {self._get_timestamp()}
**Invoice**: {invoice_data.get('vendor', 'Unknown')} - {invoice_data.get('invoice_number', 'N/A')}

**Findings**:

*Audit Agent*:
- Duplicates: {len(audit_findings.get('duplicates', []))}
- Mismatches: {audit_findings.get('mismatches', [])}
- Total Errors: {audit_findings.get('total_errors', [])}

*Compliance Agent*:
- Status: {compliance_findings.get('status', 'unknown')}
- Violations: {compliance_findings.get('violations', [])}

*Fraud Agent*:
- Anomaly Detected: {fraud_findings.get('anomaly_detected', False)}
- Risk Score: {fraud_findings.get('risk_score', 0.0):.2f}

**Context Retrieved**: {len(context_chunks)} chunks used
**Chunk IDs**: {context_chunks[:5] if len(context_chunks) > 5 else context_chunks}

**Summary**:
{explanation}

---"""
        return self.append_entry(entry)

    def get_content(self) -> str:
        """
        Get full workspace content

        Returns:
            Workspace content as string
        """
        try:
            return self.workspace_path.read_text(encoding='utf-8')
        except Exception as e:
            log_error(e, "Workspace read")
            return ""

    def get_recent_entries(self, n: int = 10) -> str:
        """
        Get recent entries from workspace

        Args:
            n: Number of recent entries to return

        Returns:
            Recent entries
        """
        try:
            content = self.get_content()
            # Split by section headers
            sections = content.split('###')
            # Get last n sections (skip header)
            recent = sections[-(n+1):]
            return '###'.join(recent)
        except Exception as e:
            log_error(e, "Workspace recent entries")
            return ""

    def search_workspace(self, query: str) -> str:
        """
        Search workspace for entries containing query

        Args:
            query: Search query

        Returns:
            Matching entries
        """
        try:
            content = self.get_content()
            sections = content.split('###')
            matches = [f"###{section}" for section in sections if query.lower() in section.lower()]
            return '\n\n'.join(matches)
        except Exception as e:
            log_error(e, "Workspace search")
            return ""


# Global workspace instance
workspace = WorkspaceWriter()
