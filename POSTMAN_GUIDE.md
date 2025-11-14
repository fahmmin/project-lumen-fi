# PROJECT LUMEN - Postman Testing Guide

## 🚀 Quick Start

### 1. Start the Server
```bash
cd backend
python main.py
```

**Server URL:** `http://localhost:8000`
**API Docs:** `http://localhost:8000/docs`

---

### 2. Load Dummy Data
```bash
cd backend
python seed_data.py
```

This creates:
- **Test User:** `test_user_001`
- **~140 Receipts** (6 months of spending)
- **3 Goals** (Car, Emergency Fund, Vacation)

---

## 📮 POSTMAN COLLECTION

### Test User Info
```
User ID: test_user_001
Email: john.doe@example.com
Salary: $5,000/month
```

---

## 🔥 TOP 10 ENDPOINTS TO TEST (Start Here!)

### 1️⃣ **Health Check**
```
GET http://localhost:8000/health
```
✅ Verify system is running

---

### 2️⃣ **Get Personal Finance Dashboard**
```
GET http://localhost:8000/finance/dashboard/test_user_001?period=month
```

**Query Params:**
- `period`: `month` | `quarter` | `year`

**Response:** Complete dashboard with spending breakdown, savings, insights

---

### 3️⃣ **Get Spending Predictions**
```
GET http://localhost:8000/finance/predictions/test_user_001
```

**Response:** Next month's predicted spending with confidence intervals

---

### 4️⃣ **Get Budget Recommendations**
```
GET http://localhost:8000/finance/budget-recommendations/test_user_001
```

**Response:** AI-powered budget optimization suggestions

---

### 5️⃣ **Get Financial Health Score**
```
GET http://localhost:8000/finance/health-score/test_user_001
```

**Response:** 0-100 score with breakdown (debt, emergency fund, savings rate, etc.)

---

### 6️⃣ **List User's Goals**
```
GET http://localhost:8000/goals/test_user_001
```

**Response:** All financial goals for user

---

### 7️⃣ **Get Goal Savings Plan**
```
GET http://localhost:8000/finance/test_user_001/goals/{goal_id}/plan
```

**Replace `{goal_id}` with actual goal ID from step 6**

**Response:** Complete savings plan with:
- Monthly savings needed
- Investment strategy
- Asset allocation
- Milestones
- Recommendations

---

### 8️⃣ **Get Smart Reminders**
```
GET http://localhost:8000/reminders/test_user_001
```

**Response:** Active smart reminders based on spending patterns

---

### 9️⃣ **Get Detected Subscriptions**
```
GET http://localhost:8000/subscriptions/test_user_001
```

**Response:** All detected subscriptions (Netflix, Spotify, etc.)

---

### 🔟 **Get Behavioral Analysis**
```
GET http://localhost:8000/finance/behavior/test_user_001
```

**Response:** Spending psychology analysis (day-of-week patterns, impulse scores)

---

## 📋 COMPLETE API REFERENCE

### **USERS** (`/users`)

#### Create User Profile
```
POST http://localhost:8000/users/profile
Content-Type: application/json

{
  "user_id": "user_123",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "salary_monthly": 6000.00,
  "currency": "USD",
  "budget_categories": {
    "groceries": 600,
    "dining": 400,
    "rent": 1800
  }
}
```

#### Get User Profile
```
GET http://localhost:8000/users/profile/test_user_001
```

#### Update Salary
```
POST http://localhost:8000/users/test_user_001/salary
Content-Type: application/json

{
  "salary_monthly": 5500.00,
  "currency": "USD"
}
```

#### Delete User
```
DELETE http://localhost:8000/users/profile/test_user_001
```

---

### **GOALS** (`/goals`)

#### Create Goal
```
POST http://localhost:8000/goals/
Content-Type: application/json

{
  "user_id": "test_user_001",
  "name": "Buy a House",
  "target_amount": 100000.00,
  "target_date": "2030-12-31",
  "current_savings": 10000.00,
  "priority": "high"
}
```

#### List Goals
```
GET http://localhost:8000/goals/test_user_001
```

#### Get Goal Details
```
GET http://localhost:8000/goals/test_user_001/{goal_id}
```

#### Update Goal
```
PUT http://localhost:8000/goals/{goal_id}?user_id=test_user_001
Content-Type: application/json

{
  "current_savings": 5000.00
}
```

#### Delete Goal
```
DELETE http://localhost:8000/goals/{goal_id}?user_id=test_user_001
```

---

### **FINANCE** (`/finance`)

#### Dashboard
```
GET http://localhost:8000/finance/dashboard/test_user_001?period=month
```

#### Spending Breakdown
```
GET http://localhost:8000/finance/spending/test_user_001
```

**Optional Query Params:**
- `start_date`: `2024-01-01`
- `end_date`: `2024-12-31`
- `category`: `groceries`

#### Predictions
```
GET http://localhost:8000/finance/predictions/test_user_001
```

#### Budget Recommendations
```
GET http://localhost:8000/finance/budget-recommendations/test_user_001
```

#### AI Insights
```
GET http://localhost:8000/finance/insights/test_user_001
```

#### Health Score
```
GET http://localhost:8000/finance/health-score/test_user_001
```

#### Behavioral Analysis
```
GET http://localhost:8000/finance/behavior/test_user_001
```

#### Goal Plan
```
GET http://localhost:8000/finance/test_user_001/goals/{goal_id}/plan
```

