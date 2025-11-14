# PROJECT LUMEN 🔆

**AI-Native Financial Intelligence Layer**

An autonomous AI system that transforms raw financial documents into structured intelligence through multimodal analysis, RAG-powered reasoning, and agentic audit workflows.

---

## 🎯 Overview

Project LUMEN is an end-to-end AI financial intelligence platform that:

- **Ingests** financial documents (PDFs, images) and extracts structured data
- **Indexes** content using hybrid RAG (Dense + Sparse + HyDE retrieval)
- **Analyzes** invoices with autonomous AI agents (Audit, Compliance, Fraud, Explainability)
- **Maintains** persistent memory in `workspace.md` for context-aware reasoning
- **Delivers** actionable insights through a clean web interface

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python FastAPI |
| **Embeddings** | sentence-transformers/all-mpnet-base-v2 |
| **Vector Store** | FAISS (local) |
| **Sparse Retrieval** | BM25 (rank-bm25) |
| **Reranker** | MonoT5 (castorini/monot5-base-msmarco) |
| **Document Processing** | pdfminer.six, pytesseract |
| **Anomaly Detection** | IsolationForest, Z-score |
| **Frontend** | HTML/CSS/JavaScript |

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                   DOCUMENT INGESTION                    │
│  PDF/Image → Text Extraction → LLM Parsing → Indexing  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                   RAG PIPELINE (Local)                  │
│  HyDE → Dense (FAISS) + Sparse (BM25) → Rerank (MonoT5)│
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                   AGENTIC AI SYSTEM                     │
│  Audit Agent → Compliance Agent → Fraud Agent →        │
│  Explainability Agent → workspace.md                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Tesseract OCR** (for image processing)
   - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Mac: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`
3. **OpenAI API Key** (optional, for LLM parsing)

### Installation

```bash
# Clone repository
cd project-lumen

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
# LLM Configuration (Optional)
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=your_api_key_here

# Or use local models
# LLM_PROVIDER=local
```

### Run the Application

#### Backend

```bash
# From project root
cd backend
python main.py

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

#### Frontend

```bash
# Open frontend/index.html in a browser
# Or use a simple HTTP server:
cd frontend
python -m http.server 3000

# Then open: http://localhost:3000
```

---

## 📡 API Endpoints

### 1. Document Ingestion

**POST** `/ingest/`

Upload and process financial documents.

```bash
curl -X POST "http://localhost:8000/ingest/" \
  -F "file=@invoice.pdf"
```

**Response:**
```json
{
  "status": "success",
  "document_id": "doc_abc123",
  "filename": "invoice.pdf",
  "extracted_fields": {
    "vendor": "ABC Corp",
    "date": "2025-11-10",
    "amount": 1250.00,
    "tax": 225.00,
    "category": "Office Supplies",
    "invoice_number": "INV-001"
  },
  "chunks_created": 12
}
```

### 2. Audit Execution

**POST** `/audit/`

Run comprehensive multi-agent audit.

```bash
curl -X POST "http://localhost:8000/audit/" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_data": {
      "vendor": "ABC Corp",
      "date": "2025-11-10",
      "amount": 1250.00,
      "tax": 225.00,
      "category": "Office Supplies",
      "invoice_number": "INV-001"
    }
  }'
```

**Response:**
```json
{
  "audit_id": "audit_xyz789",
  "overall_status": "pass",
  "findings": {
    "audit": {
      "status": "pass",
      "duplicates": [],
      "mismatches": [],
      "total_errors": []
    },
    "compliance": {
      "compliant": true,
      "violations": [],
      "confidence": 0.85
    },
    "fraud": {
      "anomaly_detected": false,
      "risk_score": 0.23,
      "suspicious_indicators": []
    }
  },
  "explanation": "Detailed natural language summary..."
}
```

### 3. Workspace Memory

**GET** `/memory/`

Retrieve complete workspace memory.

```bash
curl "http://localhost:8000/memory/"
```

**GET** `/memory/recent?n=10`

Get recent entries.

**POST** `/memory/search`

Search workspace content.

---

## 🧠 Agentic AI System

### 1. **Audit Agent**
- Detects duplicate invoices
- Analyzes vendor spending patterns
- Verifies invoice totals and calculations
- Identifies amount anomalies

### 2. **Compliance Agent**
- Retrieves relevant policies using RAG
- Validates invoices against financial rules
- Checks approval requirements
- Ensures regulatory compliance

### 3. **Fraud Agent**
- Z-score anomaly detection
- Isolation Forest ML model
- Pattern-based fraud indicators
- Risk scoring (0-1 scale)

### 4. **Explainability Agent**
- Generates natural language summaries
- Contextualizes findings
- Provides actionable recommendations
- Transparent decision-making

---

## 🔍 RAG Pipeline Details

### Hybrid Retrieval Flow

1. **HyDE (Hypothetical Document Embeddings)**
   - LLM generates hypothetical policy document
   - Improves query quality for dense retrieval

2. **Dense Retrieval**
   - Sentence-transformers embeddings
   - FAISS vector similarity search
   - Top 50 chunks retrieved

3. **Sparse Retrieval**
   - BM25 lexical matching
   - Complementary keyword search
   - Top 30 chunks retrieved

4. **Merge & Deduplicate**
   - Combine dense + sparse results
   - Remove duplicates by content

5. **Rerank with MonoT5**
   - Cross-encoder relevance scoring
   - Return top 5 most relevant chunks

---

## 📂 Project Structure

