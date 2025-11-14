# PROJECT LUMEN - Feature Gap Analysis & Enhancement Roadmap

## 📊 Executive Summary

This document analyzes the current state of PROJECT LUMEN, identifies gaps against the proposed personal finance features, and provides a detailed architectural roadmap for implementation.

---

## 🎯 Current State: What's Already Built

### ✅ Core Infrastructure (PRODUCTION READY)

#### 1. **Document Processing Pipeline**
- ✅ PDF extraction (pdfminer.six)
- ✅ Image OCR (pytesseract)
- ✅ LLM-based structured data extraction
- ✅ Invoice/receipt parsing to JSON
- ✅ File upload API (`POST /ingest/`)

#### 2. **RAG System (Hybrid Retrieval)**
- ✅ Dense embeddings (all-mpnet-base-v2, 768-dim)
- ✅ Vector store (FAISS, local)
- ✅ Sparse retrieval (BM25)
- ✅ HyDE (Hypothetical Document Embeddings)
- ✅ MonoT5 reranking
- ✅ Persistent indices (chunks.jsonl, vector_index.faiss)

#### 3. **Multi-Agent System**
- ✅ **Audit Agent**: Duplicate detection, pattern analysis, total verification
- ✅ **Compliance Agent**: RAG-powered policy validation
- ✅ **Fraud Agent**: Z-score, Isolation Forest, pattern-based fraud detection
- ✅ **Explainability Agent**: Natural language summaries
- ✅ **Orchestrator**: Coordinates all agents

#### 4. **Memory & Persistence**
- ✅ Workspace.md (persistent markdown memory)
- ✅ Historical transaction storage in vector store
- ✅ Search and stats APIs

#### 5. **Current Fraud Detection Capabilities**
- ✅ Statistical anomaly detection (Z-score > 3σ)
- ✅ ML-based anomaly detection (Isolation Forest)
- ✅ Pattern analysis:
  - Multiple invoices same vendor/day
  - Round number amounts
  - Amounts near approval thresholds
  - Vendor name variations
  - Missing invoice numbers
- ❌ **NOT BUILT**: Image forensics (photoshop detection)

---

## 🚀 Proposed New Features (User Requirements)

### 1. **Image Authenticity Detection**
**Goal**: Detect photoshopped/manipulated receipt images

**Current State**: ❌ NOT IMPLEMENTED
- Fraud agent only detects *numeric anomalies*, not *image manipulation*

### 2. **Personal Finance Dashboard**
**Goal**: Track user's receipts → show expenditure insights

**Current State**: ❌ NOT IMPLEMENTED
- Current system is for *invoice auditing*, not *personal spending tracking*

### 3. **Income vs Spending Intelligence**
**Goal**: User inputs salary → system shows:
- How much spent vs income
- Spending predictions (next month)
- Budget control recommendations

**Current State**: ❌ NOT IMPLEMENTED
- No user profile/salary tracking
- No predictive spending models

### 4. **Goal-Based Financial Planning**
**Goal**: "Buy a $30K car in 4 years → tell me how much to save/invest"

**Current State**: ❌ NOT IMPLEMENTED
- No goal tracking system
- No investment recommendation engine

### 5. **Smart Purchase Reminders**
**Goal**: Analyze monthly receipts → detect patterns → send reminders

**Current State**: ⚠️ PARTIALLY IMPLEMENTED
- Pattern detection exists (vendor analysis in Audit Agent)
- No reminder system or calendar integration

---

## 🔍 Detailed Gap Analysis

| Feature | Status | Existing Components to Leverage | What Needs Building |
|---------|--------|--------------------------------|---------------------|
| **Image Forensics** | ❌ Missing | Document ingestion pipeline | ELA analysis, metadata forensics, CNN-based detector |
| **Personal Finance Dashboard** | ❌ Missing | Vector store (for receipts), workspace memory | User profiles, spending categorization UI, analytics engine |
| **Income Tracking** | ❌ Missing | None | User profile system, income input API |
| **Spending Predictions** | ❌ Missing | RAG system (historical data), fraud agent (pattern detection) | Time-series forecasting model, budget prediction agent |
| **Goal Planning** | ❌ Missing | RAG (financial product knowledge), agents | Goal tracking system, investment recommendation agent |
| **Smart Reminders** | ⚠️ Partial | Audit agent (pattern detection), workspace memory | Recurring pattern detection agent, notification system |
| **Expense Categorization** | ✅ Exists | LLM parser extracts category from receipts | Refinement for personal finance categories |
| **Anomaly Detection** | ✅ Exists | Fraud agent (Z-score, Isolation Forest) | Adapt for personal spending patterns |

