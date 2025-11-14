"""
Ollama LLM Client for PROJECT LUMEN
Connects to Ollama server (local or remote) for all LLM operations
"""

import os
import requests
import json
import re
from typing import Dict, Optional
from backend.config import settings
from backend.utils.logger import logger


class OllamaClient:
    """Client for Ollama LLM server"""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Ollama client

        Args:
            base_url: Ollama server URL (default: from settings)
            model: Model name (default: from settings)
        """
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

        # Remove trailing slash
        self.base_url = self.base_url.rstrip('/')

        logger.info(f"Ollama client initialized: {self.base_url} | Model: {self.model}")

    def generate(self,
                 prompt: str,
                 system_message: str = "You are a helpful assistant.",
                 temperature: float = 0.1,
                 max_tokens: int = 500) -> str:
        """
        Generate completion from prompt

        Args:
            prompt: User prompt
            system_message: System instruction
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            # Use Ollama chat API
            response = requests.post(
                f'{self.base_url}/api/chat',
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return data['message']['content']
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise Exception(
                f"Cannot connect to Ollama server at {self.base_url}. "
                f"Make sure Ollama is running on your GPU computer and accessible from this network."
            )
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout")
            raise Exception("Ollama request timed out. The model might be loading or the prompt is too long.")
        except Exception as e:
            logger.error(f"Ollama generation error: {str(e)}")
            raise

    def parse_json_response(self, response: str) -> Optional[Dict]:
        """
        Extract JSON from LLM response (handles markdown code blocks)

        Args:
            response: LLM response text

        Returns:
            Parsed JSON dict or None if invalid
        """
        try:
            # Try direct parsing first
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try extracting JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding JSON object in text
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning(f"Could not extract JSON from response: {response[:100]}...")
        return None

    def health_check(self) -> Dict[str, any]:
        """
        Check if Ollama service is healthy and model is available

        Returns:
            Health status dict
        """
        try:
            # Check if server is reachable
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)

            if response.status_code != 200:
                return {
                    "status": "unhealthy",
                    "error": f"Server returned {response.status_code}",
                    "base_url": self.base_url
                }

            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [m.get('name') for m in models]

            if self.model not in model_names:
                return {
                    "status": "model_not_found",
                    "error": f"Model '{self.model}' not found",
                    "available_models": model_names,
                    "base_url": self.base_url
                }

            # Test generation
            test_response = self.generate("Say 'OK'", max_tokens=10)

            return {
                "status": "healthy",
                "base_url": self.base_url,
                "model": self.model,
                "response_preview": test_response[:50],
                "available_models": model_names
            }

        except requests.exceptions.ConnectionError:
            return {
                "status": "connection_failed",
                "error": f"Cannot connect to {self.base_url}",
                "base_url": self.base_url,
                "help": "Make sure Ollama is running on your GPU computer and the firewall allows connections"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "base_url": self.base_url
            }


# Global instance
ollama_client = OllamaClient()


# Convenience functions
def generate_completion(prompt: str, system_message: str = "You are a helpful assistant.", **kwargs) -> str:
    """Generate completion using default Ollama client"""
    return ollama_client.generate(prompt, system_message, **kwargs)


def parse_json_completion(prompt: str, system_message: str = "You are a helpful assistant.", **kwargs) -> Optional[Dict]:
    """Generate and parse JSON completion"""
    response = ollama_client.generate(prompt, system_message, **kwargs)
    return ollama_client.parse_json_response(response)
