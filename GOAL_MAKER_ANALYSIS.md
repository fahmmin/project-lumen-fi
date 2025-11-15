# Project Lumen - Goal Maker & Financial Analysis Architecture

## Overview
Project Lumen is an AI-native financial intelligence system with 16 specialized agents that work together to provide comprehensive financial analysis, goal planning, receipt processing, and spending insights.

---

## 1. GOAL CREATION FLOW - "I Want to Do This"

### Entry Points
- **API Endpoint**: `POST /goals/` (backend/routers/goals.py)
- **Voice Input**: Via `/voice` endpoint (transcribed to text)
- **Web UI**: Goals page in Next.js app

### Step-by-Step Goal Creation Flow

```
User Says: "I want to buy a car for $30,000 by 2029"
         ↓
[FastAPI Endpoint: POST /goals/]
         ↓
[GoalCreate Model Validation]
  - name: "Buy a Car"
  - target_amount: 30000.0
  - target_date: 2029-11-15
  - current_savings: 0.0
  - priority: MEDIUM
         ↓
[UserStorage.create_goal()]
  - Auto-create user profile if not exists
  - Generate goal_id: "goal_e0e9f39cb4f6"
  - Calculate progress_percentage: (current_savings / target_amount) * 100
  - Set status: "ON_TRACK" | "AHEAD" | "BEHIND" | "COMPLETED" | "ABANDONED"
         ↓
[Persist to File: /backend/data/user_data/{user_id}/goals.json]
  {
    "goal_id": "goal_e0e9f39cb4f6",
    "user_id": "test_user_001",
    "name": "Buy a Car",
    "target_amount": 30000.0,
    "target_date": "2029-11-14",
    "current_savings": 0.0,
    "progress_percentage": 0.0,
    "status": "on_track",
    "priority": "high",
    "monthly_contribution": null,
    "created_at": "2025-11-14T14:30:06.240060",
    "updated_at": "2025-11-14T14:30:06.240060"
  }
         ↓
[Return Success Response]
  {
    "status": "success",
    "message": "Goal created successfully",
    "goal_id": "goal_e0e9f39cb4f6",
    "name": "Buy a Car",
    "created_at": "2025-11-14T14:30:06.240060"
  }
```

## 2. GOAL STORAGE & DATA PERSISTENCE

### Storage Architecture
```
File System Structure:
/backend/data/user_data/
├── {user_id}/
│   ├── profile.json           # User profile with salary, budget
│   ├── goals.json             # Array of all user goals
│   └── receipts/              # Optional receipt directory
```

**Goal Model Structure:**
```python
{
  "goal_id": str,                    # Unique identifier
  "user_id": str,                    # Owner
  "name": str,                       # Goal name
  "target_amount": float,            # Target amount
  "target_date": date,               # Target date
  "current_savings": float,          # Current progress
  "progress_percentage": float,      # Calculated %
  "status": "on_track|ahead|behind|completed|abandoned",
  "priority": "low|medium|high|critical",
  "monthly_contribution": Optional[float],
  "created_at": datetime,
  "updated_at": datetime
}
```

## 3. RECEIPT ANALYSIS & CATEGORIZATION

### Receipt Processing Pipeline

```
Receipt Source: Email
         ↓
[Email Integration Router: POST /email/parse-receipt]
         ↓
[EmailReceiptParser: _parse_with_ollama()]
  LLM Prompt: "Extract receipt information from email"
  Model: Ollama (llama3.1:8b)
  Temperature: 0.1 (deterministic)
         ↓
[Extraction Results]
  {
    "vendor": "Zomato",
    "amount": 450.0,
    "date": "2024-12-10",
    "category": "dining",
    "items": ["Biryani", "Coke"],
    "confidence": 0.95,
    "method": "ollama"
  }
         ↓
[Fallback: Regex Patterns if Ollama fails]
  - Vendor patterns
  - Amount patterns (supports ₹, Rs, $)
  - Date patterns
         ↓
[Chunking & Vector Indexing]
  chunk_document(receipt_text, metadata)
         ↓
[Vector Store Indexing]
  - Embed receipt with sentence-transformers/all-mpnet-base-v2
  - Store metadata with receipt
  - Make searchable for RAG
         ↓
[Return IngestionResponse]
```

### Receipt Categories
- `dining`: Restaurants, food delivery (Zomato, Swiggy)
- `groceries`: Supermarkets, markets (BigBasket)
- `shopping`: E-commerce, retail (Amazon, Flipkart)
- `entertainment`: Movies, subscriptions
- `transportation`: Travel, fuel, transit
- `healthcare`: Medical, pharmacy
- `utilities`: Bills, subscriptions
- `travel`: Hotels, flights

## 4. SPENDING ANALYSIS & DECREASE SUGGESTIONS

### Personal Finance Agent Analysis

#### A. Dashboard Analysis - `analyze_dashboard(user_id, period)`

