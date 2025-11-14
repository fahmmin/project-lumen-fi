"""
PROJECT LUMEN - Text Extraction Utilities
Extract text from PDFs and images
"""

import io
from pathlib import Path
from typing import Union, Tuple
from PIL import Image
import pytesseract
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from backend.utils.logger import logger, log_error


class TextExtractor:
    """Handles text extraction from various document types"""

    @staticmethod
    def extract_from_pdf(file_path: Union[str, Path, io.BytesIO]) -> Tuple[str, bool]:
        """
        Extract text from PDF file

        Args:
            file_path: Path to PDF file or BytesIO object

        Returns:
            Tuple of (extracted_text, success)
        """
        try:
            if isinstance(file_path, io.BytesIO):
                text = extract_text(file_path)
            else:
                text = extract_text(str(file_path))

            # Clean up text
            text = text.strip()

            if not text:
                logger.warning("PDF text extraction returned empty string")
                return "", False

            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text, True

        except PDFSyntaxError as e:
            log_error(e, "PDF syntax error during extraction")
            return "", False
        except Exception as e:
            log_error(e, "PDF text extraction")
            return "", False

    @staticmethod
    def extract_from_image(file_path: Union[str, Path, io.BytesIO]) -> Tuple[str, bool]:
        """
        Extract text from image using OCR

        Args:
            file_path: Path to image file or BytesIO object

        Returns:
            Tuple of (extracted_text, success)
        """
        try:
            # Load image
            if isinstance(file_path, io.BytesIO):
                image = Image.open(file_path)
            else:
                image = Image.open(str(file_path))

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Perform OCR
            text = pytesseract.image_to_string(image)

            # Clean up text
            text = text.strip()

            if not text:
                logger.warning("OCR returned empty string")
                return "", False

            logger.info(f"Successfully extracted {len(text)} characters from image")
            return text, True

        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract OCR not found. Please install Tesseract.")
            return "", False
        except Exception as e:
            log_error(e, "Image text extraction")
            return "", False

    @staticmethod
    def extract_text(file_path: Union[str, Path, io.BytesIO], file_extension: str = None) -> Tuple[str, bool]:
        """
        Extract text from file (auto-detect type)

        Args:
            file_path: Path to file or BytesIO object
            file_extension: File extension (e.g., '.pdf', '.png')

        Returns:
            Tuple of (extracted_text, success)
        """
        try:
            # Determine file type
            if file_extension is None and not isinstance(file_path, io.BytesIO):
                file_extension = Path(file_path).suffix.lower()

            if not file_extension:
                logger.error("Could not determine file type")
                return "", False

            # Route to appropriate extractor
            if file_extension == '.pdf':
                return TextExtractor.extract_from_pdf(file_path)
            elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                return TextExtractor.extract_from_image(file_path)
            else:
                logger.error(f"Unsupported file type: {file_extension}")
                return "", False

        except Exception as e:
            log_error(e, "Text extraction routing")
            return "", False

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]

        # Rejoin with single newlines
        cleaned = '\n'.join(lines)

        # Remove excessive spaces
        import re
        cleaned = re.sub(r' +', ' ', cleaned)

        return cleaned


# Convenience functions
def extract_text(file_path: Union[str, Path, io.BytesIO], file_extension: str = None) -> str:
    """
    Extract and clean text from file

    Args:
        file_path: Path to file or BytesIO object
        file_extension: File extension

    Returns:
        Cleaned extracted text
    """
    text, success = TextExtractor.extract_text(file_path, file_extension)
    if success:
        return TextExtractor.clean_text(text)
    return ""
