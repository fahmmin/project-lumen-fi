# PROJECT LUMEN - Complete API Documentation

Base URL: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

---

## 🚀 Quick Start

### Test User
```
User ID: test_user_001 (or use wallet format: 0x1aea8cf0dfe13ed3025910c88f7356935d76536c)
```

### Load Demo Data
```bash
cd backend
python seed_data.py
```

Creates: ~140 receipts, 3 goals, complete user profile

---

## 📚 Core API Endpoints

### **1. Users API** (`/users`)

#### Create User Profile
```bash
POST /users/profile
Content-Type: application/json

{
  "user_id": "test_user_001",
  "name": "John Doe",
  "email": "john@example.com",
  "salary_monthly": 5000.00,
  "currency": "USD",
  "budget_categories": {
    "groceries": 500,
    "dining": 300,
    "rent": 1500
  }
}
```

#### Get User Profile
```bash
GET /users/profile/{user_id}
```

#### Update Salary
```bash
POST /users/{user_id}/salary
Content-Type: application/json

{
  "salary_monthly": 5500.00,
  "currency": "USD"
}
```

---

### **2. Goals API** (`/goals`)

#### Create Goal
```bash
POST /goals/
Content-Type: application/json

{
  "user_id": "test_user_001",
  "name": "Buy a Car",
  "target_amount": 30000.00,
  "target_date": "2029-11-15",
  "current_savings": 2000.00,
  "priority": "high"
}
```

#### List User Goals
```bash
GET /goals/{user_id}
```

#### Get Goal Details
```bash
GET /goals/{user_id}/{goal_id}
```

#### Update Goal
```bash
PUT /goals/{goal_id}?user_id={user_id}
Content-Type: application/json

{
  "current_savings": 3000.00
}
```

#### Delete Goal
```bash
DELETE /goals/{goal_id}?user_id={user_id}
```

---

### **3. Finance API** (`/finance`)

#### Get Dashboard
```bash
GET /finance/dashboard/{user_id}?period=month
```
**Params:** `period` = `month` | `quarter` | `year`

**Response:**
```json
{
  "summary": {
    "income": 5000.00,
    "total_spent": 3800.00,
    "savings": 1200.00,
    "savings_rate": 0.24
  },
  "spending_by_category": {
    "groceries": 480.00,
    "dining": 320.00,
    "rent": 1500.00
  },
  "insights": ["You spent 7% more on dining this month"]
}
```

#### Get Spending Breakdown
```bash
GET /finance/spending/{user_id}?start_date=2024-01-01&end_date=2024-12-31
```

#### Get Predictions
```bash
GET /finance/predictions/{user_id}
```

#### Get Budget Recommendations
```bash
GET /finance/budget-recommendations/{user_id}
```

#### Get AI Insights
```bash
GET /finance/insights/{user_id}
```

#### Get Financial Health Score
```bash
GET /finance/health-score/{user_id}
```

**Response:**
```json
{
  "health_score": 72,
  "rating": "Good",
  "breakdown": {
    "debt_to_income": {"score": 20, "max": 25},
    "emergency_fund": {"score": 18, "max": 25},
    "savings_rate": {"score": 16, "max": 20}
  },
  "recommendations": ["Build emergency fund to 3 months"]
}
```

#### Get Behavioral Analysis
```bash
GET /finance/behavior/{user_id}
```

#### Get Goal Plan
```bash
GET /finance/{user_id}/goals/{goal_id}/plan
```

**Response:**
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
      "Reduce dining from $350 to $200 (saves $150/month)",
      "Cancel unused subscriptions (saves $75/month)"
    ]
  },
  "investment_strategy": {
    "asset_allocation": {"stocks": 60, "bonds": 40, "cash": 0},
    "expected_return": 6.0
  }
}
```

#### Get Goal Progress
```bash
GET /finance/{user_id}/goals/{goal_id}/progress
```

---

### **4. Subscriptions API** (`/subscriptions`)

#### Get All Subscriptions
```bash
GET /subscriptions/{user_id}
```

#### Get Unused Subscriptions
```bash
GET /subscriptions/{user_id}/unused
```

---

### **5. Reminders & Patterns API** (`/reminders`, `/patterns`)

#### Get Active Reminders
```bash
GET /reminders/{user_id}
```

#### Get Detected Patterns
```bash
GET /patterns/{user_id}
```

---

### **6. Email Integration API** (`/email`)

#### Parse Email Receipt
```bash
POST /email/parse-receipt
Content-Type: application/json

