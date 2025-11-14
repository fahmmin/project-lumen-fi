"""
PROJECT LUMEN - Forensics Agent
Detects image manipulation and authenticity
"""

from typing import Dict
from backend.utils.image_forensics import ImageForensics
from backend.utils.logger import logger


class ForensicsAgent:
    """Image authenticity detection agent"""

    def __init__(self):
        self.forensics = ImageForensics()

    def analyze_image(self, image_path: str) -> Dict:
        """
        Comprehensive image authenticity analysis

        Args:
            image_path: Path to image file

        Returns:
            Complete authenticity analysis
        """
        logger.info(f"ForensicsAgent: Analyzing {image_path}")

        # Get file info
        file_info = self.forensics.get_file_info(image_path)

        # Run all analyses
        ela_results = self.forensics.error_level_analysis(image_path)
        exif_results = self.forensics.analyze_exif(image_path)
        clone_results = self.forensics.detect_cloning(image_path)
        lighting_results = self.forensics.analyze_lighting(image_path)

        # Aggregate scores (weighted average)
        scores = {
            'ela': (ela_results.get('score', 0.5), 0.30),  # 30% weight
            'exif': (exif_results.get('score', 0.5), 0.25),  # 25% weight
            'clone': (clone_results.get('score', 0.5), 0.25),  # 25% weight
            'lighting': (lighting_results.get('score', 0.5), 0.20)  # 20% weight
        }

        total_score = sum(score * weight for score, weight in scores.values())
        confidence = round(total_score, 2)

        # Determine verdict
        if confidence >= 0.80:
            authentic = True
            verdict = "likely_authentic"
            risk_score = round(1.0 - confidence, 2)
        elif confidence >= 0.60:
            authentic = True
            verdict = "possibly_authentic"
            risk_score = round(1.0 - confidence, 2)
        elif confidence >= 0.40:
            authentic = False
            verdict = "possibly_manipulated"
            risk_score = round(1.0 - confidence, 2)
        else:
            authentic = False
            verdict = "likely_manipulated"
            risk_score = round(1.0 - confidence, 2)

        # Collect manipulation indicators
        indicators = []

        if ela_results.get('anomalies_detected'):
            indicators.append(
                f"ELA detected anomalies in {', '.join(ela_results.get('suspicious_regions', ['unknown areas']))}"
            )

        if not exif_results.get('exif_consistent'):
            indicators.append("EXIF data missing or inconsistent")

        if clone_results.get('clones_detected'):
            indicators.append("Clone stamp/copy-paste detected")

        if lighting_results.get('inconsistencies'):
            areas = lighting_results.get('suspicious_areas', [])
            if areas:
                indicators.append(f"Lighting inconsistencies in {', '.join(areas)}")

        if not indicators:
            indicators.append("No obvious manipulation detected")

        # Generate recommendation
        if risk_score > 0.6:
            recommendation = "REJECT - High risk of manipulation detected"
        elif risk_score > 0.4:
            recommendation = "Manual review recommended - moderate manipulation detected"
        elif risk_score > 0.2:
            recommendation = "CAUTION - Minor inconsistencies detected"
        else:
            recommendation = "ACCEPT - Image appears authentic"

        return {
            "status": "success",
            "file_info": file_info,
            "authenticity": {
                "authentic": authentic,
                "confidence": confidence,
                "risk_score": risk_score,
                "verdict": verdict
            },
            "analysis": {
                "ela_analysis": ela_results,
                "exif_analysis": exif_results,
                "clone_detection": clone_results,
                "lighting_analysis": lighting_results
            },
            "manipulation_indicators": indicators,
            "recommendation": recommendation
        }


# Global agent instance
_forensics_agent = None


def get_forensics_agent() -> ForensicsAgent:
    """Get global forensics agent instance"""
    global _forensics_agent
    if _forensics_agent is None:
        _forensics_agent = ForensicsAgent()
    return _forensics_agent
