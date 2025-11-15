# AI Assistant Chatbot - Universal Natural Language API Router

## Overview

Project Lumen now includes an **intelligent AI chatbot** that allows users to interact with **ALL 71 API endpoints** using natural language. No need to remember endpoint paths, HTTP methods, or request formats - just talk to the assistant naturally!

### What It Does

The AI Assistant automatically:
1. **Understands** what you want (intent detection)
2. **Finds** the right API endpoint (semantic search + LLM)
3. **Extracts** required parameters from your message (LLM parsing)
4. **Executes** the API call internally (no changes to existing APIs)
5. **Responds** in friendly natural language (not JSON!)

### Key Features

✨ **Zero Changes to Existing APIs** - Works with all endpoints as-is
🧠 **Intelligent Intent Detection** - Uses LLM + RAG for accurate routing
💬 **Natural Language** - Input and output in plain English
🔄 **Multi-Turn Conversations** - Asks follow-up questions when needed
📊 **71 Endpoints Covered** - Every single API automatically supported
🎯 **Context-Aware** - Remembers conversation history
⚡ **Auto-Discovery** - New endpoints automatically registered

---

## Quick Start

### 1. Start the Server

```bash
python -m uvicorn backend.main:app --reload
```

The chatbot initializes automatically on startup and scans all endpoints.

### 2. Chat with the Assistant

```bash
POST /assistant/chat
Content-Type: application/json

{
  "message": "I spent $50 at Starbucks today",
  "user_id": "0x1234567890abcdef"
}
```

**Response:**
```json
{
  "response": "✅ Great! I've added your $50.00 receipt from Starbucks to your expenses!",
  "session_id": "abc-123-def-456",
  "action_taken": {
    "endpoint": "/email/parse-receipt",
    "method": "POST",
    "success": true,
    "parameters": {
      "user_id": "0x1234567890abcdef",
      "vendor": "Starbucks",
      "amount": 50.0,
      "date": "2025-11-15"
    }
  },
  "follow_up_needed": false,
  "suggestions": [
    "Want to see your spending dashboard?",
    "Check if you have any budget alerts"
  ]
}
```

---

## Example Conversations

### Example 1: Add Receipt

```
👤 User: "I spent $35 at Target yesterday"

🤖 Assistant: "✅ Great! I've added your $35.00 receipt from Target to your expenses!"

   Suggestions:
   - Want to see your spending dashboard?
   - Check if you have any budget alerts
```

**What happened:**
- Detected intent: Upload receipt
- Extracted: vendor="Target", amount=35.0, date="2025-11-14"
- Called: `POST /email/parse-receipt`
- Response: Friendly confirmation

---

### Example 2: Create Goal

```
👤 User: "I want to save $10000 for a house"

🤖 Assistant: "By when would you like to reach this goal?"

👤 User: "In 2 years"

🤖 Assistant: "🎯 Awesome! I've created your goal: 'Save for house' with a target of $10,000.00!"

   Suggestions:
   - Want to see a savings plan?
   - Check your goal progress
```

**What happened:**
- Detected intent: Create goal
- Extracted: name="Save for house", target_amount=10000
- Missing: target_date (required parameter)
- Asked follow-up question
- User provided: "In 2 years"
- Calculated: target_date="2027-11-15"
- Called: `POST /goals/`
- Response: Success with suggestions

---

### Example 3: Generate Report

```
👤 User: "Send me a financial report"

🤖 Assistant: "📧 Perfect! I'm generating your weekly report now. I'll email it to you@example.com shortly!"

   Suggestions:
   - Schedule weekly reports
   - View report history
```

**What happened:**
- Detected intent: Generate report
- Extracted: user_id (from context), email (from context), report_type="weekly"
- Called: `POST /scheduled-reports/generate-now`
- Response: Confirmation with email details

---

### Example 4: Dashboard

```
👤 User: "Show me my spending dashboard"

🤖 Assistant: "📊 This period you've spent $2,450.00. You're at 67.3% of your budget."

   Suggestions:
   - See spending breakdown by category
   - Get budget recommendations
   - Check for savings opportunities
```

**What happened:**
- Detected intent: View dashboard
- Called: `GET /finance/dashboard/{user_id}`
- Parsed response data
- Generated natural language summary

---

### Example 5: Update Salary