---

## 🏗️ Proposed Architecture for New Features

### **Phase 1: Image Authenticity Detection**

#### Components to Build:

##### 1. **Image Forensics Agent** (`backend/agents/forensics_agent.py`)
```python
class ForensicsAgent:
    def analyze_image(self, image_path: str) -> Dict:
        """
        Detects image manipulation

        Methods:
        1. Error Level Analysis (ELA) - JPEG compression artifacts
        2. EXIF metadata verification - camera, timestamp, GPS
        3. Clone detection - copy-paste regions
        4. Lighting inconsistency detection
        5. CNN-based deepfake detector (optional)

        Returns:
            {
                "authentic": bool,
                "confidence": float,
                "manipulation_indicators": List[str],
                "risk_score": float
            }
        """
```

##### 2. **Image Processing Utilities** (`backend/utils/image_forensics.py`)
- ELA (Error Level Analysis) implementation
- EXIF parser (using Pillow)
- Clone stamp detection (using OpenCV)
- Lighting analysis (using image gradients)

##### 3. **New Dependencies**
```txt
opencv-python>=4.8.0  # Image processing
pillow>=10.1.0        # EXIF extraction
scikit-image>=0.22.0  # Image forensics algorithms
```

##### 4. **Integration Point**
- Extend `/ingest/` endpoint to run ForensicsAgent on uploaded images
- Add new field to response: `"image_authenticity": {...}`

---

### **Phase 2: Personal Finance Dashboard**

#### Components to Build:

##### 1. **User Profile System** (`backend/models/user.py`)
```python
class UserProfile:
    user_id: str
    name: str
    salary_monthly: float
    currency: str = "USD"
    financial_goals: List[FinancialGoal]
    budget_categories: Dict[str, float]  # e.g., {"groceries": 500, "rent": 1500}
    created_at: datetime
    updated_at: datetime
```

##### 2. **Personal Finance Agent** (`backend/agents/personal_finance_agent.py`)
```python
class PersonalFinanceAgent:
    def analyze_spending(self, user_id: str) -> Dict:
        """
        Analyzes user's spending patterns

        Uses:
        - RAG to retrieve user's historical receipts from vector store
        - Categorizes spending by month/category
        - Compares to salary

        Returns:
            {
                "total_spent_this_month": float,
                "income_this_month": float,
                "savings_rate": float,
                "spending_by_category": Dict[str, float],
                "vs_last_month": float,  # % change
                "insights": List[str]
            }
        """

    def predict_next_month(self, user_id: str) -> Dict:
        """
        Predicts next month's spending using time-series analysis

        Uses:
        - RAG to get last 6-12 months of data
        - Simple moving average or ARIMA model

        Returns:
            {
                "predicted_spending": float,
                "confidence_interval": (float, float),
                "breakdown_by_category": Dict[str, float]
            }
        """

    def get_budget_recommendations(self, user_id: str) -> List[str]:
        """
        Uses RAG + LLM to suggest budget cuts

        Example output:
        - "You spent $450 on dining out (30% over budget) - try reducing to $350"
        - "Your grocery spending is $200 below average - well done!"
        """
```

##### 3. **New API Endpoints** (`backend/routers/personal_finance.py`)
```python
POST /users/profile         # Create/update user profile
GET  /users/profile/{user_id}
POST /users/profile/{user_id}/salary

GET  /finance/dashboard/{user_id}   # Main dashboard data
GET  /finance/spending/{user_id}?period=month
GET  /finance/predictions/{user_id}
GET  /finance/insights/{user_id}
```

