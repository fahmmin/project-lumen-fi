"""
API Orchestrator - Executes Internal API Calls
Makes internal HTTP requests to FastAPI endpoints without modifying existing code
"""

from typing import Dict, Any, Optional
import httpx
from fastapi import status

from backend.agents.api_registry import EndpointSchema
from backend.config import settings
from backend.utils.logger import logger


class APIOrchestrator:
    """
    Orchestrates internal API calls based on intent and extracted parameters
    Makes HTTP requests to FastAPI endpoints
    """

    def __init__(self):
        """Initialize API orchestrator"""
        self.base_url = f"http://{settings.API_HOST}:{settings.API_PORT}"
        self.timeout = 30.0  # 30 seconds timeout

    async def execute_endpoint(
        self,
        endpoint: EndpointSchema,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute REAL API endpoint with given parameters

        Args:
            endpoint: Endpoint schema
            parameters: Extracted parameters

        Returns:
            Dict with:
              - success: bool
              - status_code: int
              - data: REAL Response data from API
              - error: Error message if failed
        """
        logger.info(f"🔵 CALLING REAL API: {endpoint.method} {endpoint.path}")
        logger.info(f"Parameters: {parameters}")

        try:
            # Build request
            url, params, json_body, headers = self._build_request(endpoint, parameters)

            logger.info(f"Full URL: {url}")
            logger.info(f"Query params: {params}")
            logger.info(f"JSON body: {json_body}")

            # Make REAL HTTP request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if endpoint.method == "GET":
                    logger.info(f"Making GET request to {url}")
                    response = await client.get(url, params=params, headers=headers)
                elif endpoint.method == "POST":
                    logger.info(f"Making POST request to {url}")
                    response = await client.post(url, params=params, json=json_body, headers=headers)
                elif endpoint.method == "PUT":
                    logger.info(f"Making PUT request to {url}")
                    response = await client.put(url, params=params, json=json_body, headers=headers)
                elif endpoint.method == "DELETE":
                    logger.info(f"Making DELETE request to {url}")
                    response = await client.delete(url, params=params, headers=headers)
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported HTTP method: {endpoint.method}"
                    }

            logger.info(f"API Response Status: {response.status_code}")
            logger.info(f"API Response Text: {response.text[:500]}")  # First 500 chars

            # Parse REAL response
            result = self._parse_response(response)
            logger.info(f"Parsed result success: {result.get('success')}")

            return result

        except httpx.TimeoutException:
            logger.error(f"Request timeout for {endpoint.path}")
            return {
                "success": False,
                "error": "Request timed out. The operation is taking longer than expected."
            }
        except httpx.RequestError as e:
            logger.error(f"Request error for {endpoint.path}: {e}")
            return {
                "success": False,
                "error": f"Failed to connect to the service: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error executing endpoint {endpoint.path}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"An unexpected error occurred: {str(e)}"
            }

    def _build_request(
        self,
        endpoint: EndpointSchema,
        parameters: Dict[str, Any]
    ) -> tuple:
        """
        Build request components (URL, params, body, headers)

        Returns:
            tuple: (url, query_params, json_body, headers)
        """
        # Start with base path
        url_path = endpoint.path
        query_params = {}
        json_body = {}
        headers = {"Content-Type": "application/json"}

        # Separate parameters by location
        path_params = {}
        for param_name, param_value in parameters.items():
            if param_name not in endpoint.parameters:
                # Parameter not in schema, try to infer location
                if "{" + param_name + "}" in url_path:
                    path_params[param_name] = param_value
                elif endpoint.method in ["POST", "PUT"]:
                    json_body[param_name] = param_value
                else:
                    query_params[param_name] = param_value
                continue

            param_info = endpoint.parameters[param_name]
            location = param_info.get("location", "query")

            if location == "path":
                path_params[param_name] = param_value
            elif location == "query":
                query_params[param_name] = param_value
            elif location == "body":
                json_body[param_name] = param_value
            else:
                # Default behavior based on HTTP method
                if endpoint.method in ["POST", "PUT"]:
                    json_body[param_name] = param_value
                else:
                    query_params[param_name] = param_value

        # Replace path parameters
        for param_name, param_value in path_params.items():
            url_path = url_path.replace(f"{{{param_name}}}", str(param_value))

        # Build full URL
        url = f"{self.base_url}{url_path}"

        return url, query_params, json_body, headers

    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Parse HTTP response"""
        try:
            # Try to parse JSON
            try:
                data = response.json()
            except:
                data = {"raw_response": response.text}

            # Check status code
            is_success = response.status_code < 400

            result = {
                "success": is_success,
                "status_code": response.status_code,
                "data": data
            }

            if not is_success:
                # Extract error message
                if isinstance(data, dict):
                    error_msg = data.get("detail", data.get("message", "Unknown error"))
                else:
                    error_msg = str(data)

                result["error"] = error_msg

            return result

        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {
                "success": False,
                "status_code": response.status_code if response else 0,
                "error": f"Failed to parse response: {str(e)}"
            }


# Global instance
_api_orchestrator = None


def get_api_orchestrator() -> APIOrchestrator:
    """Get global API orchestrator instance"""
    global _api_orchestrator
    if _api_orchestrator is None:
        _api_orchestrator = APIOrchestrator()
    return _api_orchestrator
