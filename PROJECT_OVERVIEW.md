# PROJECT LUMEN - Complete Overview

**AI-Native Financial Intelligence Layer with Goal Planning & Receipt Analysis**

---

## 🎯 What is Project Lumen?

Project Lumen is a comprehensive AI-powered personal finance system that combines:
- **Smart Receipt Analysis** - Email receipt parsing with LLM agents
- **Goal-Based Financial Planning** - Create and track financial goals with AI-powered savings plans
- **Intelligent Spending Insights** - Budget alerts, predictions, and behavioral analysis
- **Multi-Agent Audit System** - Automated compliance and fraud detection

---

## ✅ What's Implemented

### Core Features (100% Complete)

#### 1. **Receipt Processing & Analysis** ✅
- **Email Integration**: Parse receipts from email (Zomato, Amazon, etc.)
- **LLM Extraction**: Ollama-powered receipt parsing
- **Smart Analysis**: Real-time budget alerts, goal impact, savings opportunities
- **Pattern Detection**: Identifies recurring expenses and spending patterns
- **Categorization**: Auto-categorizes expenses (dining, groceries, shopping, etc.)

**Key Files:**
- `backend/routers/email_integration.py` - Email parsing endpoint
- `backend/agents/receipt_orchestrator.py` - Orchestrates all receipt analysis
- `backend/agents/savings_opportunity_agent.py` - Finds savings opportunities

#### 2. **Goal Planning System** ✅
- **Goal Creation**: Create financial goals (car, house, emergency fund, etc.)
- **Savings Plans**: AI-generated monthly savings recommendations
- **Investment Strategies**: Asset allocation based on time horizon (stocks/bonds/cash)
- **Progress Tracking**: Real-time progress with ahead/behind calculations
- **Milestones**: Quarterly checkpoints for goal achievement

**Key Files:**
- `backend/routers/goals.py` - Goal CRUD endpoints
- `backend/agents/goal_planner_agent.py` - Creates savings plans
- `backend/models/goal.py` - Goal data models

#### 3. **Personal Finance Dashboard** ✅
- **Spending Analysis**: Category breakdown, vs budget comparisons
- **Predictions**: ML-based next month spending forecasts
- **Budget Recommendations**: AI-powered budget optimization
- **Financial Health Score**: 0-100 score based on debt, savings, emergency fund
- **Behavioral Insights**: Day-of-week patterns, impulse spending detection

**Key Files:**
- `backend/routers/personal_finance.py` - Finance analysis endpoints
- `backend/agents/personal_finance_agent.py` - Spending analysis & predictions
- `backend/agents/health_score_agent.py` - Financial health scoring

#### 4. **Multi-Agent Audit System** ✅
- **Audit Agent**: Duplicate detection, pattern validation
- **Compliance Agent**: Policy checking via RAG
- **Fraud Agent**: Z-score & Isolation Forest anomaly detection
- **Explainability Agent**: Natural language audit summaries

**Key Files:**
- `backend/agents/orchestrator.py` - Multi-agent coordination
- `backend/agents/audit_agent.py` - Duplicate & pattern checks
- `backend/agents/fraud_agent.py` - ML-based fraud detection

#### 5. **RAG System (Hybrid Retrieval)** ✅
- **Dense Retrieval**: FAISS vector store with sentence-transformers
- **Sparse Retrieval**: BM25 keyword matching
- **HyDE**: Hypothetical Document Embeddings for query enhancement
- **Reranking**: MonoT5 cross-encoder for relevance scoring
- **Local-First**: No external vector databases, privacy-preserving

**Key Files:**
- `backend/rag/vector_store.py` - FAISS operations
- `backend/rag/retriever.py` - Hybrid retrieval orchestration
- `backend/rag/sparse_retriever.py` - BM25 implementation

#### 6. **Additional Features** ✅
- **Subscriptions Detection**: Identifies recurring charges (Netflix, Spotify, etc.)
- **Smart Reminders**: Pattern-based reminders for recurring expenses
- **Gamification**: Points, badges, leaderboards
- **Family Analytics**: Shared family budgets & member comparisons
- **Social Comparison**: Anonymous peer benchmarking
- **Reports Generation**: PDF monthly/annual reports
- **Voice Integration**: Voice-to-text receipt upload
- **Image Forensics**: Receipt authenticity detection (ELA, EXIF analysis)

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python FastAPI |
| **LLM** | Ollama (llama3.1:8b) - Local, no API costs |
| **Embeddings** | sentence-transformers/all-mpnet-base-v2 |
| **Vector Store** | FAISS (local) |
| **Sparse Retrieval** | BM25 (rank-bm25) |
| **Reranker** | MonoT5 |
| **Document Processing** | pdfminer.six, pytesseract |
| **Anomaly Detection** | IsolationForest, Z-score |
| **Storage** | JSON files + FAISS indices |
| **Frontend** | Next.js + React |