##### 4. **Enhanced Receipt Storage**
- Modify ingestion to tag receipts with `user_id`
- Store user-specific metadata in vector store chunks
- Add user filtering to RAG retrieval

---

### **Phase 3: Goal-Based Financial Planning**

#### Components to Build:

##### 1. **Goal Planning Agent** (`backend/agents/goal_planner_agent.py`)
```python
class GoalPlannerAgent:
    def create_plan(self, goal: FinancialGoal, user_profile: UserProfile) -> Dict:
        """
        Creates savings/investment plan for a goal

        Steps:
        1. RAG retrieves:
           - User's current spending patterns
           - Average savings rate
           - Historical investment returns (from financial product DB)

        2. Calculate:
           - Monthly savings needed
           - Gap from current savings rate
           - Investment allocation (based on time horizon)

        3. LLM generates:
           - Actionable recommendations
           - Where to cut spending
           - Investment strategy

        Returns:
            {
                "goal": FinancialGoal,
                "monthly_savings_required": float,
                "current_savings_rate": float,
                "gap": float,
                "recommendations": List[str],
                "investment_strategy": {
                    "asset_allocation": Dict[str, float],
                    "expected_return": float,
                    "risk_level": str
                },
                "milestones": List[Milestone]
            }
        """

    def track_progress(self, goal_id: str, user_id: str) -> Dict:
        """
        Tracks progress toward goal

        Uses RAG to:
        - Get goal details
        - Retrieve actual savings since goal creation
        - Compare to plan

        Returns:
            {
                "goal": FinancialGoal,
                "progress_percentage": float,
                "on_track": bool,
                "projected_completion_date": date,
                "adjustments_needed": List[str]
            }
        """
```

##### 2. **Financial Product RAG Database**
- Create `backend/data/financial_products/` with documents on:
  - Index funds (expected returns, risk profiles)
  - Bonds, FDs, savings accounts
  - Tax-advantaged accounts (401k, IRA, etc.)
- Index these documents in RAG system
- Use for investment recommendations

##### 3. **Goal Tracking Models** (`backend/models/goal.py`)
```python
class FinancialGoal:
    goal_id: str
    user_id: str
    name: str  # "Buy a car"
    target_amount: float  # 30000
    target_date: date  # 4 years from now
    current_savings: float
    monthly_contribution: float
    investment_return_assumption: float
    status: str  # "on_track", "behind", "ahead"
    created_at: datetime
```

##### 4. **New API Endpoints**
```python
POST /goals/                    # Create new goal
GET  /goals/{user_id}           # List user's goals
GET  /goals/{goal_id}           # Goal details
GET  /goals/{goal_id}/plan      # Get savings plan
GET  /goals/{goal_id}/progress  # Track progress
PUT  /goals/{goal_id}/milestone # Update progress
```

---

### **Phase 4: Smart Purchase Reminders**

#### Components to Build:

##### 1. **Pattern Detection Agent** (`backend/agents/pattern_agent.py`)
```python
class PatternAgent:
    def detect_recurring_expenses(self, user_id: str) -> List[RecurringPattern]:
        """
        Uses RAG + time-series analysis to find patterns

        Steps:
        1. RAG retrieves all user's receipts (6-12 months)
        2. Group by:
           - Vendor (e.g., "Whole Foods")
           - Category (e.g., "Groceries")
           - Amount similarity
        3. Detect frequency:
           - Weekly, bi-weekly, monthly patterns
           - Day-of-month patterns (e.g., "10th of every month")

        Returns:
            [
                {
                    "pattern_type": "monthly_grocery",
                    "vendor": "Whole Foods",
                    "category": "Groceries",
                    "typical_amount": 450.0,
                    "typical_day": 10,  # 10th of month
                    "confidence": 0.85,
                    "last_purchase": "2025-10-12",
                    "next_expected": "2025-11-10"
                }
            ]
        """

    def generate_reminders(self, user_id: str) -> List[Reminder]:
        """
        Generates proactive reminders

        Examples:
        - "You usually buy groceries around the 10th — time to restock!"
        - "Your electricity bill is due next week (typically $120)"
        - "You haven't paid rent yet this month"
        """
```

