# Agentic RAG Report Generation System

## Overview

Project Lumen now includes a comprehensive **Agentic RAG (Retrieval-Augmented Generation) Report System** that automatically generates and emails detailed financial reports using multiple AI agents.

### What is Agentic RAG?

This system combines:
- **RAG (Retrieval-Augmented Generation)**: Hybrid retrieval using FAISS dense search, BM25 sparse search, and MonoT5 reranking to fetch relevant financial data
- **Multi-Agent Orchestration**: 8 specialized AI agents analyze different aspects of your financial data
- **Automated Scheduling**: Weekly/monthly automated report generation
- **Email Delivery**: Beautiful HTML reports sent via SendGrid

---

## Features

### 🤖 8 Specialized AI Agents

The report generator coordinates 8 AI agents, each specialized in a specific area:

1. **Personal Finance Agent** - Spending analysis, forecasting, budget tracking
2. **Goal Planner Agent** - Financial goal progress and deadline tracking
3. **Savings Opportunity Agent** - Identifies potential cost reductions
4. **Fraud Detection Agent** - Anomaly detection and suspicious transaction alerts
5. **Pattern Detection Agent** - Recurring expenses and spending trends
6. **Behavioral Analysis Agent** - Spending personality and habit insights
7. **Compliance Agent** - Financial policy compliance checking
8. **Audit Agent** - Data quality validation and integrity checks

### 📊 Comprehensive Reports Include

- **Executive Summary** with Financial Health Score (0-100)
- **Financial Overview** - Total spending, budget usage, top categories
- **Goal Progress** - Visual progress bars for all financial goals
- **Savings Opportunities** - Actionable recommendations with potential savings amounts
- **Fraud & Security Alerts** - Unusual transactions requiring attention
- **Spending Patterns** - Recurring expenses and trend analysis
- **Behavioral Insights** - Your spending personality and habits
- **Compliance Status** - Policy violations and recommendations
- **Personalized Recommendations** - Prioritized action items

### 📧 Email Delivery

- Beautiful HTML email with report summary
- Full report attached as HTML file
- Customizable sender name and email
- SendGrid integration for reliable delivery

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `sendgrid==6.11.0` - Email delivery
- `apscheduler==3.10.4` - Report scheduling

### 2. Configure SendGrid

1. Sign up for SendGrid at https://sendgrid.com/
2. Create an API key with "Mail Send" permissions
3. Add to your `.env` file:

```bash
# SendGrid Configuration
SENDGRID_API_KEY=SG.your_actual_api_key_here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=Project Lumen Reports

# Enable scheduled reports
SCHEDULED_REPORTS_ENABLED=True
DEFAULT_REPORT_SCHEDULE=weekly
REPORT_GENERATION_DAY=1  # Monday
REPORT_GENERATION_HOUR=8  # 8 AM UTC
```

### 3. Start the Server

```bash
python -m uvicorn backend.main:app --reload
```

The report scheduler will start automatically on server startup.

---

## API Usage

### 🚀 Generate Report Immediately (On-Demand)

**Perfect for when someone says: "Generate report"**

```bash
POST /scheduled-reports/generate-now
Content-Type: application/json

{
  "user_id": "0x1234567890abcdef",
  "email": "user@example.com",
  "report_type": "weekly"
}
```

**Report Types:**
- `weekly` - Last 7 days
- `monthly` - Last 30 days
- `quarterly` - Last 3 months
- `yearly` - Last 12 months

**Response:**
```json
{
  "success": true,
  "message": "Report generation initiated. Weekly report will be emailed to user@example.com shortly.",
  "details": {
    "user_id": "0x1234567890abcdef",
    "report_type": "weekly",
    "email": "user@example.com",
    "status": "processing",
    "agents_used": [
      "Personal Finance Agent",
      "Goal Planner Agent",
      "Savings Opportunity Agent",
      "Fraud Detection Agent",
      "Pattern Detection Agent",
      "Behavioral Analysis Agent",
      "Compliance Agent",
      "Audit Agent"
    ]
  }
}
```

### 📅 Schedule Weekly Reports

```bash
POST /scheduled-reports/schedule/weekly
Content-Type: application/json

{
  "user_id": "0x1234567890abcdef",
  "email": "user@example.com",
  "day_of_week": 1,  // 0=Monday, 6=Sunday
  "hour": 8,          // 24-hour format
  "minute": 0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Weekly report scheduled for Monday at 08:00 UTC",
  "schedule": {
    "user_id": "0x1234567890abcdef",
    "email": "user@example.com",
    "frequency": "weekly",
    "day_of_week": 1,
    "day_name": "Monday",
    "time": "08:00 UTC"
  }
}
```

