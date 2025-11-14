# PROJECT LUMEN - API Endpoints Documentation (Phase B)

**Base URL:** `http://localhost:8000`
**Version:** 2.0 (MVP - Personal Finance Layer)
**Last Updated:** 2025-11-14

---

## 📋 TABLE OF CONTENTS

1. [Existing Endpoints](#existing-endpoints) (Already Built)
2. [User Management](#user-management) (NEW)
3. [Personal Finance](#personal-finance) (NEW)
4. [Goals & Planning](#goals--planning) (NEW)
5. [Reminders & Patterns](#reminders--patterns) (NEW)
6. [Image Forensics](#image-forensics) (NEW)
7. [Subscriptions](#subscriptions) (NEW)
8. [Health & Behavior](#health--behavior) (NEW)

---

## 🟢 EXISTING ENDPOINTS (Already Built)

### Document Ingestion

#### `POST /ingest/`
Upload and process financial documents.

**Request:**
```bash
curl -X POST "http://localhost:8000/ingest/" \
  -F "file=@invoice.pdf" \
  -F "user_id=user_123"  # NEW: Optional user ID
```
F
**Response:**
```json
{
  "status": "success",
  "document_id": "doc_abc123",
  "filename": "invoice.pdf",
  "user_id": "user_123",
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

---

#### `GET /ingest/status/{document_id}`
Check document ingestion status.

**Response:**
```json
{
  "document_id": "doc_abc123",
  "status": "completed",
  "filename": "invoice.pdf"
}
```

---

### Audit System

#### `POST /audit/`
Run multi-agent audit (existing orchestrated audit).

**Request:**
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

**Response:**
```json
{
  "audit_id": "audit_xyz789",
  "overall_status": "pass",
  "findings": {
    "audit": { "status": "pass", "duplicates": [] },
    "compliance": { "compliant": true, "violations": [] },
    "fraud": { "anomaly_detected": false, "risk_score": 0.23 }
  },
  "explanation": "Invoice appears legitimate..."
}
```

---

### Workspace Memory

#### `GET /memory/`
Get complete workspace content.

#### `GET /memory/recent?n=10`
Get recent entries.

#### `POST /memory/search`
Search workspace.

#### `GET /memory/stats`
Get statistics.

---

### System

#### `GET /health`
Health check.

#### `GET /info`
System information.

---

## 🆕 USER MANAGEMENT (NEW)

### `POST /users/profile`
Create or update user profile.

**Request:**
```json
{
  "user_id": "user_123",
  "name": "John Doe",
  "email": "john@example.com",
  "salary_monthly": 5000.00,
  "currency": "USD",
  "budget_categories": {
    "groceries": 500,
    "dining": 300,
    "rent": 1500,
    "utilities": 200,
    "transportation": 300,
    "entertainment": 200
  }
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user_123",
  "message": "Profile created successfully",
  "created_at": "2025-11-14T10:00:00Z"
}
```

---

### `GET /users/profile/{user_id}`
Get user profile.

**Response:**
```json
{
  "user_id": "user_123",
  "name": "John Doe",
  "email": "john@example.com",
  "salary_monthly": 5000.00,
  "currency": "USD",
  "budget_categories": {
    "groceries": 500,
    "dining": 300,
    "rent": 1500
  },
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T10:00:00Z"
}
```

---

### `PUT /users/profile/{user_id}`
Update user profile (same request format as POST).

---

### `POST /users/{user_id}/salary`
Set or update monthly income.

**Request:**
```json
{
  "salary_monthly": 5500.00,
  "currency": "USD"
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user_123",
  "salary_monthly": 5500.00,
  "updated_at": "2025-11-14T10:00:00Z"
}
```

---

### `DELETE /users/profile/{user_id}`
Delete user profile and all associated data.

**Response:**
```json
{
  "status": "success",
  "message": "User data deleted successfully",
  "deleted_receipts": 45,
  "deleted_goals": 3
}
```

---

## 💰 PERSONAL FINANCE (NEW)

### `GET /finance/dashboard/{user_id}`
Get comprehensive dashboard data.

**Query Parameters:**
- `period` (optional): `month` | `quarter` | `year` (default: `month`)

**Response:**
```json
{
  "user_id": "user_123",
  "period": "month",
  "month": "2025-11",
  "summary": {
    "income": 5000.00,
    "total_spent": 3800.00,
    "savings": 1200.00,
    "savings_rate": 0.24
  },
  "spending_by_category": {
    "groceries": 480.00,
    "dining": 320.00,
    "rent": 1500.00,
    "utilities": 180.00,
    "transportation": 280.00,
    "entertainment": 240.00,
    "other": 800.00
  },
  "vs_budget": {
    "groceries": { "budget": 500, "actual": 480, "difference": 20, "status": "under" },
    "dining": { "budget": 300, "actual": 320, "difference": -20, "status": "over" }
  },
  "vs_last_month": {
    "total_change": 150.00,
    "percent_change": 4.1,
    "trend": "increasing"
  },
  "insights": [
    "You spent 7% more on dining this month compared to last month",
    "Great job staying under budget on groceries!",
    "Your savings rate (24%) is above average"
  ]
}
```

---

### `GET /finance/spending/{user_id}`
Get detailed spending breakdown.

**Query Parameters:**
- `period`: `week` | `month` | `quarter` | `year`
- `start_date`: `YYYY-MM-DD`
- `end_date`: `YYYY-MM-DD`
- `category`: Filter by category

**Response:**
```json
{
  "user_id": "user_123",
  "period": "month",
  "total_spent": 3800.00,
  "transactions": [
    {
      "date": "2025-11-12",
      "vendor": "Whole Foods",
      "category": "groceries",
      "amount": 125.50,
      "receipt_id": "doc_123"
    },
    {
      "date": "2025-11-10",
      "vendor": "Uber",
      "category": "transportation",
      "amount": 18.50,
      "receipt_id": "doc_124"
    }
  ],
  "category_breakdown": {
    "groceries": { "amount": 480.00, "count": 12, "avg_per_transaction": 40.00 },
    "dining": { "amount": 320.00, "count": 8, "avg_per_transaction": 40.00 }
  }
}
```

---

### `GET /finance/predictions/{user_id}`
Predict next month's spending.

**Response:**
```json
{
  "user_id": "user_123",
  "prediction_for": "2025-12",
  "predicted_total": 3950.00,
  "confidence_interval": [3700.00, 4200.00],
  "confidence_level": 0.85,
  "breakdown_by_category": {
    "groceries": 510.00,
    "dining": 340.00,
    "rent": 1500.00,
    "utilities": 220.00
  },
  "factors": [
    "Historical average over last 6 months",
    "Seasonal trend (December typically 10% higher)",
    "Recent spending increase in dining category"
  ],
  "recommendation": "Based on predictions, you may exceed your budget by $250. Consider reducing dining out."
}
```

---

### `GET /finance/insights/{user_id}`
Get AI-powered spending insights.

**Response:**
```json
{
  "user_id": "user_123",
  "insights": [
    {
      "type": "overspending",
      "category": "dining",
      "message": "You spent $320 on dining (7% over budget)",
      "recommendation": "Try meal prepping to reduce restaurant expenses",
      "severity": "medium"
    },
    {
      "type": "trend",
      "category": "groceries",
      "message": "Grocery prices have increased 5% compared to 3 months ago",
      "recommendation": "Consider shopping at discount stores",
      "severity": "low"
    },
    {
      "type": "achievement",
      "category": "savings",
      "message": "You saved $1,200 this month - 24% of income!",
      "recommendation": "Great work! Consider investing some savings.",
      "severity": "positive"
    }
  ]
}
```

---

### `GET /finance/budget-recommendations/{user_id}`
Get personalized budget recommendations.

**Response:**
```json
{
  "user_id": "user_123",
  "current_budget": {
    "groceries": 500,
    "dining": 300,
    "entertainment": 200
  },
  "recommended_budget": {
    "groceries": 480,
    "dining": 250,
    "entertainment": 180
  },
  "rationale": {
    "groceries": "You consistently spend less than budget - adjust to realistic level",
    "dining": "Reduce by $50 to improve savings rate",
    "entertainment": "Reduce by $20 based on actual usage patterns"
  },
  "potential_savings": 90.00,
  "annual_impact": 1080.00
}
```

---

## 🎯 GOALS & PLANNING (NEW)

### `POST /goals/`
Create a new financial goal.

**Request:**
```json
{
  "user_id": "user_123",
  "name": "Buy a Car",
  "target_amount": 30000.00,
  "target_date": "2029-11-01",
  "current_savings": 2000.00,
  "priority": "high"
}
```

**Response:**
```json
{
  "status": "success",
  "goal_id": "goal_456",
  "name": "Buy a Car",
  "created_at": "2025-11-14T10:00:00Z"
}
```

---

### `GET /goals/{user_id}`
List all goals for a user.

**Response:**
```json
{
  "user_id": "user_123",
  "goals": [
    {
      "goal_id": "goal_456",
      "name": "Buy a Car",
      "target_amount": 30000.00,
      "target_date": "2029-11-01",
      "current_savings": 2000.00,
      "progress_percentage": 6.7,
      "status": "on_track",
      "priority": "high"
    },
    {
      "goal_id": "goal_457",
      "name": "Emergency Fund",
      "target_amount": 15000.00,
      "target_date": "2026-11-01",
      "current_savings": 5000.00,
      "progress_percentage": 33.3,
      "status": "ahead",
      "priority": "critical"
    }
  ]
}
```

---

### `GET /goals/{goal_id}`
Get goal details.

**Response:**
```json
{
  "goal_id": "goal_456",
  "user_id": "user_123",
  "name": "Buy a Car",
  "target_amount": 30000.00,
  "target_date": "2029-11-01",
  "current_savings": 2000.00,
  "progress_percentage": 6.7,
  "status": "on_track",
  "priority": "high",
  "created_at": "2025-11-14T10:00:00Z",
  "updated_at": "2025-11-14T10:00:00Z"
}
```

---

### `GET /goals/{goal_id}/plan`
Get savings and investment plan for goal.

**Response:**
```json
{
  "goal_id": "goal_456",
  "goal_name": "Buy a Car",
  "target_amount": 30000.00,
  "target_date": "2029-11-01",
  "months_remaining": 48,
  "current_savings": 2000.00,
  "amount_needed": 28000.00,
  "plan": {
    "monthly_savings_required": 583.33,
    "current_savings_rate": 400.00,
    "gap": 183.33,
    "recommendations": [
      "Reduce dining out from $320 to $200 (saves $120/month)",
      "Cancel unused subscriptions (saves $75/month)",
      "Total adjustments needed: $183/month"
    ]
  },
  "investment_strategy": {
    "time_horizon": "4 years",
    "risk_level": "moderate",
    "asset_allocation": {
      "stocks": 60,
      "bonds": 40,
      "cash": 0
    },
    "expected_return": 0.06,
    "projected_final_amount": 30850.00,
    "rationale": "4-year horizon allows moderate risk. 60/40 stock/bond allocation provides growth with stability."
  },
  "milestones": [
    { "date": "2026-11-01", "target_amount": 9000.00, "description": "1 year - 30% complete" },
    { "date": "2027-11-01", "target_amount": 16000.00, "description": "2 years - 53% complete" },
    { "date": "2028-11-01", "target_amount": 23000.00, "description": "3 years - 77% complete" },
    { "date": "2029-11-01", "target_amount": 30000.00, "description": "4 years - 100% complete" }
  ]
}
```

---

### `GET /goals/{goal_id}/progress`
Track progress toward goal.

**Response:**
```json
{
  "goal_id": "goal_456",
  "goal_name": "Buy a Car",
  "progress_percentage": 6.7,
  "current_savings": 2000.00,
  "target_amount": 30000.00,
  "on_track": true,
  "projected_completion_date": "2029-10-15",
  "ahead_behind": "2 weeks ahead of schedule",
  "monthly_contribution_avg": 420.00,
  "required_monthly_contribution": 583.33,
  "adjustments_needed": [
    "You're saving $420/month but need $583/month",
    "Increase monthly savings by $163 to stay on track"
  ]
}
```

---

### `PUT /goals/{goal_id}`
Update goal (amount, date, current savings).

**Request:**
```json
{
  "current_savings": 2500.00,
  "target_date": "2029-06-01"
}
```

---

### `DELETE /goals/{goal_id}`
Delete a goal.

---

## 🔔 REMINDERS & PATTERNS (NEW)

### `GET /reminders/{user_id}`
Get active reminders.

**Response:**
```json
{
  "user_id": "user_123",
  "reminders": [
    {
      "reminder_id": "rem_789",
      "type": "recurring_expense",
      "message": "You usually buy groceries around the 10th — time to restock!",
      "category": "groceries",
      "typical_amount": 450.00,
      "typical_vendor": "Whole Foods",
      "next_expected_date": "2025-12-10",
      "confidence": 0.87,
      "status": "active"
    },
    {
      "reminder_id": "rem_790",
      "type": "bill_due",
      "message": "Your electricity bill is due next week (typically $120)",
      "category": "utilities",
      "typical_amount": 120.00,
      "due_date": "2025-11-20",
      "confidence": 0.92,
      "status": "active"
    }
  ]
}
```

---

### `GET /patterns/{user_id}`
Get detected spending patterns.

**Response:**
```json
{
  "user_id": "user_123",
  "patterns": [
    {
      "pattern_id": "pat_001",
      "pattern_type": "monthly_grocery",
      "vendor": "Whole Foods",
      "category": "groceries",
      "frequency": "monthly",
      "typical_day": 10,
      "typical_amount": 450.00,
      "last_purchase": "2025-11-10",
      "next_expected": "2025-12-10",
      "occurrences": 8,
      "confidence": 0.87
    },
    {
      "pattern_id": "pat_002",
      "pattern_type": "weekly_coffee",
      "vendor": "Starbucks",
      "category": "dining",
      "frequency": "weekly",
      "typical_day_of_week": "Monday",
      "typical_amount": 6.50,
      "last_purchase": "2025-11-11",
      "next_expected": "2025-11-18",
      "occurrences": 32,
      "confidence": 0.95
    }
  ]
}
```

---

### `POST /patterns/{pattern_id}/snooze`
Snooze a reminder for a pattern.

**Request:**
```json
{
  "snooze_until": "2025-12-01"
}
```

---

### `DELETE /reminders/{reminder_id}`
Dismiss a reminder.

---

## 🖼️ IMAGE FORENSICS (NEW)

### `POST /forensics/analyze`
Analyze image authenticity.

**Request:**
```bash
curl -X POST "http://localhost:8000/forensics/analyze" \
  -F "image=@receipt.jpg"
```

**Response:**
```json
{
  "status": "success",
  "image_file": "receipt.jpg",
  "authenticity": {
    "authentic": false,
    "confidence": 0.78,
    "risk_score": 0.62,
    "verdict": "likely_manipulated"
  },
  "analysis": {
    "ela_analysis": {
      "anomalies_detected": true,
      "suspicious_regions": ["bottom_right", "total_amount_area"],
      "score": 0.65
    },
    "exif_analysis": {
      "has_exif": true,
      "camera_make": "Apple",
      "camera_model": "iPhone 13",
      "timestamp": "2025-11-10T14:30:00Z",
      "gps_location": null,
      "exif_consistent": true,
      "score": 0.90
    },
    "clone_detection": {
      "clones_detected": false,
      "score": 0.95
    },
    "lighting_analysis": {
      "inconsistencies": true,
      "suspicious_areas": ["text_region"],
      "score": 0.55
    }
  },
  "manipulation_indicators": [
    "ELA shows high error levels around total amount (possible editing)",
    "Lighting appears inconsistent in text region",
    "Overall risk score: 62% (MEDIUM risk)"
  ],
  "recommendation": "Manual review recommended - moderate manipulation detected"
}
```

---

## 🐕 SUBSCRIPTIONS (NEW)

### `GET /subscriptions/{user_id}`
List all detected subscriptions.

**Response:**
```json
{
  "user_id": "user_123",
  "subscriptions": [
    {
      "subscription_id": "sub_001",
      "name": "Netflix",
      "category": "entertainment",
      "amount": 15.99,
      "frequency": "monthly",
      "billing_day": 15,
      "first_detected": "2025-05-15",
      "last_charge": "2025-11-15",
      "total_charges": 7,
      "total_spent": 111.93,
      "status": "active",
      "usage_estimate": "medium"
    },
    {
      "subscription_id": "sub_002",
      "name": "Spotify Premium",
      "category": "entertainment",
      "amount": 9.99,
      "frequency": "monthly",
      "billing_day": 5,
      "first_detected": "2025-02-05",
      "last_charge": "2025-08-05",
      "total_charges": 7,
      "total_spent": 69.93,
      "status": "unused",
      "usage_estimate": "none"
    }
  ],
  "summary": {
    "total_subscriptions": 2,
    "active": 1,
    "unused": 1,
    "monthly_cost": 25.98,
    "annual_cost": 311.76
  }
}
```

---

### `GET /subscriptions/{user_id}/unused`
Get unused subscriptions.

**Response:**
```json
{
  "user_id": "user_123",
  "unused_subscriptions": [
    {
      "subscription_id": "sub_002",
      "name": "Spotify Premium",
      "amount": 9.99,
      "months_unused": 3,
      "potential_savings_annual": 119.88,
      "recommendation": "Cancel - no usage detected in 3 months"
    }
  ],
  "total_potential_savings": 119.88
}
```

---

### `GET /subscriptions/{user_id}/savings`
Calculate potential savings from optimization.

---

## 💯 HEALTH & BEHAVIOR (NEW)

### `GET /finance/health-score/{user_id}`
Get financial health score.

**Response:**
```json
{
  "user_id": "user_123",
  "health_score": 72,
  "rating": "Good",
  "updated_at": "2025-11-14T10:00:00Z",
  "breakdown": {
    "debt_to_income": {
      "score": 20,
      "max": 25,
      "value": 0.15,
      "rating": "excellent",
      "description": "15% debt-to-income ratio is very healthy"
    },
    "emergency_fund": {
      "score": 18,
      "max": 25,
      "value": 4500.00,
      "months_covered": 1.2,
      "rating": "fair",
      "description": "Emergency fund covers 1.2 months of expenses (target: 3-6 months)"
    },
    "savings_rate": {
      "score": 16,
      "max": 20,
      "value": 0.24,
      "rating": "good",
      "description": "24% savings rate is above average"
    },
    "spending_volatility": {
      "score": 10,
      "max": 15,
      "value": 0.12,
      "rating": "moderate",
      "description": "Spending varies by 12% month-to-month"
    },
    "goal_progress": {
      "score": 8,
      "max": 15,
      "value": 0.35,
      "rating": "fair",
      "description": "On track with 1 of 3 goals"
    }
  },
  "recommendations": [
    "Build emergency fund to 3 months of expenses ($11,250)",
    "Reduce spending volatility by creating a stricter budget",
    "Increase goal contributions to stay on track"
  ]
}
```

---

### `GET /finance/health-score/{user_id}/breakdown`
Get detailed score breakdown (same as above, more details).

---

### `GET /finance/behavior/{user_id}`
Get spending psychology analysis.

**Response:**
```json
{
  "user_id": "user_123",
  "analysis_period": "last_3_months",
  "impulse_score": 0.45,
  "patterns": [
    {
      "type": "day_of_week",
      "finding": "You spend 2x more on weekends than weekdays",
      "data": {
        "weekday_avg": 85.00,
        "weekend_avg": 170.00,
        "ratio": 2.0
      },
      "severity": "medium"
    },
    {
      "type": "time_of_day",
      "finding": "Higher spending detected between 11pm-1am (impulse purchases)",
      "data": {
        "late_night_transactions": 12,
        "late_night_total": 450.00
      },
      "severity": "medium"
    },
    {
      "type": "emotional_spending",
      "finding": "Spending increases 30% after work trips (travel dates)",
      "data": {
        "normal_weekly_avg": 320.00,
        "post_travel_avg": 416.00
      },
      "severity": "low"
    }
  ],
  "recommendations": [
    "Set a weekend spending limit of $150",
    "Use the 24-hour rule for purchases over $100",
    "Avoid online shopping late at night",
    "Create a post-travel budget to control stress spending"
  ]
}
```

---

### `GET /finance/behavior/{user_id}/patterns`
Get behavioral patterns only (subset of above).

---

## 📊 RESPONSE CODES

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (invalid data) |
| 404 | Not Found (user/goal/subscription not found) |
| 409 | Conflict (duplicate user_id) |
| 500 | Internal Server Error |

---

## 🔒 AUTHENTICATION (Future)

**Currently:** No authentication (MVP)
**Future:** JWT-based authentication

```bash
# Future auth header
Authorization: Bearer <jwt_token>
```

---

## 📝 NOTES FOR FRONTEND INTEGRATION

### Typical User Flow

1. **Onboarding:**
   - `POST /users/profile` - Create user
   - `POST /users/{user_id}/salary` - Set income

2. **Upload Receipts:**
   - `POST /ingest/` with `user_id` - Upload receipt

3. **View Dashboard:**
   - `GET /finance/dashboard/{user_id}` - Main dashboard
   - `GET /finance/insights/{user_id}` - AI insights

4. **Create Goal:**
   - `POST /goals/` - Create goal
   - `GET /goals/{goal_id}/plan` - Get savings plan

5. **Check Reminders:**
   - `GET /reminders/{user_id}` - Active reminders

6. **Analyze Image:**
   - `POST /forensics/analyze` - Check if receipt is fake

### Pagination (Future)
Currently: All results returned
Future: Add `?page=1&limit=20` to endpoints

### Rate Limiting (Future)
Not implemented in MVP

---

**Total New Endpoints:** 30+
**Implementation Status:** 🟡 In Progress
**Last Updated:** 2025-11-14
