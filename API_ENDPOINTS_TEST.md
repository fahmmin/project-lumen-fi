# API Endpoints Documentation & Test Commands

Base URL: `http://localhost:8000`

## Test User ID
Use a wallet address format: `0x1aea8cf0dfe13ed3025910c88f7356935d76536c`

---

## 1. Users API (`/users`)

### POST /users/profile
Create user profile
```bash
curl -X POST "http://localhost:8000/users/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "0x1aea8cf0dfe13ed3025910c88f7356935d76536c",
    "name": "Test User",
    "email": "test@example.com",
    "salary_monthly": 5000.0,
    "currency": "USD"
  }'
```

### GET /users/profile/{user_id}
Get user profile (auto-creates if doesn't exist)
```bash
curl "http://localhost:8000/users/profile/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### PUT /users/profile/{user_id}
Update user profile
```bash
curl -X PUT "http://localhost:8000/users/profile/0x1aea8cf0dfe13ed3025910c88f7356935d76536c" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "salary_monthly": 6000.0
  }'
```

### POST /users/{user_id}/salary
Update salary
```bash
curl -X POST "http://localhost:8000/users/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/salary" \
  -H "Content-Type: application/json" \
  -d '{
    "salary_monthly": 7000.0,
    "currency": "USD"
  }'
```

### GET /users/
List all users
```bash
curl "http://localhost:8000/users/"
```

---

## 2. Goals API (`/goals`)

### POST /goals/
Create goal
```bash
curl -X POST "http://localhost:8000/goals/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "0x1aea8cf0dfe13ed3025910c88f7356935d76536c",
    "name": "Buy a Car",
    "target_amount": 25000.0,
    "target_date": "2025-12-31",
    "current_savings": 5000.0,
    "priority": "high"
  }'
```

### GET /goals/{user_id}
List user goals
```bash
curl "http://localhost:8000/goals/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /goals/{user_id}/{goal_id}
Get specific goal
```bash
curl "http://localhost:8000/goals/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/goal_abc123"
```

### PUT /goals/{goal_id}?user_id={user_id}
Update goal
```bash
curl -X PUT "http://localhost:8000/goals/goal_abc123?user_id=0x1aea8cf0dfe13ed3025910c88f7356935d76536c" \
  -H "Content-Type: application/json" \
  -d '{
    "current_savings": 6000.0
  }'
```

### DELETE /goals/{goal_id}?user_id={user_id}
Delete goal
```bash
curl -X DELETE "http://localhost:8000/goals/goal_abc123?user_id=0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

---

## 3. Personal Finance API (`/finance`)

### GET /finance/dashboard/{user_id}?period=month
Get dashboard
```bash
curl "http://localhost:8000/finance/dashboard/0x1aea8cf0dfe13ed3025910c88f7356935d76536c?period=month"
```

### GET /finance/spending/{user_id}?start_date=2024-01-01&end_date=2024-12-31
Get spending breakdown
```bash
curl "http://localhost:8000/finance/spending/0x1aea8cf0dfe13ed3025910c88f7356935d76536c?start_date=2024-01-01&end_date=2024-12-31"
```

### GET /finance/predictions/{user_id}
Get predictions
```bash
curl "http://localhost:8000/finance/predictions/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /finance/budget-recommendations/{user_id}
Get budget recommendations
```bash
curl "http://localhost:8000/finance/budget-recommendations/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /finance/insights/{user_id}
Get insights
```bash
curl "http://localhost:8000/finance/insights/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /finance/health-score/{user_id}
Get health score
```bash
curl "http://localhost:8000/finance/health-score/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /finance/behavior/{user_id}
Get behavior analysis
```bash
curl "http://localhost:8000/finance/behavior/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /finance/{user_id}/goals/{goal_id}/plan
Get goal plan
```bash
curl "http://localhost:8000/finance/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/goals/goal_abc123/plan"
```

### GET /finance/{user_id}/goals/{goal_id}/progress
Get goal progress
```bash
curl "http://localhost:8000/finance/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/goals/goal_abc123/progress"
```

---

## 4. Gamification API (`/gamification`)

### POST /gamification/points/award
Award points
```bash
curl -X POST "http://localhost:8000/gamification/points/award" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "0x1aea8cf0dfe13ed3025910c88f7356935d76536c",
    "activity": "create_goal",
    "metadata": {}
  }'
```

