# Project Lumen - Architecture Quick Reference

## Component Interaction Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                                │
│  Voice Input │ Text Input │ Web UI (Next.js) │ Email Integration            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                      FastAPI APPLICATION (main.py)                          │
│                                                                              │
│  Routes:                                                                   │
│  ├─ POST /goals/                    (Create goal)                          │
│  ├─ GET  /goals/{user_id}           (List goals)                           │
│  ├─ GET  /goals/{user_id}/{goal_id} (Get goal detail)                      │
│  ├─ PUT  /goals/{goal_id}           (Update goal)                          │
│  ├─ DELETE /goals/{goal_id}         (Delete goal)                          │
│  ├─ POST /email/parse-receipt       (Parse email receipts)                 │
│  ├─ GET  /finance/dashboard/{user_id} (Dashboard analysis)                 │
│  ├─ GET  /finance/{user_id}/predictions (Spending predictions)             │
│  └─ [+ 15 other routers for audit, compliance, fraud, etc]                 │
└──────────────────────┬──────────────────────────┬───────────────────────────┘
                       │                          │
        ┌──────────────▼─────────────┐   ┌───────▼──────────────┐
        │   DATA MODELS (Pydantic)   │   │  AGENT CONTROLLERS   │
        ├──────────────────────────┤   ├──────────────────────┤
        │ - GoalCreate             │   │ - GoalPlannerAgent   │
        │ - GoalUpdate             │   │ - PersonalFinance    │
        │ - FinancialGoal          │   │ - AuditAgent         │
        │ - UserProfileCreate      │   │ - ComplianceAgent    │
        │ - UserProfile            │   │ - FraudAgent         │
        │ - EmailReceiptRequest    │   │ - PatternAgent       │
        └──────────────┬───────────┘   │ - [+ 10 more agents] │
                       │                └──────────┬───────────┘
        ┌──────────────▼─────────────┐            │
        │   DATA PERSISTENCE LAYER   │            │
        ├──────────────────────────┤            │
        │ UserStorage              │            │
        │ ├─ create_goal()        │            │
        │ ├─ list_goals()         │            │
        │ ├─ get_goal()           │            │
        │ ├─ update_goal()        │            │
        │ ├─ delete_goal()        │            │
        │ ├─ create_profile()     │            │
        │ └─ ensure_profile_exists()          │
        │                          │            │
        │ Storage: JSON Files      │            │
        │ /user_data/{user_id}/    │            │
        │ ├─ profile.json          │            │
        │ └─ goals.json            │            │
        └──────────────────────────┘            │
                                                 │
        ┌────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT PROCESSING LAYER                             │
