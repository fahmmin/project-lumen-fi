"""
PROJECT LUMEN - Configuration Management
Centralized configuration for all system components
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
POLICY_DOCS_DIR = DATA_DIR / "policy_docs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
POLICY_DOCS_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "PROJECT LUMEN"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # File paths
    DATA_DIR: Path = DATA_DIR
    WORKSPACE_FILE: Path = BASE_DIR / "workspace.md"
    VECTOR_INDEX_PATH: Path = DATA_DIR / "vector_index.faiss"
    CHUNKS_FILE: Path = DATA_DIR / "chunks.jsonl"
    BM25_INDEX_PATH: Path = DATA_DIR / "bm25_index"
    POLICY_DOCS_DIR: Path = POLICY_DOCS_DIR

    # Upload settings
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg"}

    # RAG settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_DIM: int = 768
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50

    # Retrieval settings
    DENSE_TOP_K: int = 50
    SPARSE_TOP_K: int = 30
    RERANK_TOP_K: int = 5
    RERANKER_MODEL: str = "castorini/monot5-base-msmarco"

    # LLM settings (for parsing and HyDE)
    LLM_PROVIDER: str = "ollama"  # Options: "openai", "gemini", "ollama"
    LLM_MODEL: str = "llama3.1:8b"  # Ollama model name
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 1000

    # Ollama settings (for local LLM)
    OLLAMA_BASE_URL: str = "http://172.16.163.34:11434"  # Change to GPU server IP if on different machine
    OLLAMA_MODEL: str = "llama3.1:8b"

    # Cloud API keys (fallback, not used when LLM_PROVIDER=ollama)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # MongoDB settings
    MONGO_URI: Optional[str] = None

    # SendGrid Email settings
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "noreply@projectlumen.ai"
    SENDGRID_FROM_NAME: str = "Project Lumen Financial Reports"

    # Report settings
    REPORTS_DIR: Path = DATA_DIR / "reports"
    REPORT_GENERATION_ENABLED: bool = True

    # Scheduled report settings
    SCHEDULED_REPORTS_ENABLED: bool = True
    DEFAULT_REPORT_SCHEDULE: str = "weekly"  # weekly, monthly, quarterly
    REPORT_GENERATION_DAY: int = 1  # Day of week (0=Monday, 6=Sunday) for weekly reports
    REPORT_GENERATION_HOUR: int = 8  # Hour of day (24-hour format)

    # Agent settings
    AUDIT_THRESHOLD: float = 0.15  # Deviation threshold for anomaly
    FRAUD_ZSCORE_THRESHOLD: float = 3.0
    COMPLIANCE_CONFIDENCE: float = 0.7

    # Tax rates (jurisdiction-specific, configurable)
    # Common tax rates for validation (percentages as decimals)
    COMMON_TAX_RATES: list = [0.05, 0.07, 0.10, 0.15, 0.18, 0.20]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = BASE_DIR / "lumen.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(exist_ok=True)
settings.REPORTS_DIR.mkdir(exist_ok=True)


# Document schema for LLM extraction
DOCUMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "vendor": {"type": "string", "description": "Vendor or merchant name"},
        "date": {"type": "string", "description": "Transaction date (YYYY-MM-DD)"},
        "amount": {"type": "number", "description": "Total amount"},
        "tax": {"type": "number", "description": "Tax amount"},
        "category": {"type": "string", "description": "Expense category"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit_price": {"type": "number"},
                    "total": {"type": "number"}
                }
            }
        },
        "invoice_number": {"type": "string", "description": "Invoice/receipt number"},
        "payment_method": {"type": "string", "description": "Payment method if available"}
    },
    "required": ["vendor", "date", "amount"]
}


# Prompt templates
EXTRACTION_PROMPT = """
You are a financial document parser specializing in receipts and invoices. Extract structured information from the following text.

IMPORTANT INSTRUCTIONS:
- Extract the TOTAL amount as a number (remove currency symbols ₹, Rs, $)
- If amount is "Rs450" or "₹450", extract as 450.0 (not 4.5)
- If amount has comma like "Rs1,250" or "₹1,250", extract as 1250.0
- Date format MUST be YYYY-MM-DD
- Common Indian vendors: Zomato, Swiggy, BigBasket, Flipkart, Amazon, Paytm, Myntra, PhonePe, Google Pay
- Categories: dining, groceries, shopping, entertainment, transportation, healthcare, utilities, travel

Text:
{text}

Return a JSON object with these EXACT fields:
{{
  "vendor": "merchant name",
  "date": "YYYY-MM-DD",
  "amount": 450.0,
  "tax": 45.0,
  "category": "dining",
  "items": ["item1", "item2"],
  "invoice_number": "INV123",
  "payment_method": "UPI"
}}

Return ONLY valid JSON, no other text or explanation.
"""

HYDE_PROMPT = """
Generate a hypothetical financial document or policy excerpt that would answer this query:

Query: {query}

Write a detailed, realistic financial document excerpt (100-150 words) that contains relevant information.
Focus on policies, regulations, or standard practices related to the query.
"""

COMPLIANCE_PROMPT = """
You are a financial compliance auditor. Given the following invoice data and retrieved policy context,
determine if the invoice complies with financial policies.

Invoice Data:
{invoice_data}

Policy Context:
{context}

Analyze the invoice against the policies and return a JSON response:
{{
    "compliant": true/false,
    "violations": ["list of violations if any"],
    "confidence": 0.0-1.0,
    "explanation": "brief explanation"
}}

Return only valid JSON.
"""

EXPLANATION_PROMPT = """
You are an AI financial analyst. Generate a clear, professional explanation of the audit findings.

Audit Findings:
{findings}

Context Used:
{context}

Generate a concise, human-readable summary (2-3 paragraphs) explaining:
1. What was analyzed
2. Key findings and their significance
3. Recommended actions (if any issues found)

Be professional, clear, and actionable.
"""
