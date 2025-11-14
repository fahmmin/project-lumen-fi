# PROJECT LUMEN - AI Financial Intelligence Layer

## 🎯 Project Vision
An AI-native financial intelligence layer that transforms raw financial documents into structured intelligence and actionable insights using multimodal GenAI, RAG, and agentic reasoning.

## 📋 Project Status
**Status**: In Development
**Last Updated**: 2025-11-13
**Phase**: Initial Setup

---

## 🏗️ Architecture Overview

### Technology Stack
- **Backend**: Python FastAPI
- **RAG System**: Local-only (FAISS + BM25)
- **Embeddings**: sentence-transformers/all-mpnet-base-v2
- **Sparse Retrieval**: BM25 (Whoosh)
- **Reranker**: MonoT5 (castorini/monot5-base-msmarco)
- **Document Processing**: pdfminer.six, pytesseract
- **Anomaly Detection**: IsolationForest / Z-score
- **Frontend**: HTML/CSS/JavaScript

### Core Components

#### 1. Document Ingestion Pipeline
- **Input**: PDFs, Images (receipts, invoices)
- **Processing**:
  - Text extraction (PDF: pdfminer.six, Image: pytesseract)
  - LLM-based structured data extraction
  - JSON schema: vendor, date, amount, tax, items, category
- **Output**: Structured data + workspace.md log entry

#### 2. RAG Pipeline (Local-Only)
- **Dense Embeddings**: all-mpnet-base-v2
- **Sparse Retrieval**: BM25 (local index)
- **HyDE**: Hypothetical Document Embeddings
- **Vector Store**: FAISS (local files)
- **Hybrid Retrieval**:
  1. Generate HyDE pseudo document
  2. Dense retrieve top 50 (FAISS)
  3. Sparse retrieve top 30 (BM25)
  4. Merge + deduplicate
  5. Rerank with MonoT5 → top 5 chunks

#### 3. Agentic AI System
- **Audit Agent**: Duplicate detection, vendor analysis, total verification
- **Compliance Agent**: Policy rule validation via RAG
- **Fraud Agent**: Anomaly detection (IsolationForest/Z-score)
- **Explainability Agent**: Natural language explanation generation
- **Orchestrator**: Coordinates all agents, generates comprehensive reports

#### 4. Memory System
- **workspace.md**: Persistent memory file
- Logs all ingestion and audit operations
- Provides context for agent reasoning

---

## 📁 Project Structure

```
project-lumen/
│
├── backend/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration management
│   │
│   ├── routers/
│   │   ├── ingest.py               # Document ingestion endpoint
│   │   ├── audit.py                # Audit execution endpoint
│   │   └── memory.py               # Memory/workspace endpoint
│   │
│   ├── rag/
│   │   ├── hyde.py                 # HyDE implementation
│   │   ├── retriever.py            # Hybrid retrieval logic
│   │   ├── reranker.py             # MonoT5 reranking
│   │   ├── vector_store.py         # FAISS operations
│   │   └── chunker.py              # Text chunking
│   │
│   ├── agents/
│   │   ├── audit_agent.py          # Audit logic
│   │   ├── compliance_agent.py     # Compliance checking
│   │   ├── fraud_agent.py          # Anomaly detection
│   │   ├── explainability_agent.py # Explanation generation
│   │   └── orchestrator.py         # Agent coordination
│   │
│   ├── utils/
│   │   ├── text_extract.py         # PDF/Image text extraction
│   │   ├── workspace_writer.py     # workspace.md management
│   │   └── logger.py               # Logging utilities
│   │
│   ├── data/
│   │   ├── vector_index.faiss      # FAISS index file
│   │   ├── chunks.jsonl            # Indexed chunks
│   │   └── policy_docs/            # Compliance policy documents
│   │
│   └── workspace.md                # Persistent memory file
│
├── frontend/
│   ├── index.html                  # Main UI
│   ├── app.js                      # Application logic
│   └── styles.css                  # Styling
│
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

---

## 🔌 API Endpoints

### POST /ingest
**Purpose**: Upload and process financial documents

**Input**:
- Multipart file upload (PDF/Image)

**Process**:
1. Extract text from document
2. Parse into JSON via LLM
3. Embed and index text chunks
4. Update FAISS + BM25 indices
5. Log to workspace.md

**Output**:
```json
{
  "status": "success",
  "filename": "invoice_123.pdf",
  "extracted_fields": {
    "vendor": "ABC Corp",
    "date": "2025-11-10",
    "amount": 1250.00,
    "tax": 225.00,
    "category": "Office Supplies",
    "items": [...]
  },
  "document_id": "doc_xyz"
}
```

### POST /audit
**Purpose**: Run comprehensive audit on invoice

**Input**:
```json
{
  "invoice_data": {
    "vendor": "ABC Corp",
    "date": "2025-11-10",
    "amount": 1250.00,
    "tax": 225.00,
    "category": "Office Supplies"
  }
}
```

**Process**:
1. Orchestrator calls Audit Agent
2. Compliance Agent validates against policies (RAG)
3. Fraud Agent detects anomalies
4. Explainability Agent generates summary
5. Log to workspace.md

**Output**:
```json
{
  "audit_id": "audit_abc123",
  "findings": {
    "audit": {
      "duplicates": [],
      "mismatches": ["Tax rate unusual: 18% vs 12%"],
      "total_errors": []
    },
    "compliance": {
      "status": "pass",
      "violations": []
    },
    "fraud": {
      "anomaly_detected": false,
      "risk_score": 0.23
    }
  },
  "explanation": "Invoice appears valid with minor tax discrepancy...",
  "context_used": ["chunk_12", "chunk_34", "chunk_55"]
}
```

### GET /memory
**Purpose**: Retrieve workspace memory

**Output**:
```json
{
  "workspace_content": "... markdown content ...",
  "last_updated": "2025-11-13T10:30:00Z"
}
```

---

## 🧠 Agentic AI Workflow

```
User Upload → Ingestion
                ↓
         [Document Parsed]
                ↓
         workspace.md updated
                ↓