Returns comprehensive spending overview:
```python
{
  "summary": {
    "income": 5000.0,
    "total_spent": 2500.0,
    "savings": 2500.0,
    "savings_rate": 0.5
  },
  "spending_by_category": {
    "dining": {"amount": 800.0, "count": 12, "avg_per_transaction": 66.67},
    "groceries": {"amount": 1200.0, "count": 8, "avg_per_transaction": 150.0}
  },
  "vs_budget": {
    "dining": {
      "budget": 600.0,
      "actual": 800.0,
      "difference": -200.0,
      "status": "over",
      "percent_of_budget": 133.0
    }
  },
  "insights": [
    "You spent $800 on dining (33% over budget)",
    "Your savings rate (50%) is above average"
  ]
}
```

#### B. Spending Prediction - `predict_spending(user_id)`

ML-based forecasting for next month using 6+ months of history:
```python
{
  "predicted_total": 2650.0,
  "confidence_interval": [2400.0, 2900.0],
  "breakdown_by_category": {...},
  "factors": ["Historical average", "Seasonal trend detected", "Spending increasing"]
}
```

#### C. Spending Decrease Suggestions

The system generates specific recommendations by:
1. Identifying overspending categories (actual > budget)
2. Calculating specific reduction amounts
3. Ranking by impact and feasibility
4. Returning actionable recommendations

Example:
```python
recommendations = [
  "Reduce dining from $250 to $225 (saves $25/month)",
  "Cancel unused subscriptions (saves $35/month)",
  "Reduce shopping by 20% (saves $50/month)",
  "Total adjustments needed: $125/month"
]
```

## 5. GOAL PLANNER AGENT

### Create Savings Plan - `create_plan(goal_id, user_id)`

**Process:**
1. Calculate months remaining
2. Get current savings rate from PersonalFinanceAgent
3. Determine risk tolerance based on time horizon
4. Recommend asset allocation
5. Calculate monthly savings required
6. Identify gap (required - current)
7. Generate specific spending reduction recommendations
8. Create quarterly milestones
9. Project future value with compound returns

**Output:**
```python
{
  "goal_name": "Buy a Car",
  "target_amount": 30000.0,
  "months_remaining": 48,
  "plan": {
    "monthly_savings_required": 625.0,
    "current_savings_rate": 500.0,
    "gap": -125.0,
    "recommendations": [...]
  },
  "investment_strategy": {
    "time_horizon": "4.0 years",
    "risk_level": "moderate",
    "asset_allocation": {"stocks": 60, "bonds": 35, "cash": 5},
    "expected_return": 5.0,
    "projected_final_amount": 33500.0
  },
  "milestones": [
    {"date": "2026-02-14", "target": 7500.0},
    {"date": "2027-05-14", "target": 15000.0},
    {"date": "2028-08-14", "target": 22500.0},
    {"date": "2029-11-14", "target": 30000.0}
  ]
}
```

### Track Progress - `track_progress(goal_id, user_id)`

**Returns:**
- Current progress percentage
- On-track status
- Projected completion date vs target date
- Weekly/monthly ahead/behind calculation
- Adjustments needed for on-track

## 6. AGENT ARCHITECTURE

### 16 Specialized Agents

**Goal & Finance Planning:**
- GoalPlannerAgent: create_plan(), track_progress()
- PersonalFinanceAgent: analyze_dashboard(), predict_spending(), get_insights()
- InvestmentCalculator: Asset allocation, savings calculations

**Audit & Compliance:**
- AuditAgent: Duplicate checking, pattern validation, total verification
- ComplianceAgent: Policy checking via RAG
- AuditOrchestrator: Coordinates all audit agents

**Fraud & Patterns:**
- FraudAgent: Z-score, Isolation Forest, pattern analysis
- PatternAgent: Recurring expense detection
- BehavioralAgent: User behavior analysis

**Insights & Explanation:**
- ExplainabilityAgent: Human-readable report generation
- HealthScoreAgent: Financial health scoring

**Additional:**
- FamilyAnalyticsAgent
- SocialComparisonAgent
- GamificationAgent
- SubscriptionAgent
- ForensicsAgent

### Multi-Agent Audit Orchestrator Flow

```
Receipt Ingestion
         ↓
Step 1: AuditAgent
  - Check duplicates
  - Verify patterns
  - Validate totals
  - Detect anomalies
         ↓
Step 2: ComplianceAgent
  - RAG policy lookup
  - Regulation checking
  - Return violations
         ↓
Step 3: FraudAgent
  - Z-score analysis
  - ML anomaly detection
  - Pattern matching
  - Return risk score
         ↓
Step 4: ExplainabilityAgent
  - Generate summary
  - Connect context
  - Return explanation
         ↓
Step 5: Log Audit
  - Record audit_id
  - Save findings
  - Update workspace
         ↓
Return Complete Audit Report
```

## 7. LLM INTEGRATION

### Configuration (backend/config.py)
```python
LLM_PROVIDER: str = "ollama"
LLM_MODEL: str = "llama3.1:8b"
LLM_TEMPERATURE: float = 0.1  # Low = deterministic
LLM_MAX_TOKENS: int = 1000

OLLAMA_BASE_URL: str = "http://172.16.163.34:11434"
```

