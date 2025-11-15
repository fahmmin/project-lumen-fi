# MongoDB Total Amount Calculation Flow

## Overview
This document explains how the total amount is calculated from MongoDB for the dashboard display.

## Flow Diagram

```
1. AUDIT CREATION
   ↓
   [Orchestrator/Quick Audit] extracts amount from invoice_data
   ↓
   amount = invoice_data.get('amount', 0.0)
   ↓
   [MongoDB Storage] saves audit document with amount field
   ↓
   {
     "audit_id": "...",
     "user_id": "...",
     "amount": 1250.0,  ← Stored directly at document root
     "audit_report": {...},
     "timestamp": "...",
     "vendor": "...",
     "status": "...",
     "category": "..."
   }

2. DASHBOARD LOADING
   ↓
   [Frontend] calls loadMongoAudits()
   ↓
   Parallel API calls:
   ├─→ GET /audit/user/{userId}/audits
   │   ↓
   │   [Backend] mongo_storage.get_user_audits(user_id, limit=1000)
   │   ↓
   │   [MongoDB] db.audits.find({"user_id": userId})
   │   ↓
   │   Returns: Array of audit documents with "amount" field
   │
   └─→ GET /audit/user/{userId}/stats
       ↓
       [Backend] mongo_storage.get_audit_stats(user_id)
       ↓
       [MongoDB] Aggregation pipeline:
       [
         {"$match": {"user_id": userId}},
         {"$group": {
           "_id": None,
           "total_amount": {"$sum": "$amount"}  ← MongoDB sums all amounts
         }}
       ]
       ↓
       Returns: {total_audits: X, total_amount: Y, ...}

3. FRONTEND CALCULATION (Two Methods)

   Method A: Calculate from Individual Audits
   ↓
   calculateStatsFromMongoAudits(audits)
   ↓
   let totalAmount = 0;
   audits.forEach((audit) => {
     const amount = audit.amount || 0;  ← Read from document root
     totalAmount += amount;
   });
   ↓
   setAuditStats({ totalAmount, ... })

   Method B: Use Aggregated Stats
   ↓
   calculateStatsFromMongoStats(statsData)
   ↓
   setAuditStats({ 
     totalAmount: statsData.total_amount,  ← Use pre-calculated sum
     ...
   })

4. DISPLAY
   ↓
   Total Amount = auditStats?.totalAmount ?? mongoStats?.total_amount ?? 0
   ↓
   Display: ${amount.toLocaleString()}
```

## Key Points

### 1. Amount Storage Location
- **Field**: `amount` (at document root level, not nested)
- **Type**: `float` (number)
- **Source**: Extracted from `invoice_data.amount` during audit creation
- **Default**: `0.0` if not provided

### 2. Two Calculation Methods

#### Method A: Frontend Calculation (Preferred)
- **When**: When `audits.length > 0`
- **How**: Loops through all audit documents and sums `audit.amount`
- **Code**: `calculateStatsFromMongoAudits(audits)`
- **Pros**: 
  - Real-time calculation
  - Can filter/process data before summing
- **Cons**: 
  - Requires fetching all audit documents
  - More frontend processing

#### Method B: Backend Aggregation (Fallback)
- **When**: When no audits returned but `statsData.total_audits > 0`
- **How**: Uses MongoDB aggregation pipeline to sum amounts
- **Code**: `calculateStatsFromMongoStats(statsData)`
- **Pros**: 
  - Efficient (database-level calculation)
  - No need to fetch all documents
- **Cons**: 
  - Less flexible
  - Requires MongoDB aggregation support

### 3. Display Priority
The dashboard displays total amount in this order:
1. `auditStats?.totalAmount` (from frontend calculation)
2. `mongoStats?.total_amount` (from backend aggregation)
3. `0` (fallback)

## Code Locations

### Backend - Saving Amount
- **File**: `backend/utils/mongo_storage.py`
- **Method**: `save_audit()`
- **Line**: ~128
```python
audit_doc = {
    "audit_id": audit_id,
    "user_id": user_id,
    "amount": amount,  # ← Stored here
    "audit_report": audit_report,
    ...
}
```

### Backend - Aggregated Stats
- **File**: `backend/utils/mongo_storage.py`
- **Method**: `get_audit_stats()`
- **Line**: ~230-238
```python
pipeline = [
    {"$match": query},
    {"$group": {
        "_id": None,
        "total_amount": {"$sum": "$amount"}  # ← MongoDB aggregation
    }}
]
```

### Frontend - Individual Audit Calculation
- **File**: `nextjs-app/app/dashboard/page.tsx`
- **Method**: `calculateStatsFromMongoAudits()`
- **Line**: ~411-415
```typescript
audits.forEach((audit: any, index: number) => {
    const amount = audit.amount || 0;  // ← Read from document
    totalAmount += amount;  // ← Sum in frontend
});
```

### Frontend - Display
- **File**: `nextjs-app/app/dashboard/page.tsx`
- **Line**: ~702-711
```typescript
const amount = auditStats?.totalAmount ?? mongoStats?.total_amount ?? 0;
// Display: ${amount.toLocaleString()}
```

## Debugging

### Check if Amount is Saved
```javascript
// In browser console after loading dashboard
console.log('[Dashboard] Sample audits:', audits.slice(0, 3).map(a => ({
    audit_id: a.audit_id,
    amount: a.amount,
    hasAmount: 'amount' in a
})));
```

### Check MongoDB Directly
```javascript
// MongoDB query
db.audits.find({user_id: "your_user_id"}, {audit_id: 1, amount: 1})
```

### Check Aggregated Stats
```javascript
// In browser console
console.log('mongoStats:', mongoStats);
// Should show: {total_audits: X, total_amount: Y, ...}
```

## Common Issues

1. **Amount is 0 or undefined**
   - Check if `amount` field exists in MongoDB document
   - Verify `invoice_data.amount` is being extracted correctly during audit creation
   - Check MongoDB connection and query results

2. **Total Amount not updating**
   - Ensure `loadMongoAudits()` is called after new audits are saved
   - Check if `auditSaved` event is being dispatched
   - Verify `calculateStatsFromMongoAudits()` is being called

3. **Mismatch between methods**
   - Method A (frontend) and Method B (backend) should give same result
   - If different, check for:
     - Missing `amount` field in some documents
     - Type mismatches (string vs number)
     - Filtering issues (user_id mismatch)