##### 2. **Reminder System** (`backend/utils/reminder_system.py`)
- Cron job or scheduled task (daily check)
- Sends notifications via:
  - Email (using SMTP)
  - Push notifications (optional)
  - In-app alerts

##### 3. **New API Endpoints**
```python
GET  /reminders/{user_id}           # Active reminders
GET  /patterns/{user_id}            # Detected patterns
POST /patterns/{pattern_id}/snooze  # Dismiss reminder
```

---

### **Phase 5: Advanced Spending Insights**

#### Components to Build:

##### 1. **Behavioral Finance Agent** (`backend/agents/behavioral_agent.py`)
```python
class BehavioralAgent:
    def analyze_spending_psychology(self, user_id: str) -> Dict:
        """
        Detects emotional spending patterns

        Uses RAG + NLP to correlate:
        - High spending periods with calendar events (weekends, holidays)
        - Impulse purchases (quick successive transactions)
        - Stress spending indicators

        Returns:
            {
                "impulse_score": float,
                "patterns": [
                    "You spend 2x more on weekends",
                    "Retail therapy detected - $300 impulse buys after work trips"
                ],
                "recommendations": [
                    "Set a weekend spending limit",
                    "Use 24-hour rule for purchases over $100"
                ]
            }
        """
```

##### 2. **Merchant Intelligence Agent** (`backend/agents/merchant_agent.py`)
```python
class MerchantAgent:
    def price_comparison(self, receipt_data: Dict) -> Dict:
        """
        Compares prices across merchants

        Uses RAG to:
        - Find historical prices for same item
        - Suggest cheaper alternatives

        Requires:
        - Product database or API integration (e.g., CamelCamelCamel for Amazon)

        Returns:
            {
                "item": "Milk - 1 gallon",
                "price_paid": 5.99,
                "average_price": 4.50,
                "overpaid": 1.49,
                "alternatives": [
                    {"merchant": "Costco", "price": 4.50},
                    {"merchant": "Walmart", "price": 4.75}
                ]
            }
        """
```

---

## 🧠 RAG & Agent Strategy for New Features

### **How RAG Powers Personal Finance**

#### 1. **User Receipt History as Knowledge Base**
```
User's receipts → Chunked → Embedded → FAISS index (user-specific)
                                          ↓
                            Query: "What did I spend on groceries last month?"
                                          ↓
                            RAG retrieves relevant receipts → LLM summarizes
```

#### 2. **Financial Product Database**
```
Mutual funds, bonds, index funds docs → Chunked → Embedded → Separate FAISS index
                                                                ↓
Goal: "Buy car in 4 years" → RAG retrieves investment options with 4-year horizon
                                                                ↓
                                    LLM recommends: "60% index funds, 40% bonds"
```

#### 3. **Spending Pattern Retrieval**
```
Query: "How much do I usually spend on dining out?"
    ↓
RAG retrieves last 12 months of restaurant receipts
    ↓
LLM calculates average: "$450/month, 15% increase vs last year"
```

### **Agent Orchestration for New Features**

#### Example: Goal Planning Workflow
```
User: "I want to buy a $30K car in 4 years"
    ↓
[ORCHESTRATOR]
    ↓
    ├─→ [Personal Finance Agent]
    │      ↓
    │   RAG retrieves: Current income, spending patterns, savings rate
    │   Returns: "You save $400/month currently"
    │
    ├─→ [Goal Planner Agent]
    │      ↓
    │   Calculates: Need $625/month, Gap = $225/month
    │   RAG retrieves: Investment products with 4-year horizon
    │   LLM recommends: Asset allocation (60% stocks, 40% bonds)
    │
    ├─→ [Behavioral Agent]
    │      ↓
    │   RAG analyzes: Spending patterns
    │   Suggests: "Cut dining out by $150, reduce subscriptions by $75"
    │
    └─→ [Explainability Agent]
           ↓
        Generates: Natural language plan
        "To buy a $30K car in 4 years, save $625/month. You currently save $400/month,
         so you need to save an extra $225/month. I recommend cutting dining out from
         $450 to $300 and canceling unused subscriptions ($75). Invest in a balanced
         portfolio (60% stocks, 40% bonds) for a 6% annual return."
```