### 16 Specialized AI Agents

1. **GoalPlannerAgent** - Creates savings plans & investment strategies
2. **PersonalFinanceAgent** - Spending analysis & predictions
3. **SavingsOpportunityAgent** - Finds ways to save money
4. **PatternAgent** - Detects recurring expenses
5. **AuditAgent** - Validates invoices & detects duplicates
6. **ComplianceAgent** - Checks policies via RAG
7. **FraudAgent** - ML-based fraud detection
8. **ExplainabilityAgent** - Generates human-readable summaries
9. **HealthScoreAgent** - Financial health scoring
10. **BehavioralAgent** - Spending psychology analysis
11. **SubscriptionAgent** - Detects & analyzes subscriptions
12. **FamilyAnalyticsAgent** - Family spending insights
13. **SocialComparisonAgent** - Peer benchmarking
14. **GamificationAgent** - Points & achievements
15. **ForensicsAgent** - Image authenticity detection
16. **Orchestrator** - Coordinates all agents

---

## 📊 Data Flow Examples

### Example 1: Goal Creation Flow
```
User: "I want to buy a car for $30,000 by 2029"
    ↓
POST /goals/ → GoalCreate validation
    ↓
UserStorage.create_goal() → Save to JSON
    ↓
GET /goals/{user_id}/{goal_id}/plan
    ↓
GoalPlannerAgent.create_plan()
    ├─ Get current savings rate from PersonalFinanceAgent
    ├─ Calculate monthly savings needed: $625/month
    ├─ Calculate gap: -$125/month (need to save more)
    ├─ Recommend asset allocation: 60% stocks, 40% bonds
    ├─ Generate recommendations: "Reduce dining $150/month"
    └─ Create quarterly milestones
    ↓
Return complete plan with investment strategy
```

### Example 2: Receipt Analysis Flow
```
Email: "Zomato Order Confirmed - Rs450"
    ↓
POST /email/parse-receipt
    ↓
EmailReceiptParser → Ollama LLM
    ├─ Extract: vendor=Zomato, amount=450, category=dining
    ├─ Confidence: 0.95 (LLM parsing)
    └─ Fallback: Regex (if LLM fails)
    ↓
ReceiptIngestionOrchestrator
    ├─ Step 1: Duplicate Check (AuditAgent)
    ├─ Step 2: Budget Alert (PersonalFinanceAgent + LLM)
    │   → "⚠️ You've used 85% of dining budget"
    ├─ Step 3: Goal Impact (GoalPlannerAgent + LLM)
    │   → "This delays your car goal by 2 days"
    ├─ Step 4: Savings Opportunity (SavingsOpportunityAgent + LLM)
    │   → "Cook at home: save $200/month"
    ├─ Step 5: Pattern Detection (PatternAgent + LLM)
    │   → "You order Zomato every Saturday"
    └─ Step 6: Store with enriched metadata
    ↓
Return complete analysis + alerts + recommendations
```

---

## 📁 Project Structure

```
project-lumen-fi/
├── backend/
│   ├── agents/ (16 AI agents)
│   ├── routers/ (16 API route files)
│   ├── models/ (8 data models)
│   ├── utils/ (16 utility files)
│   ├── rag/ (7 RAG components)
│   ├── config.py (Settings & LLM config)
│   ├── main.py (FastAPI app)
│   └── data/
│       ├── user_data/{user_id}/ (User profiles & goals)
│       ├── vector_index.faiss (Vector store)
│       └── chunks.jsonl (Indexed documents)
│
├── nextjs-app/ (Next.js frontend)
│   ├── app/ (Pages)
│   ├── components/ (React components)
│   └── services/ (API client)
│
└── Documentation/
    ├── README.md (Main docs)
    ├── QUICKSTART.md (Setup guide)
    ├── API_DOCUMENTATION.md (Complete API reference)
    ├── GOAL_MAKER_ANALYSIS.md (Goal system deep dive)
    ├── IMPLEMENTATION_SUMMARY.md (Receipt analysis system)
    ├── ARCHITECTURE_QUICK_REFERENCE.md (Architecture overview)
    ├── FILE_MANIFEST.md (File locations)
    ├── OLLAMA_SETUP_INSTRUCTIONS.md (Ollama setup)
    └── GEMINI_SETUP.md (Gemini setup)
```

