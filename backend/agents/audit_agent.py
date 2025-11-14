"""
PROJECT LUMEN - Audit Agent
Performs financial audit checks on invoices
"""

from typing import Dict, List
import statistics
from backend.rag.vector_store import get_vector_store
from backend.utils.logger import logger, log_agent_action
from backend.config import settings


class AuditAgent:
    """Performs audit checks on invoice data"""

    def __init__(self, threshold: float = settings.AUDIT_THRESHOLD):
        self.threshold = threshold
        self.vector_store = get_vector_store()

    def audit(self, invoice_data: Dict) -> Dict:
        """
        Perform comprehensive audit on invoice

        Args:
            invoice_data: Invoice data dictionary

        Returns:
            Audit findings
        """
        logger.info(f"Audit Agent: Auditing invoice for {invoice_data.get('vendor', 'Unknown')}")

        findings = {
            "duplicates": [],
            "mismatches": [],
            "total_errors": [],
            "anomalies": [],
            "status": "pass"
        }

        # Check 1: Duplicate invoices
        duplicates = self._check_duplicates(invoice_data)
        if duplicates:
            findings["duplicates"] = duplicates
            findings["status"] = "warning"

        # Check 2: Vendor pattern analysis
        mismatches = self._check_vendor_patterns(invoice_data)
        if mismatches:
            findings["mismatches"] = mismatches
            findings["status"] = "warning"

        # Check 3: Total verification
        total_errors = self._check_totals(invoice_data)
        if total_errors:
            findings["total_errors"] = total_errors
            findings["status"] = "error"

        # Check 4: Amount anomalies
        anomalies = self._check_amount_anomalies(invoice_data)
        if anomalies:
            findings["anomalies"] = anomalies
            findings["status"] = "warning"

        log_agent_action("AuditAgent", "audit", {"status": findings["status"], "issues": len(findings["duplicates"]) + len(findings["mismatches"])})

        return findings

    def _check_duplicates(self, invoice_data: Dict) -> List[str]:
        """
        Check for duplicate invoices

        Args:
            invoice_data: Invoice data

        Returns:
            List of duplicate warnings
        """
        duplicates = []

        # Search for similar invoices by invoice number
        invoice_number = invoice_data.get('invoice_number', '')
        if invoice_number and invoice_number != 'N/A':
            # Search in vector store metadata
            # This is a simplified check - in production, you'd have a dedicated invoice DB
            all_chunks = self.vector_store.get_all_chunks()
            for chunk in all_chunks:
                metadata = chunk.get('metadata', {})
                if metadata.get('invoice_number') == invoice_number:
                    duplicates.append(f"Possible duplicate: Invoice {invoice_number} already exists")
                    break

        # Check for same vendor + amount + date combination
        vendor = invoice_data.get('vendor', '')
        amount = invoice_data.get('amount', 0)
        date = invoice_data.get('date', '')

        if vendor and amount and date:
            all_chunks = self.vector_store.get_all_chunks()
            for chunk in all_chunks:
                metadata = chunk.get('metadata', {})
                if (metadata.get('vendor') == vendor and
                    abs(metadata.get('amount', 0) - amount) < 0.01 and
                    metadata.get('date') == date):
                    duplicates.append(f"Possible duplicate: Same vendor, amount, and date found")
                    break

        return duplicates

    def _check_vendor_patterns(self, invoice_data: Dict) -> List[str]:
        """
        Check if invoice matches vendor patterns

        Args:
            invoice_data: Invoice data

        Returns:
            List of mismatch warnings
        """
        mismatches = []

        vendor = invoice_data.get('vendor', '')
        amount = invoice_data.get('amount', 0)
        category = invoice_data.get('category', '')

        if not vendor or not amount:
            return mismatches

        # Get historical data for this vendor
        vendor_history = self._get_vendor_history(vendor)

        if len(vendor_history) >= 3:  # Need sufficient history
            # Check amount deviation
            historical_amounts = [h['amount'] for h in vendor_history]
            mean_amount = statistics.mean(historical_amounts)
            std_amount = statistics.stdev(historical_amounts) if len(historical_amounts) > 1 else 0

            if std_amount > 0:
                deviation = abs(amount - mean_amount) / std_amount
                if deviation > 2:  # More than 2 standard deviations
                    mismatches.append(
                        f"Amount ${amount:.2f} deviates significantly from vendor average ${mean_amount:.2f}"
                    )

            # Check category consistency
            historical_categories = [h['category'] for h in vendor_history if h.get('category')]
            if historical_categories:
                most_common_category = max(set(historical_categories), key=historical_categories.count)
                if category and category != most_common_category:
                    mismatches.append(
                        f"Category '{category}' differs from typical '{most_common_category}' for this vendor"
                    )

        return mismatches

    def _check_totals(self, invoice_data: Dict) -> List[str]:
        """
        Verify invoice totals

        Args:
            invoice_data: Invoice data

        Returns:
            List of total errors
        """
        errors = []

        amount = invoice_data.get('amount', 0)
        tax = invoice_data.get('tax', 0)
        items = invoice_data.get('items', [])

        # Check if items total matches invoice total
        if items:
            items_total = sum(item.get('total', 0) for item in items)
            expected_total = items_total + tax

            if abs(amount - expected_total) > 0.01:  # Allow 1 cent rounding
                errors.append(
                    f"Total mismatch: Invoice total ${amount:.2f} != Items total ${items_total:.2f} + Tax ${tax:.2f} = ${expected_total:.2f}"
                )

        # Check tax calculation (uses configurable common tax rates)
        if items and tax > 0:
            items_subtotal = sum(item.get('total', 0) for item in items)
            if items_subtotal > 0:
                tax_rate = tax / items_subtotal
                # Use configurable common tax rates from settings
                common_rates = settings.COMMON_TAX_RATES
                if not any(abs(tax_rate - rate) < 0.01 for rate in common_rates):
                    expected_rates_str = ', '.join([f"{r*100:.0f}%" for r in common_rates])
                    errors.append(
                        f"Unusual tax rate: {tax_rate*100:.1f}% (expected common rates: {expected_rates_str})"
                    )

        return errors

    def _check_amount_anomalies(self, invoice_data: Dict) -> List[str]:
        """
        Check for amount anomalies

        Args:
            invoice_data: Invoice data

        Returns:
            List of anomaly warnings
        """
        anomalies = []

        amount = invoice_data.get('amount', 0)
        category = invoice_data.get('category', '')

        # Get historical data for this category
        category_history = self._get_category_history(category)

        if len(category_history) >= 5:  # Need sufficient history
            historical_amounts = [h['amount'] for h in category_history]
            mean_amount = statistics.mean(historical_amounts)

            # Check if amount is significantly higher than average
            if amount > mean_amount * 2:
                anomalies.append(
                    f"Amount ${amount:.2f} is unusually high for category '{category}' (avg: ${mean_amount:.2f})"
                )

        # Check for round numbers (potential red flag)
        if amount > 100 and amount == int(amount):
            anomalies.append(f"Amount ${amount:.2f} is a suspiciously round number")

        return anomalies

    def _get_vendor_history(self, vendor: str) -> List[Dict]:
        """Get historical data for vendor"""
        history = []
        all_chunks = self.vector_store.get_all_chunks()

        for chunk in all_chunks:
            metadata = chunk.get('metadata', {})
            if metadata.get('vendor') == vendor:
                history.append(metadata)

        return history

    def _get_category_history(self, category: str) -> List[Dict]:
        """Get historical data for category"""
        history = []
        all_chunks = self.vector_store.get_all_chunks()

        for chunk in all_chunks:
            metadata = chunk.get('metadata', {})
            if metadata.get('category') == category:
                history.append(metadata)

        return history


# Global audit agent instance
audit_agent = None


def get_audit_agent() -> AuditAgent:
    """Get global audit agent instance"""
    global audit_agent
    if audit_agent is None:
        audit_agent = AuditAgent()
    return audit_agent