{
  "user_id": "test_user_001",
  "email_subject": "Your Zomato Order Confirmation",
  "email_body": "Total: Rs450\nDate: 12/10/2024",
  "sender_email": "no-reply@zomato.com"
}
```

#### Test Email Parser
```bash
POST /email/test-parser
Content-Type: application/json

{
  "email_subject": "Order Confirmation",
  "email_body": "Total: $59.99"
}
```

---

### **7. Audit API** (`/audit`)

#### Execute Full Audit
```bash
POST /audit/?user_id={user_id}
Content-Type: application/json

{
  "invoice_data": {
    "vendor": "Amazon",
    "date": "2024-12-10",
    "amount": 59.99,
    "tax": 4.72,
    "category": "shopping",
    "invoice_number": "123-4567890"
  }
}
```

#### Quick Audit
```bash
POST /audit/quick?user_id={user_id}
Content-Type: application/json

{
  "vendor": "Amazon",
  "date": "2024-12-10",
  "amount": 59.99,
  "category": "shopping"
}
```

---

### **8. Gamification API** (`/gamification`)

#### Award Points
```bash
POST /gamification/points/award
Content-Type: application/json

{
  "user_id": "test_user_001",
  "activity": "create_goal",
  "metadata": {}
}
```

#### Get User Stats
```bash
GET /gamification/stats/{user_id}
```

#### Get Leaderboard
```bash
GET /gamification/leaderboard?limit=10&user_id={user_id}
```

---

### **9. Family API** (`/family`)

#### Create Family
```bash
POST /family/create
Content-Type: application/json

{
  "name": "Smith Family",
  "description": "Family budget",
  "created_by": "test_user_001",
  "shared_budget": {"total": 5000.0}
}
```

#### Join Family
```bash
POST /family/join
Content-Type: application/json

{
  "invite_code": "ABC123",
  "user_id": "test_user_001",
  "display_name": "John"
}
```

---

### **10. Social Comparison API** (`/social`)

#### Get User Percentile
```bash
GET /social/{user_id}/percentile?period=month
```

#### Get Category Leaderboard
```bash
GET /social/category/{category}/leaderboard?period=month&limit=10
```

---

### **11. Reports API** (`/reports`)

#### Generate Report
```bash
POST /reports/generate/{user_id}?report_type=monthly_summary&period=month
```

#### Download Report
```bash
GET /reports/download/{filename}
```

---

### **12. Voice API** (`/voice`)

#### Transcribe Audio
```bash
POST /voice/transcribe
Content-Type: multipart/form-data

Form Data:
- audio: [audio file]
```

---

## 🧪 Testing

### Quick Test Script
```bash
#!/bin/bash
BASE_URL="http://localhost:8000"
USER_ID="test_user_001"

echo "Testing PROJECT LUMEN APIs..."

# Health check
curl -s "$BASE_URL/health" | jq .

# User profile
curl -s "$BASE_URL/users/profile/$USER_ID" | jq .

# Goals
curl -s "$BASE_URL/goals/$USER_ID" | jq .

# Dashboard
curl -s "$BASE_URL/finance/dashboard/$USER_ID?period=month" | jq .

# Predictions
curl -s "$BASE_URL/finance/predictions/$USER_ID" | jq .

# Health score
curl -s "$BASE_URL/finance/health-score/$USER_ID" | jq .

echo "✅ Tests complete!"
```

### Postman Collection

**Import Steps:**
1. Create new collection "PROJECT LUMEN"
2. Set environment variable: `base_url` = `http://localhost:8000`
3. Set environment variable: `user_id` = `test_user_001`
4. Import endpoints from this document

---

## 📊 Common Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## 🔍 Troubleshooting

### "User not found"
→ Run: `python backend/seed_data.py`

### "Not enough data for prediction"
→ Need at least 10 transactions. Run seed script.

### "Goal not found"
→ List goals first: `GET /goals/{user_id}`, then use returned `goal_id`

### Empty dashboard
→ Check: `GET /info` - should show indexed documents > 0

---

## 📖 Additional Resources

- **API Interactive Docs**: `http://localhost:8000/docs`
- **Architecture**: See `ARCHITECTURE_QUICK_REFERENCE.md`
- **Goal System**: See `GOAL_MAKER_ANALYSIS.md`
- **Setup**: See `QUICKSTART.md`

---

**All endpoints documented and ready for testing!** 🚀