│                                                                  │
│ GOAL PLANNING:                                                  │
│ ├─ GoalPlannerAgent                                             │
│ │  ├─ Calls: PersonalFinanceAgent.analyze_dashboard()          │
│ │  ├─ Calls: InvestmentCalculator.recommend_asset_allocation() │
│ │  ├─ Calls: InvestmentCalculator.calculate_monthly_savings()  │
│ │  └─ Calls: InvestmentCalculator.project_future_value()       │
│ │                                                               │
│ └─ PersonalFinanceAgent                                         │
│    ├─ analyze_dashboard(user_id, period)                        │
│    ├─ predict_spending(user_id)                                 │
│    ├─ get_spending_breakdown()                                  │
│    ├─ get_budget_recommendations()                              │
│    └─ Uses: VectorStore._get_user_receipts()                    │
│                                                                  │
│ RECEIPT PROCESSING:                                             │
│ ├─ EmailReceiptParser                                           │
│ │  ├─ parse_email(email_text, subject)                          │
│ │  ├─ _parse_with_ollama()  [Primary]                           │
│ │  └─ _parse_with_regex()   [Fallback]                          │
│ │                                                               │
│ └─ LLMParser (for PDFs/images)                                  │
│    └─ parse_document(text)                                      │
│                                                                  │
│ AUDIT & COMPLIANCE:                                             │
│ ├─ AuditOrchestrator                                            │
│ │  ├─ Step 1: AuditAgent.audit()                                │
│ │  ├─ Step 2: ComplianceAgent.check_compliance()                │
│ │  ├─ Step 3: FraudAgent.detect_fraud()                         │
│ │  ├─ Step 4: ExplainabilityAgent.explain()                     │
│ │  └─ Step 5: Log to workspace.md                               │
│ │                                                               │
│ ├─ AuditAgent: Duplicate checking, pattern validation           │
│ ├─ ComplianceAgent: Policy checking via RAG                     │
│ └─ FraudAgent: Anomaly detection (Z-score, ML)                  │
│                                                                  │
│ PATTERNS & INSIGHTS:                                            │
│ ├─ PatternAgent: Recurring expense detection                    │
│ ├─ BehavioralAgent: User behavior analysis                      │
│ └─ HealthScoreAgent: Financial health scoring                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │   LLM INTEGRATION LAYER     │
        ├────────────────────────────┤
        │ OllamaClient               │
        │ ├─ Model: llama3.1:8b      │
        │ ├─ Temperature: 0.1        │
        │ ├─ Max Tokens: 1000        │
        │ └─ URL: 172.16.163.34:11434│
        │                            │
        │ LLMParser                  │
        │ └─ Uses OllamaClient for   │
        │    document parsing        │
        │                            │
        │ EmailReceiptParser         │
        │ └─ Uses OllamaClient for   │
        │    email extraction        │
        └────────────┬───────────────┘
                     │
        ┌────────────▼──────────────┐
        │   RAG SYSTEM              │
        ├────────────────────────────┤
        │ VectorStore (FAISS)        │
        │ ├─ Embedding: sentence-    │
        │ │  transformers/all-mpnet  │
        │ ├─ Dim: 768                │
        │ ├─ Methods:                │
        │ │  ├─ index_documents()    │
        │ │  ├─ search()             │
        │ │  ├─ get_chunks()         │
        │ │  └─ get_all_chunks()     │
        │ │                          │
        │ └─ Storage: faiss_index    │
        │                            │
        │ Retrievers:                │
        │ ├─ DenseRetriever (vector) │
        │ ├─ SparseRetriever (BM25)  │
        │ ├─ Reranker (monoT5)       │
        │ └─ HyDE (hypothetical)     │
        │                            │
        │ Chunker:                   │
        │ └─ chunk_document()        │
        │    Size: 500, Overlap: 50  │
        │                            │
        │ Document Storage:          │
        │ ├─ Metadata:               │
        │ │  ├─ document_id          │
        │ │  ├─ user_id              │
        │ │  ├─ vendor               │
        │ │  ├─ amount               │
        │ │  ├─ date                 │
        │ │  ├─ category             │
        │ │  └─ source                │
        │ └─ Content: Receipt text   │
        └────────────────────────────┘
```

## Data Flow Sequences

### Goal Creation Sequence
```
User Input (voice/text)
    ↓
POST /goals/
    ↓
Pydantic: GoalCreate validation
    ↓
UserStorage.create_goal()
    ├─ Auto-create profile if needed
    ├─ Generate goal_id
    ├─ Calculate progress_percentage
    ├─ Set status to ON_TRACK
    └─ Save to JSON
    ↓
Return: {"status": "success", "goal_id": "..."}
```

### Goal Planning Sequence
```
GET /goals/{user_id}/{goal_id}/plan
    ↓
GoalPlannerAgent.create_plan()
    ├─ UserStorage.get_goal()
    ├─ PersonalFinanceAgent.analyze_dashboard()
    │   └─ VectorStore._get_user_receipts()
    ├─ Calculate months remaining
    ├─ InvestmentCalculator.recommend_asset_allocation()
    ├─ InvestmentCalculator.calculate_monthly_savings_needed()
    ├─ _generate_recommendations()
    │   └─ Identify overspending categories
    ├─ InvestmentCalculator.create_milestones()
    ├─ InvestmentCalculator.project_future_value()
    └─ Return complete plan
```

### Receipt Processing Sequence
```
POST /email/parse-receipt
    ↓
EmailReceiptParser.parse_email()
    ├─ _parse_with_ollama()
    │   ├─ OllamaClient.generate()
    │   └─ OllamaClient.parse_json_response()
    └─ _parse_with_regex() [if Ollama fails]
    ↓
