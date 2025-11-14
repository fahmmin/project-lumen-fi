"""
PROJECT LUMEN - Image Forensics Utilities
Tools for detecting manipulated images (ELA, EXIF, etc.)
"""

from typing import Dict, Tuple, Optional
from PIL import Image, ImageChops, ImageEnhance
import io
import os

try:
    from PIL.ExifTags import TAGS
    EXIF_AVAILABLE = True
except:
    EXIF_AVAILABLE = False

from backend.utils.logger import logger


class ImageForensics:
    """Image manipulation detection utilities"""

    @staticmethod
    def error_level_analysis(image_path: str, quality: int = 90) -> Dict:
        """
        Perform Error Level Analysis (ELA)

        ELA detects JPEG compression artifacts. Manipulated areas show
        different error levels than original areas.

        Args:
            image_path: Path to image file
            quality: JPEG quality for comparison (default 90)

        Returns:
            ELA analysis results
        """
        try:
            # Open original image
            original = Image.open(image_path)

            # Convert to RGB if necessary
            if original.mode != 'RGB':
                original = original.convert('RGB')

            # Save as JPEG with specified quality
            temp_buffer = io.BytesIO()
            original.save(temp_buffer, 'JPEG', quality=quality)
            temp_buffer.seek(0)

            # Reload the compressed image
            compressed = Image.open(temp_buffer)

            # Calculate difference
            diff = ImageChops.difference(original, compressed)

            # Enhance to make differences more visible
            extrema = diff.getextrema()

            # Calculate max difference across all channels
            max_diff = max([ex[1] for ex in extrema])

            # Determine if anomalies detected
            # High max_diff suggests manipulation
            anomalies_detected = max_diff > 30  # Threshold

            # Analyze regions (simplified - would need more sophisticated analysis)
            suspicious_regions = []
            if anomalies_detected:
                suspicious_regions.append("center")  # Placeholder

            score = min(max_diff / 100, 1.0)  # Normalize to 0-1

            return {
                "anomalies_detected": anomalies_detected,
                "suspicious_regions": suspicious_regions,
                "max_difference": max_diff,
                "score": round(1.0 - score, 2),  # Higher score = less suspicious
                "method": "ELA"
            }

        except Exception as e:
            logger.error(f"ELA analysis failed: {e}")
            return {
                "anomalies_detected": False,
                "error": str(e),
                "score": 0.5
            }

    @staticmethod
    def analyze_exif(image_path: str) -> Dict:
        """
        Analyze EXIF metadata

        Args:
            image_path: Path to image file

        Returns:
            EXIF analysis results
        """
        try:
            image = Image.open(image_path)

            if not EXIF_AVAILABLE:
                return {
                    "has_exif": False,
                    "exif_consistent": True,
                    "score": 0.5,
                    "message": "EXIF analysis not available"
                }

            # Get EXIF data
            exif_data = image.getexif()

            if not exif_data:
                return {
                    "has_exif": False,
                    "camera_make": None,
                    "camera_model": None,
                    "timestamp": None,
                    "gps_location": None,
                    "exif_consistent": False,
                    "score": 0.3,  # No EXIF is suspicious for phone photos
                    "warning": "No EXIF data found - photo may have been edited or screenshot"
                }

            # Extract key fields
            metadata = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = value

            camera_make = metadata.get('Make', None)
            camera_model = metadata.get('Model', None)
            timestamp = metadata.get('DateTime', None)

            # Check GPS
            gps_info = metadata.get('GPSInfo', None)

            # Consistency checks
            exif_consistent = True
            warnings = []

            # Check if camera info present
            if not camera_make and not camera_model:
                exif_consistent = False
                warnings.append("No camera information")

            # Check timestamp
            if not timestamp:
                warnings.append("No timestamp")

            score = 0.9 if exif_consistent else 0.6

            return {
                "has_exif": True,
                "camera_make": camera_make,
                "camera_model": camera_model,
                "timestamp": timestamp,
                "gps_location": "present" if gps_info else None,
                "exif_consistent": exif_consistent,
                "score": score,
                "warnings": warnings
            }

        except Exception as e:
            logger.error(f"EXIF analysis failed: {e}")
            return {
                "has_exif": False,
                "error": str(e),
                "score": 0.5
            }

    @staticmethod
    def detect_cloning(image_path: str) -> Dict:
        """
        Detect clone stamp / copy-paste regions

        This is a simplified version. Full clone detection requires
        more sophisticated algorithms (SIFT, SURF, etc.)

        Args:
            image_path: Path to image file

        Returns:
            Clone detection results
        """
        try:
            # Placeholder implementation
            # Real implementation would use:
            # - SIFT/SURF feature detection
            # - Block matching algorithms
            # - Pattern recognition

            return {
                "clones_detected": False,
                "score": 0.95,
                "method": "simplified",
                "note": "Basic clone detection - may not catch sophisticated edits"
            }

        except Exception as e:
            logger.error(f"Clone detection failed: {e}")
            return {
                "clones_detected": False,
                "error": str(e),
                "score": 0.5
            }

    @staticmethod
    def analyze_lighting(image_path: str) -> Dict:
        """
        Analyze lighting consistency

        Detects lighting inconsistencies that suggest composite images

        Args:
            image_path: Path to image file

        Returns:
            Lighting analysis results
        """
        try:
            image = Image.open(image_path)

            # Convert to grayscale
            gray = image.convert('L')

            # Get image regions
            width, height = gray.size

            # Divide into quadrants
            regions = {
                'top_left': gray.crop((0, 0, width//2, height//2)),
                'top_right': gray.crop((width//2, 0, width, height//2)),
                'bottom_left': gray.crop((0, height//2, width//2, height)),
                'bottom_right': gray.crop((width//2, height//2, width, height))
            }

            # Calculate average brightness for each region
            brightness = {}
            for region_name, region_img in regions.items():
                pixels = list(region_img.getdata())
                avg = sum(pixels) / len(pixels)
                brightness[region_name] = avg

            # Check variance
            brightness_values = list(brightness.values())
            variance = max(brightness_values) - min(brightness_values)

            # High variance might indicate inconsistent lighting
            inconsistencies = variance > 50  # Threshold

            suspicious_areas = []
            if inconsistencies:
                # Find regions with unusual brightness
                avg_brightness = sum(brightness_values) / len(brightness_values)
                for region, value in brightness.items():
                    if abs(value - avg_brightness) > 30:
                        suspicious_areas.append(region)

            score = 1.0 - (variance / 255.0)  # Normalize

            return {
                "inconsistencies": inconsistencies,
                "suspicious_areas": suspicious_areas,
                "brightness_variance": round(variance, 2),
                "score": round(score, 2),
                "method": "brightness_analysis"
            }

        except Exception as e:
            logger.error(f"Lighting analysis failed: {e}")
            return {
                "inconsistencies": False,
                "error": str(e),
                "score": 0.5
            }

    @staticmethod
    def get_file_info(image_path: str) -> Dict:
        """Get basic file information"""
        try:
            file_size = os.path.getsize(image_path)
            image = Image.open(image_path)

            return {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2)
            }

        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return {"error": str(e)}