### 📅 Schedule Monthly Reports

```bash
POST /scheduled-reports/schedule/monthly
Content-Type: application/json

{
  "user_id": "0x1234567890abcdef",
  "email": "user@example.com",
  "day_of_month": 1,  // 1-28
  "hour": 8,
  "minute": 0
}
```

### ❌ Cancel Scheduled Reports

```bash
DELETE /scheduled-reports/schedule/{user_id}
```

### ℹ️ Check User's Schedule

```bash
GET /scheduled-reports/schedule/{user_id}
```

### 📋 List All Schedules (Admin)

```bash
GET /scheduled-reports/schedules
```

### ⚙️ Check Scheduler Status

```bash
GET /scheduled-reports/status
```

**Response:**
```json
{
  "success": true,
  "scheduler": {
    "enabled": true,
    "running": true,
    "default_schedule": "weekly",
    "default_day": 1,
    "default_hour": 8
  },
  "email": {
    "configured": true,
    "from_email": "noreply@projectlumen.ai",
    "from_name": "Project Lumen Financial Reports"
  }
}
```

---

## How It Works

### Report Generation Flow

```
1. User Request ("generate report")
   ↓
2. API receives request (/scheduled-reports/generate-now)
   ↓
3. Agentic Report Generator activates
   ↓
4. RAG Retrieval Phase
   - Query vector store for spending data
   - Query for budget information
   - Query for goal data
   - Hybrid search: Dense + Sparse + Reranking
   ↓
5. Multi-Agent Analysis Phase
   - Personal Finance Agent: Spending analysis
   - Goal Planner Agent: Goal progress
   - Savings Agent: Identifies opportunities
   - Fraud Agent: Anomaly detection
   - Pattern Agent: Trend analysis
   - Behavioral Agent: Habit insights
   - Compliance Agent: Policy checks
   - Audit Agent: Data validation
   ↓
6. Synthesis Phase
   - Combine all agent insights
   - Calculate financial health score
   - Generate recommendations
   - Create executive summary
   ↓
7. Report Generation
   - Create beautiful HTML report
   - Include all visualizations
   - Add progress bars, charts
   ↓
8. Email Delivery
   - Create email with summary
   - Attach full HTML report
   - Send via SendGrid
   ↓
9. User receives comprehensive report in email
```

### Scheduled Report Flow

```
1. Scheduler starts on server startup
   ↓
2. Loads all saved schedules from JSON
   ↓
3. APScheduler creates cron jobs
   ↓
4. At scheduled time (e.g., Monday 8 AM):
   - Trigger report generation
   - Run full agentic RAG analysis
   - Generate report
   - Email to user
   ↓
5. Repeat weekly/monthly automatically
```

---

## Example Report Content

### Executive Summary
- **Financial Health Score**: 85/100 (Excellent)
- **Total Spending**: $2,450.00
- **Budget Usage**: 67.3%
- **Active Goals**: 3
- **Potential Savings**: $150.00

### Key Highlights
- ⚠️ Budget usage at 92% - Consider reducing spending
- 💡 Potential savings of $150.00 identified
- ℹ️ Tracking 3 active financial goals

### Financial Overview
- Total Spending: $2,450.00
- Monthly Average: $2,300.00
- Spending Trend: Increasing
- Budget: $2,100 used of $3,000 (70%)

**Top Categories:**
1. Dining - $800.00 (32.7%)
2. Groceries - $500.00 (20.4%)
3. Shopping - $450.00 (18.4%)
4. Transportation - $350.00 (14.3%)
5. Entertainment - $250.00 (10.2%)

### Goal Progress
1. **Emergency Fund** - 65% complete ($6,500 / $10,000)
2. **Vacation Savings** - 40% complete ($800 / $2,000)
3. **New Laptop** - 25% complete ($300 / $1,200)

### Savings Opportunities
1. **Subscription Optimization** - Potential savings: $75/month
   - You have 5 active subscriptions. Cancel unused ones.
2. **Dining Cost Reduction** - Potential savings: $50/month
   - Reduce dining out frequency by 2 meals/week
3. **Grocery Shopping Optimization** - Potential savings: $25/month
   - Switch to bulk buying for staples

### Recommendations
1. **HIGH PRIORITY - Budget Alert**
   - Your spending is approaching your budget limit
   - Action: Review and reduce non-essential spending

2. **MEDIUM PRIORITY - Savings Opportunity**
   - Potential savings of $150/month identified
   - Action: Review savings opportunities