---

## 💡 Additional Innovative Features (Beyond User's Request)

### 1. **Financial Health Score**
```python
class HealthScoreAgent:
    def calculate_score(self, user_id: str) -> int:
        """
        0-100 score based on:
        - Debt-to-income ratio (25%)
        - Emergency fund adequacy (25%)
        - Savings rate (20%)
        - Spending volatility (15%)
        - Goal progress (15%)

        Uses RAG to get historical data for all metrics
        """
```

### 2. **Subscription Bloodhound**
```python
class SubscriptionAgent:
    def detect_subscriptions(self, user_id: str) -> List[Subscription]:
        """
        RAG finds recurring charges → Identifies subscriptions

        Flags:
        - Unused subscriptions (no related app usage data)
        - Price increases
        - Cheaper alternatives
        """
```

### 3. **Tax Optimization Co-Pilot**
```python
class TaxAgent:
    def categorize_for_taxes(self, user_id: str) -> Dict:
        """
        RAG retrieves all receipts → Categorizes for tax deductions

        Categories:
        - Business expenses (home office, equipment)
        - Medical expenses
        - Charitable donations

        Generates tax-ready CSV report
        """
```

### 4. **Cashback Maximizer**
```python
class CashbackAgent:
    def optimize_card_usage(self, receipt_data: Dict) -> str:
        """
        RAG stores user's credit cards + reward structures

        Before purchase:
        "Use Chase card — 5% cashback on groceries this quarter"

        After purchase:
        "You could have earned $15 more with Amex Blue Cash"
        """
```

### 5. **Life Event Forecaster**
```python
class LifeEventAgent:
    def predict_major_expenses(self, user_profile: UserProfile) -> List[Prediction]:
        """
        Based on age, location, life stage:
        - "Expect $5K in car repairs in next 2 years"
        - "Average wedding costs $30K — start saving if engaged"

        Uses RAG + demographic financial data
        """
```

### 6. **Debt Destroyer Agent**
```python
class DebtAgent:
    def optimize_payoff(self, user_debts: List[Debt]) -> Dict:
        """
        Analyzes all debts (credit cards, loans)

        Recommends:
        - Avalanche vs Snowball strategy
        - Optimal payment allocation

        "Pay extra $100 to Card A — you'll save $340 in interest over 2 years"
        """
```

---

## 🗂️ Proposed File Structure (New Components)

```
backend/
├── agents/
│   ├── forensics_agent.py          # ✨ NEW - Image authenticity
│   ├── personal_finance_agent.py   # ✨ NEW - Spending analysis & predictions
│   ├── goal_planner_agent.py       # ✨ NEW - Goal-based planning
│   ├── pattern_agent.py            # ✨ NEW - Recurring expense detection
│   ├── behavioral_agent.py         # ✨ NEW - Emotional spending patterns
│   ├── merchant_agent.py           # ✨ NEW - Price comparison
│   ├── subscription_agent.py       # ✨ NEW - Subscription detection
│   ├── tax_agent.py                # ✨ NEW - Tax optimization
│   ├── cashback_agent.py           # ✨ NEW - Reward optimization
│   └── debt_agent.py               # ✨ NEW - Debt payoff strategy
│
├── models/
│   ├── user.py                     # ✨ NEW - User profile models
│   ├── goal.py                     # ✨ NEW - Financial goal models
│   ├── subscription.py             # ✨ NEW - Subscription tracking
│   └── debt.py                     # ✨ NEW - Debt tracking
│
├── routers/
│   ├── personal_finance.py         # ✨ NEW - Personal finance APIs
│   ├── goals.py                    # ✨ NEW - Goal management APIs
│   ├── reminders.py                # ✨ NEW - Reminder APIs
│   └── users.py                    # ✨ NEW - User profile APIs
│
├── utils/
│   ├── image_forensics.py          # ✨ NEW - ELA, EXIF, clone detection
│   ├── time_series.py              # ✨ NEW - Forecasting utilities
│   ├── reminder_system.py          # ✨ NEW - Notification system
│   └── investment_calculator.py    # ✨ NEW - Investment math
│
└── data/
    ├── financial_products/         # ✨ NEW - Investment product docs
    ├── tax_rules/                  # ✨ NEW - Tax deduction rules
    └── user_data/                  # ✨ NEW - User-specific data
        └── {user_id}/
            ├── receipts/
            ├── goals.json
            └── profile.json
```