### Receipt Parsing with Ollama
- **Model**: llama3.1:8b (local, no API costs)
- **Temperature**: 0.1 (deterministic)
- **Handles**: Indian vendors, currency symbols (₹, Rs, $), number formatting
- **Output**: JSON with vendor, date, amount, category, items, confidence
- **Fallback**: Regex patterns if confidence < 0.5

### LLM Prompts (in config.py)
- **Receipt Extraction**: Parse vendor, amount, date, category from emails
- **Compliance Check**: Validate invoice against policies
- **Explanation**: Generate human-readable audit summaries

## 8. COMPLETE DATA FLOW

### Goal Creation to Plan Flow
```
User Input → API → GoalCreate Model → UserStorage.create_goal()
         → Persist to JSON → Return success + goal_id

Goal Plan Request → GoalPlannerAgent.create_plan()
         → Get savings rate from PersonalFinanceAgent
         → Calculate risk tolerance
         → InvestmentCalculator: Asset allocation
         → Calculate monthly savings needed
         → Identify gap
         → Generate recommendations
         → Return complete plan
```

### Receipt to Dashboard Flow
```
Email Receipt → EmailReceiptParser
         → Ollama LLM: Extract fields
         → VectorStore: Index with metadata
         → Audit checks pass
         → PersonalFinanceAgent: Incorporate into analysis
         → Dashboard: Category breakdown, insights, predictions
```

## 9. KEY FILES

### Core Models & APIs
- `/backend/models/goal.py`: Goal data models
- `/backend/models/user.py`: User profile models
- `/backend/routers/goals.py`: Goal CRUD API
- `/backend/routers/personal_finance.py`: Finance analysis API
- `/backend/routers/email_integration.py`: Email receipt parsing
- `/backend/utils/user_storage.py`: File-based persistence

### Agents
- `agents/goal_planner_agent.py`: Goal planning & tracking
- `agents/personal_finance_agent.py`: Spending analysis
- `agents/audit_agent.py`: Invoice validation
- `agents/compliance_agent.py`: Policy checking
- `agents/fraud_agent.py`: Anomaly detection
- `agents/pattern_agent.py`: Pattern detection
- `agents/orchestrator.py`: Multi-agent coordination

### Utilities
- `utils/email_parser.py`: Email receipt extraction
- `utils/llm_parser.py`: LLM document parsing
- `utils/investment_calculator.py`: Savings calculations
- `utils/ollama_client.py`: Ollama LLM interface
- `utils/time_series.py`: Forecasting

### Configuration
- `config.py`: Settings, LLM config, prompts
- `main.py`: FastAPI app setup

## 10. COMPLETE USER JOURNEY EXAMPLE

### Day 1: Create Goal
User: "I want to buy a car for $30,000 by November 2029"
System:
- Creates goal_id: "goal_e0e9f39cb4f6"
- Sets status: ON_TRACK
- Saves to goals.json
- Returns success

### Day 2: Generate Plan
User requests plan
System:
- Analyzes: 48 months remaining, $500/month current savings
- Recommends: Moderate risk allocation (60% stocks, 35% bonds, 5% cash)
- Calculates: Need $625/month (gap of -$125)
- Recommends: Reduce dining $25 + subscriptions $35 + shopping $50
- Projects: $33,500 by target date (exceeds goal!)
- Creates: Quarterly milestones

### Day 3: Link Receipt
Email: "Zomato Order Confirmed - Rs450"
System:
- Extracts: vendor=Zomato, amount=450, category=dining, confidence=0.95
- Indexes: In VectorStore with metadata
- Audits: No duplicates, amount valid, no anomalies
- Stores: For future analysis

### Week 1: Dashboard
System generates:
- Income: $5,000, Spent: $1,200, Savings: $3,800, Rate: 76%
- Dining: $250 (budget $200) - over by $50
- Insights: "You're saving 76%! On pace to exceed goal"

### Monthly: Progress
System calculates:
- Savings added: $750
- Total savings: $3,500
- Progress: 11.7%
- Status: AHEAD (8 weeks early!)
- Recommendation: "Keep current pace - you're ahead of schedule"

## Summary

Project Lumen provides:

1. **Goal Creation**: Voice/text-based goal setting with auto-profiles
2. **Receipt Processing**: Email extraction with Ollama LLM + auto-categorization
3. **Spending Analysis**: Dashboard, predictions, category breakdown, insights
4. **Decrease Suggestions**: Specific, actionable recommendations to close savings gaps
5. **Investment Planning**: Risk-based asset allocation and monthly savings requirements
6. **Progress Tracking**: Real-time progress updates with ahead/behind calculations
7. **Multi-Agent Audit**: Duplicate checking, compliance validation, fraud detection
8. **RAG Integration**: Policy-based compliance checking with context retrieval

All data persisted locally in JSON files with vector-indexed receipts for intelligent analysis.