```
👤 User: "I earn $6000 per month"

🤖 Assistant: "✅ Updated! Your monthly salary is now set to $6,000.00."

   Suggestions:
   - Set up a budget
   - Create savings goals
```

**What happened:**
- Detected intent: Update salary
- Extracted: salary_monthly=6000
- Called: `POST /users/{user_id}/salary`
- Response: Confirmation

---

## Architecture

```
┌─────────────────────────────────┐
│  User Natural Language Input    │
│  "I spent $50 at Starbucks"     │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  POST /assistant/chat           │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  1. API Registry (71 endpoints) │
│     - Endpoint schemas          │
│     - Parameter definitions     │
│     - Semantic embeddings       │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  2. Intent Detection Agent      │
│     - Semantic search (top 5)   │
│     - LLM classification         │
│     - Confidence scoring        │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  3. Parameter Extraction Agent  │
│     - Pattern matching (regex)  │
│     - LLM extraction            │
│     - Type conversion           │
│     - Schema validation         │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  4. Follow-up Check             │
│     - Missing required params?  │
│     - Generate question         │
│     - Wait for user response    │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  5. API Orchestrator            │
│     - Build HTTP request        │
│     - Call internal endpoint    │
│     - Parse response            │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  6. Response Generator          │
│     - Convert JSON → NL         │
│     - Add emojis & formatting   │
│     - Generate suggestions      │
└──────────────┬──────────────────┘
               ↓
┌─────────────────────────────────┐
│  Natural Language Response       │
│  "✅ Added $50 receipt!"         │
└─────────────────────────────────┘
```

---

## Components

### 1. API Registry Builder (`api_registry.py`)

**Purpose:** Automatically discovers and catalogs all API endpoints

**Features:**
- Scans FastAPI app on startup
- Extracts endpoint paths, methods, parameters
- Creates semantic embeddings for search
- Stores 250+ natural language examples
- Categorizes endpoints (receipts, goals, reports, etc.)

**Registry Entry Example:**
```python
{
  "path": "/goals/",
  "method": "POST",
  "description": "Create a new financial goal",
  "parameters": {
    "user_id": {"type": "str", "required": True},
    "name": {"type": "str", "required": True},
    "target_amount": {"type": "float", "required": True},
    "target_date": {"type": "date", "required": True}
  },
  "examples": ["create a goal", "save for", "I want to save"],
  "category": "financial_goals"
}
```

---

### 2. Intent Detection Agent (`intent_detection_agent.py`)

**Purpose:** Determines which API endpoint to call

**Strategy:**
1. **Semantic Search** - Find top 5 matching endpoints using embeddings
2. **LLM Classification** - Use Ollama to refine selection
3. **Confidence Scoring** - Return confidence level (0.0-1.0)

**Example:**
```
Input: "I want to save money for vacation"
Semantic Search: [POST /goals/, GET /goals/, POST /users/...]
LLM Analysis: POST /goals/ (confidence: 0.95)
Output: {endpoint, method, confidence, reasoning}
```

---

### 3. Parameter Extraction Agent (`parameter_extraction_agent.py`)

**Purpose:** Extracts required parameters from natural language

**Techniques:**
1. **Pattern Matching** - Regex for amounts, dates, emails
2. **LLM Extraction** - Intelligent parsing with schema awareness
3. **Type Conversion** - String → int/float/date
4. **Context Injection** - Add user_id from session

**Example:**
```
Message: "I spent $50 at Starbucks yesterday"
Schema: {user_id, vendor, amount, date}

Extracted:
- vendor: "Starbucks" (from text)
- amount: 50.0 (pattern match)
- date: "2025-11-14" (yesterday → ISO date)
- user_id: "0x123..." (from context)
```

---

### 4. API Orchestrator (`api_orchestrator.py`)

**Purpose:** Executes internal HTTP calls to endpoints

**Features:**
- Makes async HTTP requests (GET, POST, PUT, DELETE)
- Handles path/query/body parameters
- 30-second timeout
- Error handling with retries
- No modifications to existing APIs!

**Example:**
```python
await orchestrator.execute_endpoint(
    endpoint=endpoint_schema,
    parameters={"user_id": "0x123", "amount": 50}
)
# → Makes POST http://localhost:8000/email/parse-receipt
```

---

### 5. Conversation Manager (`conversation_manager.py`)

**Purpose:** Handles multi-turn conversations

