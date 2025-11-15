# Project Lumen - File Manifest

## Complete File Paths for Goal Maker & Financial Analysis

### Core Models
- `/home/user/project-lumen-fi/backend/models/goal.py` - Goal models (FinancialGoal, GoalCreate, GoalUpdate, GoalStatus, GoalPriority)
- `/home/user/project-lumen-fi/backend/models/user.py` - User profile models (UserProfile, UserProfileCreate, UserProfileUpdate)
- `/home/user/project-lumen-fi/backend/models/reminder.py` - Reminder and pattern models
- `/home/user/project-lumen-fi/backend/models/achievement.py` - Achievement models
- `/home/user/project-lumen-fi/backend/models/alert.py` - Alert models
- `/home/user/project-lumen-fi/backend/models/subscription.py` - Subscription models
- `/home/user/project-lumen-fi/backend/models/report.py` - Report models
- `/home/user/project-lumen-fi/backend/models/family.py` - Family models

### API Routers
- `/home/user/project-lumen-fi/backend/routers/goals.py` - Goals CRUD endpoints
- `/home/user/project-lumen-fi/backend/routers/personal_finance.py` - Financial analysis endpoints
- `/home/user/project-lumen-fi/backend/routers/email_integration.py` - Email receipt parsing endpoints
- `/home/user/project-lumen-fi/backend/routers/ingest.py` - Document ingestion endpoints
- `/home/user/project-lumen-fi/backend/routers/audit.py` - Audit endpoints
- `/home/user/project-lumen-fi/backend/routers/users.py` - User profile endpoints
- `/home/user/project-lumen-fi/backend/routers/reminders.py` - Reminder management endpoints
- `/home/user/project-lumen-fi/backend/routers/subscriptions.py` - Subscription management endpoints
- `/home/user/project-lumen-fi/backend/routers/gamification.py` - Gamification endpoints
- `/home/user/project-lumen-fi/backend/routers/forensics.py` - Forensics analysis endpoints
- `/home/user/project-lumen-fi/backend/routers/voice.py` - Voice input endpoints
- `/home/user/project-lumen-fi/backend/routers/family.py` - Family analytics endpoints
- `/home/user/project-lumen-fi/backend/routers/social.py` - Social comparison endpoints
- `/home/user/project-lumen-fi/backend/routers/reports.py` - Report generation endpoints
- `/home/user/project-lumen-fi/backend/routers/websocket.py` - WebSocket connections
- `/home/user/project-lumen-fi/backend/routers/memory.py` - Memory management endpoints

### Agent Implementations (16 Total)
- `/home/user/project-lumen-fi/backend/agents/goal_planner_agent.py` - Goal planning and tracking agent
- `/home/user/project-lumen-fi/backend/agents/personal_finance_agent.py` - Spending analysis and predictions agent
- `/home/user/project-lumen-fi/backend/agents/audit_agent.py` - Invoice validation agent
- `/home/user/project-lumen-fi/backend/agents/compliance_agent.py` - Policy compliance checking agent
- `/home/user/project-lumen-fi/backend/agents/fraud_agent.py` - Fraud detection agent
- `/home/user/project-lumen-fi/backend/agents/pattern_agent.py` - Recurring expense pattern detection agent
- `/home/user/project-lumen-fi/backend/agents/explainability_agent.py` - Human-readable explanation generation agent
- `/home/user/project-lumen-fi/backend/agents/health_score_agent.py` - Financial health scoring agent
- `/home/user/project-lumen-fi/backend/agents/behavioral_agent.py` - User behavior analysis agent
- `/home/user/project-lumen-fi/backend/agents/family_analytics_agent.py` - Family spending analysis agent
- `/home/user/project-lumen-fi/backend/agents/social_comparison_agent.py` - Peer comparison agent
- `/home/user/project-lumen-fi/backend/agents/subscription_agent.py` - Subscription management agent
- `/home/user/project-lumen-fi/backend/agents/gamification_agent.py` - Achievement and badge agent
- `/home/user/project-lumen-fi/backend/agents/forensics_agent.py` - Image forensics analysis agent
- `/home/user/project-lumen-fi/backend/agents/orchestrator.py` - Multi-agent orchestrator
- `/home/user/project-lumen-fi/backend/agents/__init__.py` - Agent package initialization