```
project-lumen/
│
├── backend/
│   ├── main.py                      # FastAPI app entry
│   ├── config.py                    # Configuration
│   │
│   ├── routers/
│   │   ├── ingest.py               # Ingestion API
│   │   ├── audit.py                # Audit API
│   │   └── memory.py               # Memory API
│   │
│   ├── rag/
│   │   ├── vector_store.py         # FAISS operations
│   │   ├── sparse_retriever.py     # BM25 retrieval
│   │   ├── hyde.py                 # HyDE generation
│   │   ├── reranker.py             # MonoT5 reranking
│   │   ├── retriever.py            # Hybrid orchestration
│   │   └── chunker.py              # Text chunking
│   │
│   ├── agents/
│   │   ├── audit_agent.py          # Audit logic
│   │   ├── compliance_agent.py     # Compliance validation
│   │   ├── fraud_agent.py          # Fraud detection
│   │   ├── explainability_agent.py # Explanation generation
│   │   └── orchestrator.py         # Agent coordination
│   │
│   ├── utils/
│   │   ├── text_extract.py         # PDF/Image extraction
│   │   ├── llm_parser.py           # LLM-based parsing
│   │   ├── workspace_writer.py     # workspace.md manager
│   │   └── logger.py               # Logging
│   │
│   ├── data/
│   │   ├── vector_index.faiss      # FAISS index
│   │   ├── chunks.jsonl            # Indexed chunks
│   │   ├── bm25_index/             # BM25 index files
│   │   ├── uploads/                # Uploaded files
│   │   └── policy_docs/            # Policy documents
│   │
│   └── workspace.md                # Persistent memory
│
├── frontend/
│   ├── index.html                  # Main UI
│   ├── app.js                      # Application logic
│   └── styles.css                  # Styling
│
├── requirements.txt                # Dependencies
├── README.md                       # This file
├── PROJECT_OUTLINE.md              # Architecture docs
└── DEVELOPMENT_LOG.md              # Development log
```

---

## 🎨 Frontend Features

### 1. Document Ingestion Panel
- Drag & drop file upload
- Real-time extraction results
- Auto-populate audit form

### 2. Audit Execution Panel
- Manual invoice entry
- Full multi-agent audit
- Detailed findings display

### 3. Workspace Memory Viewer
- Recent activity feed
- Full workspace view
- Statistics dashboard

---

## 🧪 Testing

### Test Document Ingestion

```bash
# Test with sample invoice
curl -X POST "http://localhost:8000/ingest/" \
  -F "file=@sample_invoice.pdf"
```

### Test Audit

```bash
# Test audit endpoint
curl -X POST "http://localhost:8000/audit/" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_data": {
      "vendor": "Test Vendor",
      "date": "2025-11-13",
      "amount": 500.00,
      "tax": 50.00,
      "category": "Office Supplies"
    }
  }'
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

---

## 🔐 Security Features

- End-to-end local processing (no external APIs for RAG)
- Audit trail in workspace.md
- File size limits on uploads
- Input validation and sanitization
- CORS configuration for frontend

---

## 📊 Performance

| Operation | Typical Time |
|-----------|--------------|
| PDF Text Extraction | 1-3s |
| Image OCR | 2-5s |
| LLM Parsing | 2-4s |
| Indexing (per doc) | 1-2s |
| Hybrid Retrieval | 0.5-1s |
| Full Audit | 5-10s |

---

## 🚧 Known Limitations

1. **LLM Dependency**: Document parsing and HyDE require LLM (OpenAI API or local model)
2. **Tesseract OCR**: Image quality affects OCR accuracy
3. **Memory Usage**: Large document sets may require RAM optimization
4. **MonoT5 Reranking**: Can be slow without GPU acceleration

---

## 🔮 Future Enhancements

- [ ] Local LLM support (Llama 2, Mistral)
- [ ] Multi-language support
- [ ] Blockchain-based audit trails
- [ ] Smart purchase reminders
- [ ] Category-based spending forecasts
- [ ] Real-time anomaly alerts
- [ ] Multi-user authentication
- [ ] ERP system integrations

---

## 🛠️ Troubleshooting

### Issue: Tesseract not found

**Solution:**
```bash
# Windows: Add Tesseract to PATH
# Or set in config.py:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue: CUDA out of memory

**Solution:**
```bash
# Use CPU-only versions
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue: OpenAI API errors

**Solution:**
- Check API key in .env file
- Verify sufficient credits
- Or set `LLM_PROVIDER=local` for rule-based fallback

---

## 📖 Documentation

- **API Docs**: http://localhost:8000/docs
- **Project Outline**: See `PROJECT_OUTLINE.md`
- **Development Log**: See `DEVELOPMENT_LOG.md`

---

## 🤝 Contributing

This is a hackathon project built for **PROJECT LUMEN** challenge.

Key areas for contribution:
- Additional fraud detection algorithms
- More compliance policy templates
- Enhanced OCR preprocessing
- Performance optimizations

---

## 📄 License

MIT License - Built for educational and research purposes.

---

## 🏆 Hackathon Submission

**Project**: PROJECT LUMEN - AI Financial Intelligence Layer

**Theme**: Generative AI | Agentic AI | Financial Security

**Key Innovations**:
1. ✅ Multimodal document intelligence (PDF + Image)
2. ✅ Hybrid RAG with HyDE enhancement
3. ✅ Multi-agent autonomous reasoning
4. ✅ Explainable AI with natural language summaries
5. ✅ Persistent workspace memory for context
6. ✅ Local-first architecture (privacy-preserving)

---

## 👥 Team

Built with ❤️ by the Project LUMEN Team

---

## 📞 Support

For issues or questions:
- Check the `/health` endpoint
- Review logs in `backend/lumen.log`
- Inspect `workspace.md` for audit history

---

**PROJECT LUMEN** - Illuminating Financial Intelligence Through AI 🔆