---

## 🚦 Implementation Roadmap

### **Sprint 1: Foundation (2-3 days)**
- [ ] User profile system (models + APIs)
- [ ] Enhance ingestion to support user_id tagging
- [ ] Modify vector store to filter by user_id
- [ ] Basic personal finance agent (spending analysis)

### **Sprint 2: Image Forensics (2-3 days)**
- [ ] Forensics agent (ELA, EXIF, basic checks)
- [ ] Image forensics utilities (OpenCV integration)
- [ ] Integrate with /ingest/ endpoint
- [ ] Add authenticity score to UI

### **Sprint 3: Predictions & Insights (3-4 days)**
- [ ] Time-series forecasting for spending
- [ ] Budget recommendation logic
- [ ] Personal finance dashboard API
- [ ] Frontend dashboard UI

### **Sprint 4: Goal Planning (3-4 days)**
- [ ] Goal tracking models
- [ ] Goal planner agent
- [ ] Financial product RAG database
- [ ] Goal management APIs
- [ ] Frontend goal creation/tracking UI

### **Sprint 5: Smart Reminders (2-3 days)**
- [ ] Pattern detection agent
- [ ] Reminder system (email/push)
- [ ] Recurring expense detection
- [ ] Reminder UI

### **Sprint 6: Advanced Features (4-5 days)**
- [ ] Behavioral finance agent
- [ ] Merchant intelligence agent
- [ ] Subscription detector
- [ ] Tax optimization agent
- [ ] Cashback maximizer
- [ ] Debt payoff optimizer

### **Sprint 7: Polish & Testing (2-3 days)**
- [ ] End-to-end testing
- [ ] UI/UX refinement
- [ ] Performance optimization
- [ ] Documentation updates

**Total Estimated Time**: 18-25 days (3-5 weeks)

---

## 🔐 Security & Privacy Considerations

### For Personal Finance Features:
1. **Data Isolation**: User data must be strictly isolated (user_id filters in all queries)
2. **Encryption at Rest**: User profiles, goals, receipts encrypted
3. **Access Control**: JWT-based authentication for APIs
4. **GDPR Compliance**: User data export/deletion APIs
5. **Local-First**: Keep RAG processing local (no external APIs)

---

## 📊 Success Metrics

### Phase 1 (Image Forensics):
- [ ] 90%+ accuracy in detecting manipulated images
- [ ] <2s processing time per image

### Phase 2 (Personal Finance):
- [ ] 85%+ accuracy in spending predictions
- [ ] <1s dashboard load time

### Phase 3 (Goal Planning):
- [ ] Realistic investment recommendations (validated against financial advisor benchmarks)
- [ ] 95%+ user satisfaction with actionable advice

### Phase 4 (Reminders):
- [ ] 80%+ reminder accuracy (user confirms pattern)
- [ ] <5% false positive rate

---

## 🎯 Conclusion

**PROJECT LUMEN is already 50% of the way there!**

The existing infrastructure (RAG, agents, document processing) is solid. The new features are primarily:
1. **New agents** leveraging existing RAG system
2. **User profile layer** on top of existing backend
3. **Specialized models** (image forensics, time-series prediction)

**Key Advantages**:
- ✅ Don't need to rebuild RAG pipeline
- ✅ Agent orchestration pattern already proven
- ✅ Vector store ready for user-specific data
- ✅ Workspace memory provides audit trail

**Recommended Next Steps**:
1. Start with **Sprint 1** (user profiles) — unlocks everything else
2. Implement **Sprint 2** (image forensics) — high-impact, novel feature
3. Build **Sprint 3** (predictions) — core value proposition
4. Add **Sprint 4-6** incrementally based on user feedback

---

**Ready to illuminate personal finance through AI!** 🔆💰