---

## Architecture

### New Components

```
backend/
├── agents/
│   └── report_generation_agent.py      # Multi-agent orchestrator
├── utils/
│   ├── email_service.py                # SendGrid integration
│   ├── comprehensive_report_generator.py  # HTML report creation
│   └── report_scheduler.py             # APScheduler integration
└── routers/
    └── scheduled_reports.py            # API endpoints
```

### Key Classes

1. **AgenticReportGenerator** (`report_generation_agent.py`)
   - Coordinates all 8 AI agents
   - Orchestrates RAG retrieval
   - Synthesizes comprehensive insights

2. **EmailService** (`email_service.py`)
   - SendGrid API integration
   - Email template creation
   - Attachment handling

3. **ComprehensiveReportGenerator** (`comprehensive_report_generator.py`)
   - Beautiful HTML report creation
   - Responsive design
   - Chart and progress bar generation

4. **ReportScheduler** (`report_scheduler.py`)
   - APScheduler integration
   - Cron job management
   - Schedule persistence

---

## Testing

### Test On-Demand Report Generation

```bash
curl -X POST http://localhost:8000/scheduled-reports/generate-now \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "email": "your.email@example.com",
    "report_type": "weekly"
  }'
```

### Test Weekly Schedule

```bash
curl -X POST http://localhost:8000/scheduled-reports/schedule/weekly \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "email": "your.email@example.com",
    "day_of_week": 1,
    "hour": 8,
    "minute": 0
  }'
```

### Check Status

```bash
curl http://localhost:8000/scheduled-reports/status
```

---

## Troubleshooting

### Email Not Sending

1. **Check SendGrid API Key**
   ```bash
   # Verify in .env
   SENDGRID_API_KEY=SG.your_key_here
   ```

2. **Check Server Logs**
   ```bash
   tail -f backend/lumen.log | grep -i email
   ```

3. **Verify SendGrid Account**
   - Check sending limits
   - Verify sender email domain
   - Check API key permissions

### Scheduler Not Running

1. **Check Configuration**
   ```bash
   # In .env
   SCHEDULED_REPORTS_ENABLED=True
   ```

2. **Check Server Logs**
   ```bash
   tail -f backend/lumen.log | grep -i scheduler
   ```

3. **Verify Schedules**
   ```bash
   curl http://localhost:8000/scheduled-reports/schedules
   ```

### Reports Empty or Missing Data

1. **Check User Data**
   - Ensure user has receipts/transactions
   - Verify data is indexed in RAG system

2. **Check Agent Logs**
   ```bash
   tail -f backend/lumen.log | grep -i agent
   ```

---

## Production Deployment

### Environment Variables

```bash
# Production settings
DEBUG=False
SCHEDULED_REPORTS_ENABLED=True

# SendGrid (use production API key)
SENDGRID_API_KEY=SG.production_key_here
SENDGRID_FROM_EMAIL=reports@yourdomain.com
SENDGRID_FROM_NAME=Your Company Financial Reports

# Schedule (adjust for your timezone)
REPORT_GENERATION_DAY=1  # Monday
REPORT_GENERATION_HOUR=8  # 8 AM UTC
```

### Security Considerations

1. **API Key Security**
   - Never commit API keys to git
   - Use environment variables
   - Rotate keys regularly

2. **Email Validation**
   - Validate email addresses
   - Implement rate limiting
   - Add unsubscribe links (future)

3. **Data Privacy**
   - Encrypt sensitive data
   - Use HTTPS for all communications
   - Comply with data protection regulations

### Monitoring

1. **Track Email Delivery**
   - Monitor SendGrid dashboard
   - Set up delivery webhooks
   - Track bounce rates

2. **Monitor Scheduler**
   - Log all scheduled executions
   - Alert on failures
   - Track generation times

3. **Performance**
   - Monitor RAG query times
   - Track agent execution times
   - Optimize slow queries

---

## Future Enhancements

- [ ] PDF report generation (currently HTML only)
- [ ] Custom report templates per user
- [ ] Interactive charts and visualizations
- [ ] Report history and archive
- [ ] Unsubscribe functionality
- [ ] Email delivery status tracking
- [ ] Multi-language support
- [ ] SMS notifications
- [ ] Slack/Discord integration
- [ ] Report preview before sending

---

## Support

For issues or questions:
1. Check server logs: `backend/lumen.log`
2. Review API documentation: http://localhost:8000/docs
3. Check scheduler status: `/scheduled-reports/status`

---

## License

This feature is part of Project Lumen and follows the same license as the main project.