**Features:**
- Session management (UUID-based)
- Message history storage
- Context persistence (pending parameters, user data)
- JSON file persistence

**Session Example:**
```python
{
  "session_id": "abc-123",
  "user_id": "0x123...",
  "messages": [
    {"role": "user", "content": "I want to save money"},
    {"role": "assistant", "content": "How much?"},
    {"role": "user", "content": "$10000"}
  ],
  "context": {
    "waiting_for_parameter": True,
    "pending_endpoint": "/goals/",
    "pending_parameters": {"name": "savings"}
  }
}
```

---

### 6. Response Generator (`response_generator.py`)

**Purpose:** Converts API responses to natural language

**Features:**
- Category-specific formatting (receipts, goals, reports, etc.)
- Emoji integration (✅, 🎯, 📊, etc.)
- Suggestion generation
- Error handling with friendly messages

**Example:**
```python
API Result: {
  "success": true,
  "data": {"goal_id": "g123", "name": "Vacation", "target_amount": 5000}
}

Generated Response:
"🎯 Awesome! I've created your goal: 'Vacation' with a target of $5,000.00!"

Suggestions:
- "Want to see a savings plan?"
- "Check your goal progress"
```

---

## API Endpoints

### POST /assistant/chat

Main chatbot endpoint - handles all natural language requests

**Request:**
```json
{
  "message": "string (required)",
  "user_id": "string (optional)",
  "session_id": "string (optional)",
  "email": "string (optional)"
}
```

**Response:**
```json
{
  "response": "Natural language response",
  "session_id": "UUID",
  "action_taken": {
    "endpoint": "/path/to/endpoint",
    "method": "POST",
    "parameters": {...},
    "success": true,
    "response_data": {...}
  },
  "follow_up_needed": false,
  "follow_up_question": null,
  "suggestions": ["...", "..."]
}
```

---

### GET /assistant/capabilities

List all chatbot capabilities

**Response:**
```json
{
  "categories": [
    {
      "category": "financial_goals",
      "name": "Financial Goals",
      "endpoints": [...],
      "examples": ["create a goal", "show my goals", ...]
    },
    ...
  ],
  "total_endpoints": 71,
  "examples": ["I spent $50 at Starbucks", ...]
}
```

---

### GET /assistant/session/{session_id}/history

Get conversation history

**Response:**
```json
{
  "success": true,
  "session_id": "abc-123",
  "messages": [
    {
      "role": "user",
      "content": "I spent $50",
      "timestamp": "2025-11-15T10:30:00"
    },
    {
      "role": "assistant",
      "content": "✅ Added receipt!",
      "timestamp": "2025-11-15T10:30:01"
    }
  ],
  "total_messages": 2
}
```

---

### DELETE /assistant/session/{session_id}

Clear conversation session

---

### GET /assistant/status

Get system status

**Response:**
```json
{
  "success": true,
  "status": "operational",
  "components": {
    "api_registry": {
      "status": "operational",
      "endpoints_registered": 71,
      "categories": 15
    },
    "intent_detection": {"status": "operational"},
    "conversation_manager": {"status": "operational"}
  }
}
```

---

## Supported Commands

The assistant understands natural language for **all 71 endpoints**. Here are examples:

### User Profile
- "Create my profile"
- "Show my profile"
- "I earn $6000 per month"
- "Update my salary to $5000"

### Financial Goals
- "I want to save $10000 for a car"
- "Create a goal to buy a house"
- "Show my goals"
- "How's my vacation savings goal?"
- "Am I on track for my goals?"

### Spending & Dashboard
- "Show my dashboard"
- "How much did I spend this month?"
- "What's my financial health score?"
- "Give me budget recommendations"
- "Analyze my spending behavior"
- "Predict my next month's spending"

### Receipts
- "I spent $50 at Starbucks"
- "Add a receipt for $35 at Target"
- "Upload this email receipt"
- "Parse this voice recording"

### Reports
- "Generate a financial report"
- "Email me a weekly report"
- "Schedule monthly reports every 1st"
- "Send me a report right now"

### Subscriptions & Patterns
- "What subscriptions do I have?"
- "Show unused subscriptions"
- "What are my spending patterns?"
- "Any bills due soon?"

### Family Budgets
- "Create a family group"
- "Join family with code ABC123"
- "Show family dashboard"
- "How do I compare to my family?"

### Gamification
- "What's my level?"
- "Show leaderboard"
- "My achievements"
- "How many points do I have?"