Create receipt document with metadata
    ↓
chunk_document() → VectorStore.index_documents()
    ├─ Embed with sentence-transformers
    ├─ Store in FAISS
    └─ Save metadata
    ↓
Return: IngestionResponse
```

### Dashboard Analysis Sequence
```
GET /finance/dashboard/{user_id}
    ↓
PersonalFinanceAgent.analyze_dashboard(user_id, period)
    ├─ VectorStore._get_user_receipts()
    │   └─ Filter by user_id, date range
    ├─ _calculate_category_breakdown()
    ├─ _compare_to_budget()
    ├─ _group_by_month()
    ├─ _generate_insights()
    └─ Return dashboard JSON
```

### Audit Sequence
```
Receipt indexed in VectorStore
    ↓
AuditOrchestrator.run_audit()
    ├─ Step 1: AuditAgent.audit()
    │   ├─ _check_duplicates()
    │   ├─ _check_vendor_patterns()
    │   ├─ _check_totals()
    │   └─ _check_amount_anomalies()
    ├─ Step 2: ComplianceAgent.check_compliance()
    │   ├─ RAG retrieval of policy docs
    │   └─ LLM validation
    ├─ Step 3: FraudAgent.detect_fraud()
    │   ├─ _zscore_analysis()
    │   ├─ _isolation_forest_analysis()
    │   └─ _pattern_analysis()
    ├─ Step 4: ExplainabilityAgent.explain()
    └─ Return audit report
```

## Configuration & Settings

### backend/config.py
```python
LLM_PROVIDER = "ollama"
LLM_MODEL = "llama3.1:8b"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 1000
OLLAMA_BASE_URL = "http://172.16.163.34:11434"
OLLAMA_MODEL = "llama3.1:8b"

EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIM = 768
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

DENSE_TOP_K = 50
SPARSE_TOP_K = 30
RERANK_TOP_K = 5

AUDIT_THRESHOLD = 0.15
FRAUD_ZSCORE_THRESHOLD = 3.0
COMPLIANCE_CONFIDENCE = 0.7
```

## API Endpoints Summary

### Goals Management
- `POST /goals/` - Create goal
- `GET /goals/{user_id}` - List goals
- `GET /goals/{user_id}/{goal_id}` - Get goal
- `PUT /goals/{goal_id}` - Update goal
- `DELETE /goals/{goal_id}` - Delete goal

### Financial Analysis
- `GET /finance/dashboard/{user_id}` - Dashboard analysis
- `GET /finance/{user_id}/predictions` - Spending predictions
- `GET /finance/{user_id}/breakdown` - Spending breakdown
- `GET /finance/{user_id}/budget` - Budget recommendations

### Email Integration
- `POST /email/parse-receipt` - Parse email receipt

### Audit & Validation
- `POST /audit` - Run full audit
- `POST /audit/partial` - Run partial audit with selected agents

## Key Statistics

- **Total Agents**: 16 specialized agents
- **LLM Model**: Ollama llama3.1:8b
- **Temperature**: 0.1 (deterministic)
- **Embedding Dim**: 768
- **Chunk Size**: 500 tokens
- **Asset Allocation**: Conservative/Moderate/Aggressive based on horizon
- **Risk Thresholds**: Z-score 3.0, Fraud risk 0.7, Audit threshold 0.15

## Data Storage

**File-based persistence:**
- `/backend/data/user_data/{user_id}/profile.json` - User profile
- `/backend/data/user_data/{user_id}/goals.json` - Goals list

**Vector storage:**
- `/backend/data/vector_index.faiss` - FAISS index
- `/backend/data/chunks.jsonl` - Chunk metadata

**Optional MongoDB:**
- User registration (if connected)
- Not required for core functionality

## Receipt Categories & Vendors

**Common Categories:**
- dining: Zomato, Swiggy, restaurants
- groceries: BigBasket, DMart, supermarkets
- shopping: Amazon, Flipkart, e-commerce
- entertainment: Movies, subscriptions
- transportation: Travel, fuel, transit
- healthcare: Medical, pharmacy
- utilities: Bills, subscriptions
- travel: Hotels, flights
- other: Uncategorized