### Utilities
- `/home/user/project-lumen-fi/backend/utils/user_storage.py` - File-based user data persistence
- `/home/user/project-lumen-fi/backend/utils/email_parser.py` - Email receipt extraction parser
- `/home/user/project-lumen-fi/backend/utils/llm_parser.py` - LLM-based document parser
- `/home/user/project-lumen-fi/backend/utils/ollama_client.py` - Ollama LLM client interface
- `/home/user/project-lumen-fi/backend/utils/investment_calculator.py` - Investment and savings calculations
- `/home/user/project-lumen-fi/backend/utils/time_series.py` - Time series forecasting utilities
- `/home/user/project-lumen-fi/backend/utils/logger.py` - Logging utilities
- `/home/user/project-lumen-fi/backend/utils/alert_manager.py` - Alert management utilities
- `/home/user/project-lumen-fi/backend/utils/workspace_writer.py` - Workspace file management
- `/home/user/project-lumen-fi/backend/utils/mongo_storage.py` - MongoDB storage interface
- `/home/user/project-lumen-fi/backend/utils/family_storage.py` - Family data storage
- `/home/user/project-lumen-fi/backend/utils/text_extract.py` - Text extraction utilities
- `/home/user/project-lumen-fi/backend/utils/image_forensics.py` - Image analysis utilities
- `/home/user/project-lumen-fi/backend/utils/voice_processor.py` - Voice processing utilities
- `/home/user/project-lumen-fi/backend/utils/pdf_generator.py` - PDF report generation
- `/home/user/project-lumen-fi/backend/utils/__init__.py` - Utils package initialization

### RAG System
- `/home/user/project-lumen-fi/backend/rag/vector_store.py` - FAISS vector store implementation
- `/home/user/project-lumen-fi/backend/rag/retriever.py` - Document retrieval interface
- `/home/user/project-lumen-fi/backend/rag/chunker.py` - Document chunking utilities
- `/home/user/project-lumen-fi/backend/rag/sparse_retriever.py` - BM25 sparse retriever
- `/home/user/project-lumen-fi/backend/rag/reranker.py` - Reranking utilities
- `/home/user/project-lumen-fi/backend/rag/hyde.py` - HyDE (Hypothetical Documents) generator
- `/home/user/project-lumen-fi/backend/rag/__init__.py` - RAG package initialization

### Configuration & Main
- `/home/user/project-lumen-fi/backend/config.py` - Settings, LLM config, prompts
- `/home/user/project-lumen-fi/backend/main.py` - FastAPI application entry point
- `/home/user/project-lumen-fi/backend/seed_data.py` - Test data seeding

### Data Files
- `/home/user/project-lumen-fi/backend/data/user_data/test_user_001/goals.json` - Sample user goals
- `/home/user/project-lumen-fi/backend/data/user_data/test_user_001/profile.json` - Sample user profile
- `/home/user/project-lumen-fi/backend/data/user_data/{user_id}/goals.json` - Per-user goals storage
- `/home/user/project-lumen-fi/backend/data/user_data/{user_id}/profile.json` - Per-user profile storage

### Frontend
- `/home/user/project-lumen-fi/nextjs-app/app/goals/page.tsx` - Goals management UI
- `/home/user/project-lumen-fi/nextjs-app/app/finance/page.tsx` - Financial dashboard UI
- `/home/user/project-lumen-fi/nextjs-app/app/email/page.tsx` - Email integration UI
- `/home/user/project-lumen-fi/nextjs-app/app/voice/page.tsx` - Voice input UI
- `/home/user/project-lumen-fi/nextjs-app/services/api.ts` - API client service
- `/home/user/project-lumen-fi/nextjs-app/contexts/UserContext.tsx` - User context provider

### Documentation
- `/home/user/project-lumen-fi/GOAL_MAKER_ANALYSIS.md` - Comprehensive analysis (THIS FILE GENERATED)
- `/home/user/project-lumen-fi/ARCHITECTURE_QUICK_REFERENCE.md` - Architecture reference (THIS FILE GENERATED)
- `/home/user/project-lumen-fi/FILE_MANIFEST.md` - This file

---

## Key Code Snippets

### Goal Creation Model
**File**: `/home/user/project-lumen-fi/backend/models/goal.py`
```python
class GoalCreate(BaseModel):
    user_id: str
    name: str
    target_amount: float
    target_date: date
    current_savings: float = 0.0
    priority: GoalPriority = GoalPriority.MEDIUM

class FinancialGoal(BaseModel):
    goal_id: str
    user_id: str
    name: str
    target_amount: float
    target_date: date
    current_savings: float = 0.0
    progress_percentage: float = 0.0
    status: GoalStatus = GoalStatus.ON_TRACK
```

### Goal Storage Implementation
**File**: `/home/user/project-lumen-fi/backend/utils/user_storage.py`
```python
def create_goal(self, goal_data: GoalCreate) -> FinancialGoal:
    # Auto-create profile if needed
    # Generate goal_id
    # Calculate progress
    # Persist to JSON
```

### Goal Planning
**File**: `/home/user/project-lumen-fi/backend/agents/goal_planner_agent.py`
```python
def create_plan(self, goal_id: str, user_id: str) -> Dict:
    # Get goal and calculate months remaining
    # Get current savings rate from PersonalFinanceAgent
    # Calculate risk tolerance
    # Get asset allocation from InvestmentCalculator
    # Calculate monthly savings needed
    # Generate recommendations based on spending analysis
    # Create milestones
    # Project future value
```