### Social Comparison
- "How do I compare to others?"
- "What's my percentile?"
- "Am I spending too much?"
- "Show top spenders"

### Audit & Compliance
- "Audit this invoice"
- "Check compliance"
- "Is this receipt legitimate?"

---

## Technical Details

### Intent Detection Process

```python
# 1. Semantic Search
candidates = registry.search_endpoints("I spent $50 at Starbucks", top_k=5)
# Returns: [
#   {endpoint: "/email/parse-receipt", confidence: 0.87},
#   {endpoint: "/ingest/", confidence: 0.75},
#   ...
# ]

# 2. LLM Refinement
llm_result = ollama.classify(user_message, candidates)
# Returns: {
#   "selected_index": 1,
#   "confidence": 0.95,
#   "reasoning": "User wants to add a receipt"
# }

# 3. Final Result
endpoint = "/email/parse-receipt"
method = "POST"
confidence = 0.95
```

---

### Parameter Extraction Process

```python
# 1. Pattern Matching (Fast)
amount = extract_amount("$50") # → 50.0
date = extract_date("yesterday") # → "2025-11-14"

# 2. LLM Extraction (Intelligent)
llm_params = ollama.extract({
  "message": "I spent $50 at Starbucks yesterday",
  "schema": {
    "user_id": "required",
    "vendor": "optional",
    "amount": "optional",
    "date": "optional"
  }
})
# Returns: {
#   "vendor": "Starbucks",
#   "amount": 50.0,
#   "date": "2025-11-14"
# }

# 3. Context Injection
final_params = {
  **llm_params,
  "user_id": session.context["user_id"]  # From session
}
```

---

## Files Created

```
backend/
├── agents/
│   ├── api_registry.py              # Endpoint discovery & indexing
│   ├── intent_detection_agent.py    # NL → Endpoint mapping
│   ├── parameter_extraction_agent.py # Parameter extraction
│   ├── api_orchestrator.py          # Internal API calls
│   ├── conversation_manager.py      # Session management
│   └── response_generator.py        # JSON → Natural language
├── routers/
│   └── assistant.py                 # Main chatbot endpoint
└── models/
    └── conversation.py              # Pydantic models
```

---

## Data Storage

### API Registry
**File:** `backend/data/api_registry.json`

Contains all 71 registered endpoints with schemas and examples.

### Conversation Sessions
**File:** `backend/data/conversation_sessions.json`

Stores active conversation sessions with message history.

---

## Testing

### Test Basic Chat

```bash
curl -X POST http://localhost:8000/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I spent $50 at Starbucks",
    "user_id": "test_user_123"
  }'
```

### Test Multi-Turn

```bash
# First message
curl -X POST http://localhost:8000/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a goal to save money",
    "user_id": "test_user_123"
  }'

# Response will ask "How much?" and return session_id

# Second message
curl -X POST http://localhost:8000/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "$10000",
    "user_id": "test_user_123",
    "session_id": "abc-123-returned-from-above"
  }'
```

### Test Capabilities

```bash
curl http://localhost:8000/assistant/capabilities
```

---

## Troubleshooting

### Chatbot not understanding

**Check:**
1. Are endpoints registered? → `/assistant/status`
2. Is LLM running? → Check Ollama at `http://172.16.163.34:11434`
3. Check logs: `tail -f backend/lumen.log | grep -i assistant`

### Parameters not extracted

**Check:**
1. Is user_id in context or message?
2. Are dates in recognizable format?
3. Is amount using $ symbol?

### Follow-up not working

**Check:**
1. Is session_id being passed in second message?
2. Check session: `GET /assistant/session/{session_id}/history`

---

## Future Enhancements

- [ ] Voice input support (integrate with /voice/ endpoints)
- [ ] Proactive suggestions based on spending patterns
- [ ] Natural language queries (not just commands)
- [ ] Sentiment analysis
- [ ] Multi-language support
- [ ] Slack/Discord integration
- [ ] Mobile app integration

---

## Summary

✨ **The AI Assistant makes Project Lumen's 71 APIs accessible through natural language!**

- **Zero code changes** to existing endpoints
- **Automatic discovery** of new endpoints
- **Intelligent routing** with LLM + RAG
- **Multi-turn conversations** with context
- **Friendly responses** with suggestions

Just talk naturally, and the assistant handles the rest! 🚀