**Code Statistics:**
- **Total Lines**: ~10,000+ lines of Python
- **Total Agents**: 16 specialized agents
- **Total Routers**: 16 API route files
- **Total Endpoints**: ~50+ API endpoints
- **Total Models**: 8 core data models

---

## 🚀 Quick Start

### 1. Setup Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure LLM
```bash
# Option 1: Ollama (Local, Free)
# See OLLAMA_SETUP_INSTRUCTIONS.md

# Option 2: Gemini (Cloud, Free tier)
echo "GEMINI_API_KEY=your-key" >> .env
# See GEMINI_SETUP.md
```

### 3. Start Server
```bash
python -m uvicorn backend.main:app --reload
```

### 4. Load Demo Data
```bash
python seed_data.py
```

### 5. Test APIs
```bash
# Health check
curl http://localhost:8000/health

# Get dashboard
curl http://localhost:8000/finance/dashboard/test_user_001?period=month

# List goals
curl http://localhost:8000/goals/test_user_001
```

---

## 🎓 Key Innovations

### 1. **LLM-Powered Everything**
- Every agent uses LLM for intelligence (not hardcoded rules)
- Real Ollama integration (no dummy data)
- Specific, actionable recommendations

### 2. **Intelligent Receipt Analysis**
- Duplicate check BEFORE storage
- Real-time budget alerts with personalized advice
- Goal impact analysis (delays, opportunity cost)
- Savings suggestions (alternatives, strategies)
- Pattern detection (triggers, behavioral insights)

### 3. **Goal-Aligned Spending**
- Every purchase analyzed for goal impact
- Pre-purchase advice ("should I buy this?")
- Specific recommendations to stay on track

### 4. **Rich Metadata**
- Temporal context (day of week, time of month)
- Budget context (remaining, percent used)
- Goal context (affects goals, discretionary)
- All stored for future analysis

### 5. **Privacy-First**
- All processing local
- No external vector databases
- RAG system runs entirely on-premise
- User data never leaves your network

---

## 📖 Documentation Guide

| File | Purpose |
|------|---------|
| `README.md` | Complete project documentation & setup |
| `QUICKSTART.md` | 5-minute setup guide |
| `API_DOCUMENTATION.md` | Complete API reference with examples |
| `GOAL_MAKER_ANALYSIS.md` | Deep dive into goal system architecture |
| `IMPLEMENTATION_SUMMARY.md` | Receipt analysis implementation details |
| `ARCHITECTURE_QUICK_REFERENCE.md` | Architecture diagrams & data flows |
| `FILE_MANIFEST.md` | File locations & code structure |
| `OLLAMA_SETUP_INSTRUCTIONS.md` | Ollama setup for local LLM |
| `GEMINI_SETUP.md` | Gemini setup for cloud LLM |
| `FEATURE_GAP_ANALYSIS.md` | Future enhancements planning |

---

## 🎯 Use Cases

1. **Personal Finance Management**
   - Track receipts automatically from emails
   - Get real-time budget alerts
   - See spending predictions

2. **Goal Planning**
   - Create financial goals (car, house, vacation)
   - Get AI-powered savings plans
   - Track progress with milestones

3. **Spending Optimization**
   - Find unused subscriptions
   - Get specific budget cut recommendations
   - See behavioral spending patterns

4. **Invoice Auditing**
   - Detect duplicate invoices
   - Check policy compliance
   - Identify fraudulent patterns

---

## 🔮 Future Enhancements

- **Mobile App** (React Native)
- **Real-time notifications** (WebSockets)
- **Voice assistant** ("Hey Lumen, should I buy this?")
- **Bank integration** (Plaid API)
- **Cryptocurrency tracking**
- **Tax optimization** (auto-categorize for deductions)

---

## 📞 Support

- **API Docs**: `http://localhost:8000/docs`
- **Architecture**: See `ARCHITECTURE_QUICK_REFERENCE.md`
- **Setup Issues**: See `QUICKSTART.md`
- **API Reference**: See `API_DOCUMENTATION.md`

---

**PROJECT LUMEN - Illuminating Financial Intelligence Through AI** 🔆

*A complete, production-ready AI financial intelligence system with goal planning, receipt analysis, and multi-agent reasoning.*