User triggers Audit
                ↓
         ORCHESTRATOR
                ↓
    ┌───────────┼───────────┬──────────┐
    ↓           ↓           ↓          ↓
[Audit]  [Compliance]  [Fraud]  [Explainability]
    ↓           ↓           ↓          ↓
    └───────────┴───────────┴──────────┘
                ↓
         Combined Report
                ↓
         workspace.md updated
                ↓
         Return to User
```

---

## 🚀 Development Phases

### Phase 1: Foundation ✅ COMPLETE
- [x] Project structure created
- [x] Configuration setup
- [x] Utility modules
- [x] workspace.md initialization

### Phase 2: RAG Pipeline ✅ COMPLETE
- [x] Text chunking
- [x] Dense embeddings (all-mpnet-base-v2)
- [x] FAISS vector store
- [x] BM25 sparse retrieval
- [x] HyDE implementation
- [x] MonoT5 reranking
- [x] Hybrid retrieval orchestration

### Phase 3: Document Ingestion ✅ COMPLETE
- [x] PDF text extraction
- [x] Image OCR (pytesseract)
- [x] LLM-based JSON parsing
- [x] Ingestion API endpoint

### Phase 4: Agentic System ✅ COMPLETE
- [x] Audit Agent
- [x] Compliance Agent
- [x] Fraud Agent
- [x] Explainability Agent
- [x] Orchestrator
- [x] Audit API endpoint

### Phase 5: Frontend ✅ COMPLETE
- [x] Upload interface
- [x] Audit trigger
- [x] Results display
- [x] Memory viewer

### Phase 6: Testing & Deployment ✅ COMPLETE
- [x] Integration testing
- [x] Documentation
- [x] README finalization
- [x] Deployment scripts
- [x] Verification tools

---

## 🔐 Security & Compliance
- End-to-end encryption for uploaded documents
- Local-only processing (no external APIs for core features)
- Audit trail in workspace.md
- Compliance validation against policy documents

---

## 📊 Innovation Features

### 1. Smart Purchase Reminders
- Pattern detection from monthly receipts
- Proactive spending reminders
- Bill due date predictions

### 2. Behavioral Intelligence
- Vendor spending pattern analysis
- Anomaly detection based on historical behavior
- Category-wise spending forecasts

### 3. Explainable AI
- Natural language audit explanations
- Context-aware compliance reasoning
- Transparent decision-making process

---

## 🔄 Workspace Memory Format

```markdown
# PROJECT LUMEN WORKSPACE

## Initialized: 2025-11-13

### NEW DOCUMENT INGESTED
Filename: invoice_001.pdf
Extracted Fields: vendor=ABC Corp, amount=1250.00, date=2025-11-10
Timestamp: 2025-11-13T10:15:00Z

### [AUDIT RUN] 2025-11-13T10:20:00Z
Invoice: INV-001
Findings:
- Tax mismatch: expected 18%, found 12%
- Vendor behavior normal
Context retrieved: chunks [12, 34, 55]
Risk Score: 0.23
Status: MINOR_ISSUES
```
---
## 📝 Next Steps
1. Complete backend implementation
2. Implement all RAG components
3. Build agent system
4. Create frontend interface
5. End-to-end testing
6. Documentation
---
**Project LUMEN** - Autonomous Financial Intelligence