### Receipt Parsing with LLM
**File**: `/home/user/project-lumen-fi/backend/utils/email_parser.py`
```python
def parse_email(self, email_text: str, subject: str = "") -> Dict:
    # Try Ollama LLM parsing first
    # Fallback to regex if Ollama fails or low confidence
    # Return extracted: vendor, amount, date, category, items, confidence
```

### Spending Analysis
**File**: `/home/user/project-lumen-fi/backend/agents/personal_finance_agent.py`
```python
def analyze_dashboard(self, user_id: str, period: str = "month") -> Dict:
    # Get user receipts from VectorStore
    # Calculate spending by category
    # Compare to budget
    # Generate insights
    # Return dashboard data
```

### Multi-Agent Audit Orchestration
**File**: `/home/user/project-lumen-fi/backend/agents/orchestrator.py`
```python
def run_audit(self, invoice_data: Dict) -> Dict:
    # Step 1: AuditAgent - validate invoice
    # Step 2: ComplianceAgent - check policies
    # Step 3: FraudAgent - detect anomalies
    # Step 4: ExplainabilityAgent - generate summary
    # Step 5: Log to workspace
```

---

## Environment Configuration

**File**: `/home/user/project-lumen-fi/backend/config.py`

```python
# LLM Settings
LLM_PROVIDER = "ollama"
LLM_MODEL = "llama3.1:8b"
OLLAMA_BASE_URL = "http://172.16.163.34:11434"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 1000

# Embedding
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBEDDING_DIM = 768

# Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Retrieval
DENSE_TOP_K = 50
SPARSE_TOP_K = 30
RERANK_TOP_K = 5

# Thresholds
AUDIT_THRESHOLD = 0.15
FRAUD_ZSCORE_THRESHOLD = 3.0
COMPLIANCE_CONFIDENCE = 0.7
```

---

## API Entry Points Summary

### Goal Management
```
POST   /goals/                          - Create goal
GET    /goals/{user_id}                 - List goals
GET    /goals/{user_id}/{goal_id}       - Get goal details
PUT    /goals/{goal_id}                 - Update goal
DELETE /goals/{goal_id}                 - Delete goal
GET    /goals/{user_id}/{goal_id}/plan  - Generate savings plan
GET    /goals/{user_id}/{goal_id}/progress - Track progress
```

### Financial Analysis
```
GET  /finance/dashboard/{user_id}           - Dashboard with spending overview
GET  /finance/{user_id}/breakdown           - Detailed spending breakdown
GET  /finance/{user_id}/predictions         - Spending predictions
GET  /finance/{user_id}/budget              - Budget recommendations
GET  /insights/{user_id}                    - Spending insights
```

### Receipt Processing
```
POST /email/parse-receipt              - Extract receipt from email
POST /ingest                           - Ingest document (PDF/image)
GET  /documents/{user_id}              - List user documents
```

### Audit & Compliance
```
POST /audit                            - Run full multi-agent audit
POST /audit/partial                    - Run partial audit with selected agents
GET  /audit/{audit_id}                 - Get audit results
```

---

## Data Flow Summary

1. **Goal Creation**: User input → API → Validation → Storage → Response
2. **Goal Planning**: Goal ID → Agent → Analysis → Recommendation → Plan
3. **Receipt Ingestion**: Email → Parser → LLM → Vector indexing → Storage
4. **Spending Analysis**: Query → VectorStore retrieval → Calculation → Dashboard
5. **Audit**: Receipt → Agent orchestrator → Multi-stage validation → Report

---

## Execution Flow for Goal Maker

```
User: "I want to buy a car for $30,000 by 2029"
                    ↓
        POST /goals/ with GoalCreate
                    ↓
        UserStorage.create_goal()
        - Auto-create profile
        - Generate goal_id
        - Calculate initial progress (0%)
        - Save to JSON
                    ↓
        Return goal_id to frontend
                    ↓
        User requests plan
                    ↓
        GoalPlannerAgent.create_plan()
        - Get current savings rate
        - Calculate months remaining (48)
        - Recommend asset allocation (60/35/5)
        - Calculate monthly need ($625)
        - Identify gap ($125/month)
        - Generate spending recommendations
        - Create milestones
        - Project final amount ($33,500)
                    ↓
        Return complete plan to user
```

---

## Complete Codebase Statistics

- **Total Agents**: 16 specialized agents
- **Total Routers**: 16 API route files
- **Total Models**: 7 core models
- **Total Utilities**: 16 utility files
- **RAG Components**: 7 files (vector store, retrievers, chunker, reranker)
- **Configuration Files**: 2 main config files
- **Lines of Code**: ~10,000+ lines of Python
- **LLM Integration**: Ollama llama3.1:8b (local, no API costs)
- **Storage**: JSON files + FAISS vector index
- **Frontend**: Next.js with React components

