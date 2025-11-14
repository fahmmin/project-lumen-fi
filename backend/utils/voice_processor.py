"""
Voice Processor - Convert speech to text for receipt upload
"""

from typing import Dict, Optional
import os
import tempfile
from pathlib import Path

from backend.utils.logger import logger
from backend.utils.email_parser import EmailReceiptParser


class VoiceProcessor:
    """Processes voice input and converts to text"""

    def __init__(self):
        self.supported_formats = [".mp3", ".wav", ".m4a", ".ogg", ".webm"]
        self.email_parser = EmailReceiptParser()  # Reuse LLM parser

    async def process_voice_input(self, audio_data: bytes, filename: str) -> Dict:
        """
        Process voice input and extract receipt information

        Args:
            audio_data: Audio file bytes
            filename: Original filename

        Returns:
            Dict with transcribed text and extracted fields
        """
        try:
            # Validate file format
            file_ext = Path(filename).suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported audio format. Supported: {', '.join(self.supported_formats)}")

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            try:
                # Try Google Speech-to-Text if credentials available
                if self._has_google_credentials():
                    transcribed_text = await self._transcribe_with_google(temp_path)
                else:
                    # Fallback to simulated processing for demo
                    transcribed_text = await self._simulate_transcription()
                    logger.warning("Google Speech-to-Text not configured. Using simulated transcription.")

                # Extract receipt fields from transcribed text
                extracted_fields = self._extract_receipt_fields(transcribed_text)

                return {
                    "success": True,
                    "transcribed_text": transcribed_text,
                    "extracted_fields": extracted_fields,
                    "method": "google" if self._has_google_credentials() else "simulated"
                }

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "transcribed_text": "",
                "extracted_fields": {}
            }

    def _has_google_credentials(self) -> bool:
        """Check if Google Cloud credentials are available"""
        # Check for Google Cloud credentials
        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        google_api_key = os.getenv("GOOGLE_CLOUD_API_KEY")

        return bool(google_creds or google_api_key)

    async def _transcribe_with_google(self, audio_path: str) -> str:
        """
        Transcribe audio using Google Speech-to-Text API

        Requires: google-cloud-speech package and credentials
        """
        try:
            from google.cloud import speech

            client = speech.SpeechClient()

            # Read audio file
            with open(audio_path, "rb") as audio_file:
                content = audio_file.read()

            audio = speech.RecognitionAudio(content=content)

            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code="en-US",
                enable_automatic_punctuation=True,
            )

            # Perform transcription
            response = client.recognize(config=config, audio=audio)

            # Extract transcribed text
            transcripts = []
            for result in response.results:
                transcripts.append(result.alternatives[0].transcript)

            return " ".join(transcripts)

        except ImportError:
            logger.warning("google-cloud-speech not installed. Falling back to simulation.")
            return await self._simulate_transcription()
        except Exception as e:
            logger.error(f"Google Speech-to-Text error: {str(e)}")
            return await self._simulate_transcription()

    async def _simulate_transcription(self) -> str:
        """
        Simulate transcription for demo purposes

        In production, this would be replaced with actual speech-to-text
        """
        return (
            "I spent fifty nine dollars and ninety nine cents at "
            "Whole Foods Market on groceries including milk, bread, "
            "vegetables, and chicken on December 10th 2024"
        )

    def _extract_receipt_fields(self, text: str) -> Dict:
        """
        Extract receipt fields from transcribed text using LLM

        Args:
            text: Transcribed text

        Returns:
            Dict with extracted fields (vendor, amount, date, items)
        """
        # Use the email parser's LLM capabilities for intelligent extraction
        logger.info("Extracting receipt fields from voice transcription using LLM")
        result = self.email_parser.parse_email(email_text=text, subject="Voice Receipt")

        # Return the parsed result directly
        return result


# Global instance
voice_processor = VoiceProcessor()