#### Goal Progress
```
GET http://localhost:8000/finance/test_user_001/goals/{goal_id}/progress
```

---

### **REMINDERS & PATTERNS** (`/reminders`, `/patterns`)

#### Get Active Reminders
```
GET http://localhost:8000/reminders/test_user_001
```

#### Get Detected Patterns
```
GET http://localhost:8000/patterns/test_user_001
```

---

### **SUBSCRIPTIONS** (`/subscriptions`)

#### Get All Subscriptions
```
GET http://localhost:8000/subscriptions/test_user_001
```

#### Get Unused Subscriptions
```
GET http://localhost:8000/subscriptions/test_user_001/unused
```

---

### **IMAGE FORENSICS** (`/forensics`)

#### Analyze Image
```
POST http://localhost:8000/forensics/analyze
Content-Type: multipart/form-data

Form Data:
- image: [Upload Image File]
```

**In Postman:**
1. Select `POST`
2. URL: `http://localhost:8000/forensics/analyze`
3. Body → form-data
4. Key: `image` (Type: File)
5. Value: Select an image file

---

### **INGESTION** (`/ingest`)

#### Upload Receipt
```
POST http://localhost:8000/ingest/
Content-Type: multipart/form-data

Form Data:
- file: [Upload PDF or Image]
- user_id: test_user_001
```

**In Postman:**
1. Select `POST`
2. URL: `http://localhost:8000/ingest/`
3. Body → form-data
4. Key: `file` (Type: File), Value: Select PDF/image
5. Key: `user_id` (Type: Text), Value: `test_user_001`

---

## 🎯 RECOMMENDED TEST FLOW

### Flow 1: Complete User Journey
```
1. GET /health                                    → Verify system
2. GET /users/profile/test_user_001               → Get user info
3. GET /finance/dashboard/test_user_001           → View dashboard
4. GET /finance/predictions/test_user_001         → See predictions
5. GET /finance/budget-recommendations/test_user_001 → Get advice
6. GET /goals/test_user_001                       → List goals
7. GET /finance/test_user_001/goals/{goal_id}/plan → Get savings plan
```

### Flow 2: Quick Health Check
```
1. GET /finance/health-score/test_user_001        → Get health score
2. GET /finance/insights/test_user_001            → Get insights
3. GET /subscriptions/test_user_001/unused        → Find savings
```

### Flow 3: Advanced Analysis
```
1. GET /finance/behavior/test_user_001            → Psychology
2. GET /patterns/test_user_001                    → Spending patterns
3. GET /reminders/test_user_001                   → Smart reminders
```

---

## 📊 EXPECTED RESPONSES

### Dashboard Example
```json
{
  "user_id": "test_user_001",
  "period": "month",
  "summary": {
    "income": 5000.00,
    "total_spent": 3850.00,
    "savings": 1150.00,
    "savings_rate": 0.23
  },
  "spending_by_category": {
    "groceries": 480.00,
    "dining": 320.00,
    "rent": 1500.00,
    "utilities": 185.00
  },
  "insights": [
    "You spent 7% more on dining this month",
    "Great job staying under budget on groceries!"
  ]
}
```

### Goal Plan Example
```json
{
  "goal_name": "Buy a Car",
  "target_amount": 30000.00,
  "months_remaining": 48,
  "plan": {
    "monthly_savings_required": 625.00,
    "current_savings_rate": 400.00,
    "gap": 225.00,
    "recommendations": [
      "Reduce dining out from $350 to $200 (saves $150/month)",
      "Cancel unused Spotify subscription (saves $10/month)"
    ]
  },
  "investment_strategy": {
    "asset_allocation": {
      "stocks": 60,
      "bonds": 40,
      "cash": 0
    },
    "expected_return": 6.0
  }
}
```

### Health Score Example
```json
{
  "health_score": 72,
  "rating": "Good",
  "breakdown": {
    "debt_to_income": {
      "score": 20,
      "max": 25,
      "rating": "excellent"
    },
    "emergency_fund": {
      "score": 18,
      "max": 25,
      "months_covered": 1.2
    },
    "savings_rate": {
      "score": 16,
      "max": 20,
      "value": 0.23
    }
  },
  "recommendations": [
    "Build emergency fund to 3 months of expenses ($11,250)",
    "Increase savings rate to 25%"
  ]
}
```

---

## ⚡ QUICK TIPS

### Import into Postman
1. Create a new Collection: "PROJECT LUMEN"
2. Add requests manually using endpoints above
3. Set base URL as variable: `{{base_url}}` = `http://localhost:8000`

### Environment Variables
```
base_url: http://localhost:8000
user_id: test_user_001
```

### Save Sample Responses
Click "Save Response" → Example in Postman to save expected outputs

---

## 🐛 TROUBLESHOOTING

### "User not found"
→ Run seed data script: `python backend/seed_data.py`

### "Not enough data for prediction"
→ Need at least 10 transactions. Run seed script.

### "Goal not found"
→ Get goal list first: `GET /goals/test_user_001`
→ Copy `goal_id` from response

### Empty dashboard
→ Check receipts indexed: `GET /info` → look at "documents"
→ Re-run seed script if needed

---

## 🎉 YOU'RE READY!

All endpoints are documented and ready to test!

**Quick Start:**
1. ✅ `python backend/main.py` (start server)
2. ✅ `python backend/seed_data.py` (load data)
3. ✅ Test in Postman or `/docs`

Happy testing! 🚀
