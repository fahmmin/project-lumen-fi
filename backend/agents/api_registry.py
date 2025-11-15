"""
API Registry Builder - Automatically Discovers and Catalogs All API Endpoints
Scans FastAPI application and creates a searchable registry for the chatbot
"""

from typing import Dict, List, Optional, Any
from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic import BaseModel
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

from backend.config import settings
from backend.utils.logger import logger


class EndpointSchema(BaseModel):
    """Schema for a registered API endpoint"""
    path: str
    method: str
    name: str
    description: str
    summary: str
    parameters: Dict[str, Dict[str, Any]]  # param_name -> {type, required, location}
    request_model: Optional[str] = None
    response_model: Optional[str] = None
    examples: List[str] = []
    tags: List[str] = []
    category: str = "general"


class APIRegistry:
    """
    Automatically discovers and indexes all API endpoints from FastAPI app
    Creates searchable registry with embeddings for semantic matching
    """

    def __init__(self):
        """Initialize registry"""
        self.endpoints: List[EndpointSchema] = []
        self.embedding_model = None
        self.endpoint_embeddings: List[List[float]] = []
        self.registry_file = settings.DATA_DIR / "api_registry.json"

        # Predefined natural language examples for common patterns
        self.nl_examples = self._load_nl_examples()

    def _load_nl_examples(self) -> Dict[str, List[str]]:
        """Load natural language examples for endpoint patterns"""
        return {
            # User Profile
            "create_profile": ["create my profile", "sign up", "register", "set up account"],
            "get_profile": ["show my profile", "my account", "profile info", "who am I"],
            "update_profile": ["update my profile", "change my info", "edit account"],
            "update_salary": ["I earn", "my salary is", "update income", "monthly income"],

            # Financial Goals
            "create_goal": ["create goal", "save for", "I want to save", "new goal", "add goal"],
            "list_goals": ["show goals", "my goals", "what am I saving for", "list goals"],
            "goal_plan": ["how to reach goal", "goal plan", "savings plan", "achieve goal"],
            "goal_progress": ["goal progress", "am I on track", "how's my goal", "check goal"],

            # Spending & Dashboard
            "dashboard": ["dashboard", "summary", "overview", "how am I doing", "show me"],
            "spending": ["how much spent", "spending", "expenses", "breakdown"],
            "predict": ["predict", "forecast", "what will I spend", "next month"],
            "insights": ["insights", "tips", "advice", "suggestions", "recommendations"],
            "health_score": ["health score", "financial health", "how healthy", "rate me"],

            # Reports
            "generate_report": ["generate report", "create report", "send report", "make report"],
            "schedule_weekly": ["weekly report", "email weekly", "schedule weekly"],
            "schedule_monthly": ["monthly report", "email monthly", "schedule monthly"],

            # Receipts
            "upload_receipt": ["upload receipt", "add receipt", "I spent", "parse receipt"],
            "parse_email": ["email receipt", "parse email", "from email"],
            "voice_receipt": ["voice receipt", "audio receipt", "voice input"],

            # Subscriptions & Patterns
            "subscriptions": ["subscriptions", "recurring", "what subscriptions"],
            "unused_subscriptions": ["unused", "cancel subscriptions", "save money"],
            "patterns": ["patterns", "trends", "habits", "spending patterns"],
            "reminders": ["reminders", "bills", "what's due", "payments"],

            # Family
            "create_family": ["create family", "new family", "family group", "household"],
            "join_family": ["join family", "invite code", "join household"],
            "family_dashboard": ["family dashboard", "family spending", "our spending"],

            # Gamification
            "my_stats": ["my stats", "my level", "my points", "my badges"],
            "leaderboard": ["leaderboard", "rankings", "top users", "who's winning"],

            # Social
            "compare": ["how do I compare", "percentile", "am I normal", "comparison"],
            "social_insights": ["social insights", "peer comparison", "others spending"],

            # Audit
            "audit": ["audit", "check compliance", "validate", "is this legit"],
        }

    def scan_app(self, app: FastAPI):
        """
        Scan FastAPI app and extract all endpoint information

        Args:
            app: FastAPI application instance
        """
        logger.info("Scanning FastAPI application for endpoints...")

        self.endpoints = []

        for route in app.routes:
            if isinstance(route, APIRoute):
                endpoint = self._extract_endpoint_info(route)
                if endpoint:
                    self.endpoints.append(endpoint)

        logger.info(f"Discovered {len(self.endpoints)} API endpoints")

        # Save to file
        self._save_registry()

        # Create embeddings for semantic search
        self._create_embeddings()

    def _extract_endpoint_info(self, route: APIRoute) -> Optional[EndpointSchema]:
        """Extract information from a single route"""
        try:
            # Skip internal endpoints
            if route.path.startswith("/docs") or route.path.startswith("/openapi"):
                return None

            # Get method (GET, POST, etc.)
            methods = list(route.methods)
            if not methods:
                return None
            method = methods[0]  # Use first method

            # Get description from docstring
            description = ""
            summary = ""
            if route.endpoint and route.endpoint.__doc__:
                doc = route.endpoint.__doc__.strip()
                lines = doc.split('\n')
                summary = lines[0] if lines else ""
                description = doc

            # Get path parameters
            parameters = {}

            # Path parameters
            if route.path_regex:
                for param_name in route.param_convertors.keys():
                    parameters[param_name] = {
                        "type": "string",
                        "required": True,
                        "location": "path"
                    }

            # Query and body parameters from signature
            if route.dependant:
                for param in route.dependant.query_params:
                    parameters[param.name] = {
                        "type": str(param.annotation) if param.annotation else "string",
                        "required": param.required,
                        "location": "query",
                        "default": param.default if hasattr(param, 'default') else None
                    }

                for param in route.dependant.body_params:
                    parameters[param.name] = {
                        "type": str(param.annotation) if param.annotation else "object",
                        "required": param.required,
                        "location": "body"
                    }

            # Determine category from path
            category = self._categorize_endpoint(route.path)

            # Get natural language examples
            examples = self._get_examples_for_endpoint(route.path, method, route.name)

            # Get tags
            tags = route.tags if route.tags else []

            return EndpointSchema(
                path=route.path,
                method=method,
                name=route.name or "",
                description=description,
                summary=summary or description.split('\n')[0] if description else "",
                parameters=parameters,
                examples=examples,
                tags=tags,
                category=category
            )

        except Exception as e:
            logger.warning(f"Error extracting endpoint info for {route.path}: {e}")
            return None

    def _categorize_endpoint(self, path: str) -> str:
        """Categorize endpoint based on path"""
        if "/users" in path or "/profile" in path:
            return "user_profile"
        elif "/goals" in path:
            return "financial_goals"
        elif "/finance" in path or "/spending" in path or "/dashboard" in path:
            return "spending_analysis"
        elif "/reports" in path or "/scheduled-reports" in path:
            return "reports"
        elif "/email" in path or "/voice" in path or "/ingest" in path:
            return "receipt_upload"
        elif "/subscriptions" in path:
            return "subscriptions"
        elif "/reminders" in path or "/patterns" in path:
            return "reminders_patterns"
        elif "/family" in path:
            return "family_budgets"
        elif "/gamification" in path:
            return "gamification"
        elif "/social" in path:
            return "social_comparison"
        elif "/audit" in path:
            return "audit_compliance"
        elif "/memory" in path:
            return "memory_rag"
        else:
            return "general"

    def _get_examples_for_endpoint(self, path: str, method: str, name: str) -> List[str]:
        """Get natural language examples for an endpoint"""
        examples = []

        # Match against predefined examples
        if "profile" in path and method == "POST":
            examples = self.nl_examples.get("create_profile", [])
        elif "profile" in path and method == "GET":
            examples = self.nl_examples.get("get_profile", [])
        elif "salary" in path:
            examples = self.nl_examples.get("update_salary", [])
        elif "goals" in path and method == "POST":
            examples = self.nl_examples.get("create_goal", [])
        elif "goals" in path and method == "GET":
            examples = self.nl_examples.get("list_goals", [])
        elif "goal" in path and "plan" in path:
            examples = self.nl_examples.get("goal_plan", [])
        elif "goal" in path and "progress" in path:
            examples = self.nl_examples.get("goal_progress", [])
        elif "dashboard" in path:
            examples = self.nl_examples.get("dashboard", [])
        elif "spending" in path:
            examples = self.nl_examples.get("spending", [])
        elif "predictions" in path:
            examples = self.nl_examples.get("predict", [])
        elif "insights" in path:
            examples = self.nl_examples.get("insights", [])
        elif "health-score" in path:
            examples = self.nl_examples.get("health_score", [])
        elif "generate-now" in path:
            examples = self.nl_examples.get("generate_report", [])
        elif "schedule/weekly" in path:
            examples = self.nl_examples.get("schedule_weekly", [])
        elif "schedule/monthly" in path:
            examples = self.nl_examples.get("schedule_monthly", [])
        elif "ingest" in path or ("receipt" in path and method == "POST"):
            examples = self.nl_examples.get("upload_receipt", [])
        elif "email" in path and "parse" in path:
            examples = self.nl_examples.get("parse_email", [])
        elif "voice" in path and "upload" in path:
            examples = self.nl_examples.get("voice_receipt", [])
        elif "subscriptions" in path and "unused" in path:
            examples = self.nl_examples.get("unused_subscriptions", [])
        elif "subscriptions" in path:
            examples = self.nl_examples.get("subscriptions", [])
        elif "patterns" in path:
            examples = self.nl_examples.get("patterns", [])
        elif "reminders" in path:
            examples = self.nl_examples.get("reminders", [])
        elif "family" in path and "create" in path:
            examples = self.nl_examples.get("create_family", [])
        elif "family" in path and "join" in path:
            examples = self.nl_examples.get("join_family", [])
        elif "family" in path and "dashboard" in path:
            examples = self.nl_examples.get("family_dashboard", [])
        elif "gamification/stats" in path:
            examples = self.nl_examples.get("my_stats", [])
        elif "leaderboard" in path:
            examples = self.nl_examples.get("leaderboard", [])
        elif "social" in path and "percentile" in path:
            examples = self.nl_examples.get("compare", [])
        elif "social" in path and "insights" in path:
            examples = self.nl_examples.get("social_insights", [])
        elif "audit" in path:
            examples = self.nl_examples.get("audit", [])

        return examples

    def _save_registry(self):
        """Save registry to JSON file"""
        try:
            registry_data = {
                "endpoints": [endpoint.dict() for endpoint in self.endpoints],
                "total_endpoints": len(self.endpoints)
            }

            with open(self.registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2)

            logger.info(f"Saved API registry to {self.registry_file}")

        except Exception as e:
            logger.error(f"Error saving registry: {e}")

    def _create_embeddings(self):
        """Create embeddings for semantic search"""
        try:
            logger.info("Creating embeddings for semantic search...")

            # Initialize embedding model (use same as RAG system)
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

            # Create text for each endpoint
            texts = []
            for endpoint in self.endpoints:
                # Combine all relevant text
                text_parts = [
                    endpoint.path,
                    endpoint.summary,
                    endpoint.description,
                    " ".join(endpoint.examples),
                    " ".join(endpoint.tags),
                    endpoint.category.replace("_", " ")
                ]
                text = " ".join(filter(None, text_parts))
                texts.append(text)

            # Generate embeddings
            self.endpoint_embeddings = self.embedding_model.encode(texts, show_progress_bar=False)

            logger.info(f"Created embeddings for {len(texts)} endpoints")

        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")

    def search_endpoints(
        self,
        query: str,
        top_k: int = 3,
        method_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for endpoints using semantic similarity

        Args:
            query: Natural language query
            top_k: Number of results to return
            method_filter: Filter by HTTP method (GET, POST, etc.)

        Returns:
            List of matching endpoints with confidence scores
        """
        if not self.embedding_model or self.endpoint_embeddings is None or len(self.endpoint_embeddings) == 0:
            logger.warning("Embeddings not initialized, falling back to keyword search")
            return self._keyword_search(query, top_k, method_filter)

        try:
            # Encode query
            query_embedding = self.embedding_model.encode([query], show_progress_bar=False)[0]

            # Calculate similarity scores
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity

            scores = cosine_similarity([query_embedding], self.endpoint_embeddings)[0]

            # Get top results
            top_indices = np.argsort(scores)[::-1][:top_k * 2]  # Get more than needed for filtering

            results = []
            for idx in top_indices:
                endpoint = self.endpoints[idx]

                # Apply method filter if specified
                if method_filter and endpoint.method != method_filter:
                    continue

                results.append({
                    "endpoint": endpoint.dict(),
                    "confidence": float(scores[idx]),
                    "reasoning": f"Semantic match with score {scores[idx]:.3f}"
                })

                if len(results) >= top_k:
                    break

            return results

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return self._keyword_search(query, top_k, method_filter)

    def _keyword_search(
        self,
        query: str,
        top_k: int,
        method_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fallback keyword-based search"""
        query_lower = query.lower()
        results = []

        for endpoint in self.endpoints:
            # Apply method filter
            if method_filter and endpoint.method != method_filter:
                continue

            score = 0.0

            # Check path
            if query_lower in endpoint.path.lower():
                score += 0.5

            # Check description
            if endpoint.description and query_lower in endpoint.description.lower():
                score += 0.3

            # Check examples
            for example in endpoint.examples:
                if query_lower in example.lower():
                    score += 0.4
                    break

            # Check category
            if query_lower in endpoint.category.replace("_", " ").lower():
                score += 0.2

            if score > 0:
                results.append({
                    "endpoint": endpoint.dict(),
                    "confidence": min(score, 1.0),
                    "reasoning": "Keyword match"
                })

        # Sort by score and return top k
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[:top_k]

    def get_endpoint_by_path(self, path: str, method: str) -> Optional[EndpointSchema]:
        """Get endpoint by exact path and method"""
        for endpoint in self.endpoints:
            if endpoint.path == path and endpoint.method == method:
                return endpoint
        return None

    def get_all_endpoints(self) -> List[EndpointSchema]:
        """Get all registered endpoints"""
        return self.endpoints

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(endpoint.category for endpoint in self.endpoints))


# Global registry instance
_api_registry = None


def get_api_registry() -> APIRegistry:
    """Get global API registry instance"""
    global _api_registry
    if _api_registry is None:
        _api_registry = APIRegistry()
    return _api_registry