### GET /gamification/stats/{user_id}
Get user stats
```bash
curl "http://localhost:8000/gamification/stats/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /gamification/leaderboard?limit=10&user_id={user_id}
Get leaderboard
```bash
curl "http://localhost:8000/gamification/leaderboard?limit=10&user_id=0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /gamification/badges/{user_id}
Get user badges
```bash
curl "http://localhost:8000/gamification/badges/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### POST /gamification/daily-login/{user_id}
Record daily login
```bash
curl -X POST "http://localhost:8000/gamification/daily-login/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

---

## 5. Family API (`/family`)

### POST /family/create
Create family
```bash
curl -X POST "http://localhost:8000/family/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smith Family",
    "description": "Family budget",
    "created_by": "0x1aea8cf0dfe13ed3025910c88f7356935d76536c",
    "shared_budget": {"total": 5000.0}
  }'
```

### POST /family/join
Join family
```bash
curl -X POST "http://localhost:8000/family/join" \
  -H "Content-Type: application/json" \
  -d '{
    "invite_code": "ABC123",
    "user_id": "0x1aea8cf0dfe13ed3025910c88f7356935d76536c",
    "display_name": "John"
  }'
```

### GET /family/{family_id}
Get family
```bash
curl "http://localhost:8000/family/family_abc123"
```

### GET /family/user/{user_id}/families
Get user families
```bash
curl "http://localhost:8000/family/user/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/families"
```

### GET /family/{family_id}/dashboard?period=month
Get family dashboard
```bash
curl "http://localhost:8000/family/family_abc123/dashboard?period=month"
```

### GET /family/{family_id}/member/{user_id}/comparison?period=month
Get member comparison
```bash
curl "http://localhost:8000/family/family_abc123/member/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/comparison?period=month"
```

### PUT /family/{family_id}/update?user_id={user_id}
Update family
```bash
curl -X PUT "http://localhost:8000/family/family_abc123/update?user_id=0x1aea8cf0dfe13ed3025910c88f7356935d76536c" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Family Name"
  }'
```

### DELETE /family/{family_id}/leave?user_id={user_id}
Leave family
```bash
curl -X DELETE "http://localhost:8000/family/family_abc123/leave?user_id=0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /family/invite-code/{invite_code}/verify
Verify invite code
```bash
curl "http://localhost:8000/family/invite-code/ABC123/verify"
```

---

## 6. Social Comparison API (`/social`)

### GET /social/{user_id}/percentile?period=month
Get user percentile
```bash
curl "http://localhost:8000/social/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/percentile?period=month"
```

### GET /social/category/{category}/leaderboard?period=month&limit=10
Get category leaderboard
```bash
curl "http://localhost:8000/social/category/groceries/leaderboard?period=month&limit=10"
```

### GET /social/insights/{user_id}?period=month
Get social insights
```bash
curl "http://localhost:8000/social/insights/0x1aea8cf0dfe13ed3025910c88f7356935d76536c?period=month"
```

---

## 7. Reports API (`/reports`)

### POST /reports/generate/{user_id}?report_type=monthly_summary&period=month
Generate report
```bash
curl -X POST "http://localhost:8000/reports/generate/0x1aea8cf0dfe13ed3025910c88f7356935d76536c?report_type=monthly_summary&period=month"
```

### GET /reports/download/{filename}
Download report
```bash
curl "http://localhost:8000/reports/download/report_user_abc123.pdf" --output report.pdf
```

### GET /reports/{user_id}/history?limit=10
Get report history
```bash
curl "http://localhost:8000/reports/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/history?limit=10"
```

---

## 8. Subscriptions API (`/subscriptions`)

### GET /subscriptions/{user_id}
Get subscriptions
```bash
curl "http://localhost:8000/subscriptions/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /subscriptions/{user_id}/unused
Get unused subscriptions
```bash
curl "http://localhost:8000/subscriptions/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/unused"
```

---

## 9. Reminders API (`/reminders`)

### GET /reminders/{user_id}
Get reminders
```bash
curl "http://localhost:8000/reminders/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /patterns/{user_id}
Get patterns
```bash
curl "http://localhost:8000/patterns/0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

