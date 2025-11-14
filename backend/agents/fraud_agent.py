"""
PROJECT LUMEN - Fraud Detection Agent
Detects anomalies and potential fraud in invoices
"""

from typing import Dict, List
import numpy as np
from sklearn.ensemble import IsolationForest
from backend.rag.vector_store import get_vector_store
from backend.utils.logger import logger, log_agent_action
from backend.config import settings


class FraudAgent:
    """Detects anomalies and fraud patterns"""

    def __init__(self, z_threshold: float = settings.FRAUD_ZSCORE_THRESHOLD):
        self.z_threshold = z_threshold
        self.vector_store = get_vector_store()

    def detect_fraud(self, invoice_data: Dict) -> Dict:
        """
        Detect fraud indicators in invoice

        Args:
            invoice_data: Invoice data dictionary

        Returns:
            Fraud detection findings
        """
        logger.info(f"Fraud Agent: Analyzing {invoice_data.get('vendor', 'Unknown')}")

        findings = {
            "anomaly_detected": False,
            "risk_score": 0.0,
            "suspicious_indicators": [],
            "methods_used": []
        }

        # Method 1: Z-score analysis
        z_findings = self._zscore_analysis(invoice_data)
        if z_findings["anomaly"]:
            findings["anomaly_detected"] = True
            findings["suspicious_indicators"].extend(z_findings["indicators"])
            findings["risk_score"] = max(findings["risk_score"], z_findings["score"])
            findings["methods_used"].append("Z-Score Analysis")

        # Method 2: Isolation Forest
        if_findings = self._isolation_forest_analysis(invoice_data)
        if if_findings["anomaly"]:
            findings["anomaly_detected"] = True
            findings["suspicious_indicators"].extend(if_findings["indicators"])
            findings["risk_score"] = max(findings["risk_score"], if_findings["score"])
            findings["methods_used"].append("Isolation Forest")

        # Method 3: Pattern-based detection
        pattern_findings = self._pattern_analysis(invoice_data)
        if pattern_findings["anomaly"]:
            findings["anomaly_detected"] = True
            findings["suspicious_indicators"].extend(pattern_findings["indicators"])
            findings["risk_score"] = max(findings["risk_score"], pattern_findings["score"])
            findings["methods_used"].append("Pattern Analysis")

        log_agent_action("FraudAgent", "detect_fraud", {
            "anomaly_detected": findings["anomaly_detected"],
            "risk_score": findings["risk_score"]
        })

        return findings

    def _zscore_analysis(self, invoice_data: Dict) -> Dict:
        """
        Z-score based anomaly detection

        Args:
            invoice_data: Invoice data

        Returns:
            Z-score findings
        """
        findings = {
            "anomaly": False,
            "indicators": [],
            "score": 0.0
        }

        amount = invoice_data.get('amount', 0)
        vendor = invoice_data.get('vendor', '')
        category = invoice_data.get('category', '')

        if not amount:
            return findings

        # Get historical data
        all_chunks = self.vector_store.get_all_chunks()
        historical_amounts = []

        for chunk in all_chunks:
            metadata = chunk.get('metadata', {})
            if metadata.get('amount'):
                historical_amounts.append(metadata['amount'])

        if len(historical_amounts) < 10:  # Need sufficient data
            return findings

        # Calculate Z-score
        mean = np.mean(historical_amounts)
        std = np.std(historical_amounts)

        if std > 0:
            z_score = abs((amount - mean) / std)

            if z_score > self.z_threshold:
                findings["anomaly"] = True
                findings["indicators"].append(
                    f"Amount ${amount:.2f} is {z_score:.1f} standard deviations from mean ${mean:.2f}"
                )
                findings["score"] = min(z_score / 10.0, 1.0)  # Normalize to 0-1

        # Vendor-specific Z-score
        vendor_amounts = [
            chunk.get('metadata', {}).get('amount', 0)
            for chunk in all_chunks
            if chunk.get('metadata', {}).get('vendor') == vendor
        ]

        if len(vendor_amounts) >= 5:
            vendor_mean = np.mean(vendor_amounts)
            vendor_std = np.std(vendor_amounts)

            if vendor_std > 0:
                vendor_z_score = abs((amount - vendor_mean) / vendor_std)

                if vendor_z_score > self.z_threshold:
                    findings["anomaly"] = True
                    findings["indicators"].append(
                        f"Amount unusual for vendor '{vendor}' (Z-score: {vendor_z_score:.1f})"
                    )
                    findings["score"] = max(findings["score"], min(vendor_z_score / 10.0, 1.0))

        return findings

    def _isolation_forest_analysis(self, invoice_data: Dict) -> Dict:
        """
        Isolation Forest anomaly detection

        Args:
            invoice_data: Invoice data

        Returns:
            Isolation Forest findings
        """
        findings = {
            "anomaly": False,
            "indicators": [],
            "score": 0.0
        }

        try:
            # Get historical data
            all_chunks = self.vector_store.get_all_chunks()

            if len(all_chunks) < 20:  # Need sufficient data
                return findings

            # Extract features
            features = []
            for chunk in all_chunks:
                metadata = chunk.get('metadata', {})
                if metadata.get('amount'):
                    feature = [
                        metadata.get('amount', 0),
                        metadata.get('tax', 0),
                        hash(metadata.get('vendor', '')) % 1000,  # Vendor as numeric
                        hash(metadata.get('category', '')) % 100,  # Category as numeric
                    ]
                    features.append(feature)

            if len(features) < 20:
                return findings

            X = np.array(features)

            # Train Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            iso_forest.fit(X)

            # Predict current invoice
            current_feature = [
                invoice_data.get('amount', 0),
                invoice_data.get('tax', 0),
                hash(invoice_data.get('vendor', '')) % 1000,
                hash(invoice_data.get('category', '')) % 100,
            ]

            prediction = iso_forest.predict([current_feature])[0]
            anomaly_score = iso_forest.score_samples([current_feature])[0]

            if prediction == -1:  # Anomaly detected
                findings["anomaly"] = True
                findings["indicators"].append(
                    f"Isolation Forest detected anomaly (score: {anomaly_score:.2f})"
                )
                findings["score"] = min(abs(anomaly_score) / 2.0, 1.0)

        except Exception as e:
            logger.warning(f"Isolation Forest analysis failed: {e}")

        return findings

    def _pattern_analysis(self, invoice_data: Dict) -> Dict:
        """
        Pattern-based fraud detection

        Args:
            invoice_data: Invoice data

        Returns:
            Pattern findings
        """
        findings = {
            "anomaly": False,
            "indicators": [],
            "score": 0.0
        }

        amount = invoice_data.get('amount', 0)
        vendor = invoice_data.get('vendor', '')
        date = invoice_data.get('date', '')
        invoice_number = invoice_data.get('invoice_number', '')

        # Pattern 1: Sequential invoice numbers from same vendor on same day
        all_chunks = self.vector_store.get_all_chunks()
        same_vendor_same_day = [
            chunk for chunk in all_chunks
            if chunk.get('metadata', {}).get('vendor') == vendor and
               chunk.get('metadata', {}).get('date') == date
        ]

        if len(same_vendor_same_day) > 3:
            findings["anomaly"] = True
            findings["indicators"].append(
                f"Multiple invoices ({len(same_vendor_same_day)}) from same vendor on same day"
            )
            findings["score"] = 0.7

        # Pattern 2: Round number amounts (potential fraud flag)
        if amount > 100 and amount == int(amount) and amount % 100 == 0:
            findings["anomaly"] = True
            findings["indicators"].append(
                f"Suspiciously round amount: ${amount:.2f}"
            )
            findings["score"] = max(findings["score"], 0.4)

        # Pattern 3: Amount just below approval threshold
        approval_thresholds = [1000, 5000, 10000, 50000]
        for threshold in approval_thresholds:
            if threshold - 50 < amount < threshold:
                findings["anomaly"] = True
                findings["indicators"].append(
                    f"Amount ${amount:.2f} suspiciously close to approval threshold ${threshold}"
                )
                findings["score"] = max(findings["score"], 0.6)
                break

        # Pattern 4: Duplicate vendor names with slight variations
        vendor_lower = vendor.lower().strip()
        similar_vendors = [
            chunk.get('metadata', {}).get('vendor', '')
            for chunk in all_chunks
            if self._similar_strings(vendor_lower, chunk.get('metadata', {}).get('vendor', '').lower().strip())
        ]

        if len(set(similar_vendors)) > 2:
            findings["anomaly"] = True
            findings["indicators"].append(
                f"Multiple similar vendor names detected: {set(similar_vendors)}"
            )
            findings["score"] = max(findings["score"], 0.5)

        # Pattern 5: Missing or invalid invoice number
        if not invoice_number or invoice_number == 'N/A':
            findings["anomaly"] = True
            findings["indicators"].append("Missing invoice number")
            findings["score"] = max(findings["score"], 0.3)

        return findings

    def _similar_strings(self, s1: str, s2: str, threshold: float = 0.8) -> bool:
        """
        Check if two strings are similar

        Args:
            s1: First string
            s2: Second string
            threshold: Similarity threshold

        Returns:
            True if similar
        """
        if s1 == s2:
            return True

        # Simple Levenshtein-like similarity
        if len(s1) == 0 or len(s2) == 0:
            return False

        # Check if one is substring of other
        if s1 in s2 or s2 in s1:
            return True

        # Calculate character overlap
        set1 = set(s1)
        set2 = set(s2)
        overlap = len(set1 & set2)
        total = len(set1 | set2)

        similarity = overlap / total if total > 0 else 0
        return similarity >= threshold


# Global fraud agent instance
fraud_agent = None


def get_fraud_agent() -> FraudAgent:
    """Get global fraud agent instance"""
    global fraud_agent
    if fraud_agent is None:
        fraud_agent = FraudAgent()
    return fraud_agent