---

## 10. Voice API (`/voice`)

### POST /voice/transcribe
Transcribe audio
```bash
curl -X POST "http://localhost:8000/voice/transcribe" \
  -F "audio=@recording.mp3"
```

### POST /voice/upload-receipt
Upload receipt by voice
```bash
curl -X POST "http://localhost:8000/voice/upload-receipt" \
  -F "audio=@receipt_voice.mp3" \
  -F "user_id=0x1aea8cf0dfe13ed3025910c88f7356935d76536c"
```

### GET /voice/supported-formats
Get supported formats
```bash
curl "http://localhost:8000/voice/supported-formats"
```

---

## 11. Email API (`/email`)

### POST /email/parse-receipt
Parse email receipt
```bash
curl -X POST "http://localhost:8000/email/parse-receipt" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "0x1aea8cf0dfe13ed3025910c88f7356935d76536c",
    "email_subject": "Your Amazon Order Confirmation",
    "email_body": "Total: $59.99...Date: 12/10/2024...",
    "sender_email": "auto-confirm@amazon.com"
  }'
```

### POST /email/test-parser
Test email parser
```bash
curl -X POST "http://localhost:8000/email/test-parser" \
  -H "Content-Type: application/json" \
  -d '{
    "email_subject": "Order Confirmation",
    "email_body": "Total: $59.99"
  }'
```

### GET /email/example
Get example email
```bash
curl "http://localhost:8000/email/example"
```

---

## 12. Audit API (`/audit`)

### POST /audit/?user_id={user_id}
Execute audit
```bash
curl -X POST "http://localhost:8000/audit/?user_id=0x1aea8cf0dfe13ed3025910c88f7356935d76536c" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_data": {
      "vendor": "Amazon",
      "date": "2024-12-10",
      "amount": 59.99,
      "tax": 4.72,
      "category": "shopping",
      "invoice_number": "123-4567890"
    }
  }'
```

### POST /audit/quick?user_id={user_id}
Quick audit
```bash
curl -X POST "http://localhost:8000/audit/quick?user_id=0x1aea8cf0dfe13ed3025910c88f7356935d76536c" \
  -H "Content-Type: application/json" \
  -d '{
    "vendor": "Amazon",
    "date": "2024-12-10",
    "amount": 59.99,
    "category": "shopping"
  }'
```

### GET /audit/{audit_id}
Get audit by ID
```bash
curl "http://localhost:8000/audit/audit_abc123"
```

### GET /audit/user/{user_id}/audits?limit=100
Get user audits
```bash
curl "http://localhost:8000/audit/user/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/audits?limit=100"
```

### GET /audit/user/{user_id}/stats
Get user audit stats
```bash
curl "http://localhost:8000/audit/user/0x1aea8cf0dfe13ed3025910c88f7356935d76536c/stats"
```

---

## Testing Script

Save this as `test_all_endpoints.sh`:

```bash
#!/bin/bash
BASE_URL="http://localhost:8000"
USER_ID="0x1aea8cf0dfe13ed3025910c88f7356935d76536c"

echo "Testing all endpoints..."

# Test user profile
echo "1. Testing user profile..."
curl -s "$BASE_URL/users/profile/$USER_ID" | jq .

# Test goals
echo "2. Testing goals..."
curl -s "$BASE_URL/goals/$USER_ID" | jq .

# Test finance dashboard
echo "3. Testing finance dashboard..."
curl -s "$BASE_URL/finance/dashboard/$USER_ID?period=month" | jq .

# Test gamification
echo "4. Testing gamification..."
curl -s "$BASE_URL/gamification/stats/$USER_ID" | jq .

# Test subscriptions
echo "5. Testing subscriptions..."
curl -s "$BASE_URL/subscriptions/$USER_ID" | jq .

# Test reminders
echo "6. Testing reminders..."
curl -s "$BASE_URL/reminders/$USER_ID" | jq .

# Test social
echo "7. Testing social..."
curl -s "$BASE_URL/social/$USER_ID/percentile?period=month" | jq .

# Test reports
echo "8. Testing reports..."
curl -s -X POST "$BASE_URL/reports/generate/$USER_ID?period=month" | jq .

echo "Done!"
```


