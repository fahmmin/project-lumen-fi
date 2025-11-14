# Dashboard Backend API Requirements

This document outlines all the fields and data structures needed from the backend to replace hardcoded data in the frontend dashboard.

## Recommended Endpoint: `GET /dashboard/stats`

This endpoint should return comprehensive dashboard statistics. Optionally, it can accept a `user_id` parameter to filter by user.

---

## Response Structure

```json
{
  "status": "success",
  "data": {
    // ========== STATS CARDS ==========
    "statistics": {
      "documents_ingested": 45,           // Total documents processed
      "audits_performed": 32,             // Total audits run (from backend workspace)
      "blockchain_audits": 28,            // Total audits stored on blockchain (if available)
      "workspace_size_kb": 1250.5,        // Workspace size in KB
      "success_rate": 85,                 // Percentage of audits that passed
      "total_amount_audited": 125000.50   // Total amount from all audited invoices
    },

    // ========== AUDIT TREND CHART ==========
    // Weekly trend data for the last N weeks (default: 4)
    "audit_trends": [
      {
        "week": "2025-W01",
        "week_label": "Week 1",
        "date_range": "2025-01-01 to 2025-01-07",
        "audits_count": 12,
        "documents_count": 8,
        "total_amount": 45000.00
      },
      {
        "week": "2025-W02",
        "week_label": "Week 2",
        "date_range": "2025-01-08 to 2025-01-14",
        "audits_count": 19,
        "documents_count": 15,
        "total_amount": 52000.00
      },
      {
        "week": "2025-W03",
        "week_label": "Week 3",
        "date_range": "2025-01-15 to 2025-01-21",
        "audits_count": 15,
        "documents_count": 12,
        "total_amount": 38000.00
      },
      {
        "week": "2025-W04",
        "week_label": "Week 4",
        "date_range": "2025-01-22 to 2025-01-28",
        "audits_count": 22,
        "documents_count": 18,
        "total_amount": 65000.00
      }
    ],

    // ========== STATUS DISTRIBUTION PIE CHART ==========
    "status_distribution": [
      {
        "status": "pass",
        "name": "Pass",
        "count": 45,
        "percentage": 65.2,
        "color": "#000000"
      },
      {
        "status": "warning",
        "name": "Warning",
        "count": 18,
        "percentage": 26.1,
        "color": "#666666"
      },
      {
        "status": "error",
        "name": "Error",
        "count": 6,
        "percentage": 8.7,
        "color": "#999999"
      }
    ],

    // ========== CATEGORY SPENDING BAR CHART ==========
    "category_spending": [
      {
        "category": "Office Supplies",
        "amount": 4500.00,
        "count": 12,
        "percentage_of_total": 18.5
      },
      {
        "category": "Travel",
        "amount": 3200.00,
        "count": 8,
        "percentage_of_total": 13.2
      },
      {
        "category": "Software",
        "amount": 2800.00,
        "count": 5,
        "percentage_of_total": 11.5
      },
      {
        "category": "Utilities",
        "amount": 1500.00,
        "count": 4,
        "percentage_of_total": 6.2
      },
      {
        "category": "Marketing",
        "amount": 1200.00,
        "count": 3,
        "percentage_of_total": 4.9
      }
    ],

    // ========== RECENT AUDITS (Optional - if backend has audit data) ==========
    "recent_audits": [
      {
        "audit_id": "audit_20250128_001",
        "timestamp": "2025-01-28T10:30:00Z",
        "status": "pass",
        "vendor": "Acme Corp",
        "amount": 1250.00,
        "category": "Office Supplies",
        "invoice_date": "2025-01-25"
      },
      {
        "audit_id": "audit_20250127_002",
        "timestamp": "2025-01-27T14:15:00Z",
        "status": "warning",
        "vendor": "Tech Solutions Inc",
        "amount": 3500.00,
        "category": "Software",
        "invoice_date": "2025-01-20"
      },
      {
        "audit_id": "audit_20250126_001",
        "timestamp": "2025-01-26T09:00:00Z",
        "status": "pass",
        "vendor": "Global Travel",
        "amount": 850.00,
        "category": "Travel",
        "invoice_date": "2025-01-22"
      }
    ],

    // ========== ADDITIONAL METRICS (Optional) ==========
    "additional_metrics": {
      "average_audit_amount": 3125.00,
      "largest_audit_amount": 15000.00,
      "most_common_category": "Office Supplies",
      "most_common_vendor": "Acme Corp",
      "audits_this_month": 22,
      "audits_last_month": 18,
      "month_over_month_change": 22.2,  // Percentage
      "total_vendors": 45,
      "total_categories": 12
    }
  }
}
```

---

## Field Descriptions

### Statistics Object
- **documents_ingested**: Total number of documents processed/ingested
- **audits_performed**: Total number of audits executed (from workspace logs)
- **blockchain_audits**: Total audits stored on blockchain (if tracking available)
- **workspace_size_kb**: Total workspace size in kilobytes
- **success_rate**: Percentage of audits that passed (0-100)
- **total_amount_audited**: Sum of all amounts from audited invoices

### Audit Trends Array
Each object represents one week:
- **week**: ISO week format (YYYY-Www)
- **week_label**: Human-readable label (e.g., "Week 1")
- **date_range**: Date range string for display
- **audits_count**: Number of audits in that week
- **documents_count**: Number of documents processed in that week
- **total_amount**: Total amount audited in that week

### Status Distribution Array
Each object represents one status:
- **status**: Status code (pass, warning, error, fail)
- **name**: Display name (Pass, Warning, Error, Fail)
- **count**: Number of audits with this status
- **percentage**: Percentage of total audits (0-100)
- **color**: Hex color code for chart display

### Category Spending Array
Each object represents one category:
- **category**: Category name
- **amount**: Total amount spent in this category
- **count**: Number of audits/invoices in this category
- **percentage_of_total**: Percentage of total amount (0-100)

### Recent Audits Array (Optional)
Each object represents a recent audit:
- **audit_id**: Unique audit identifier
- **timestamp**: ISO 8601 timestamp
- **status**: Audit status (pass, warning, error)
- **vendor**: Vendor name
- **amount**: Invoice amount
- **category**: Invoice category
- **invoice_date**: Original invoice date

---

## Query Parameters

```
GET /dashboard/stats?user_id=user_123&weeks=4&limit=10
```

- **user_id** (optional): Filter by specific user
- **weeks** (optional, default: 4): Number of weeks for trend data
- **limit** (optional, default: 10): Number of recent audits to return

---

## Data Sources

The backend should aggregate data from:

1. **Workspace Logs** (`workspace.md`):
   - Count `### NEW DOCUMENT INGESTED` entries → `documents_ingested`
   - Count `### [AUDIT RUN]` entries → `audits_performed`
   - Calculate workspace file size → `workspace_size_kb`

2. **Audit Results** (from audit execution):
   - Parse audit results to extract:
     - Status (`overall_status`)
     - Invoice data (amount, category, vendor, date)
     - Timestamp
   - Aggregate by:
     - Week (for trends)
     - Status (for distribution)
     - Category (for spending analysis)

3. **Blockchain Data** (if available):
   - Query smart contract for audit count
   - This might require frontend to provide wallet address

---

## Implementation Notes

### If Backend Doesn't Have Full Audit Data

If the backend only has workspace logs and not full audit details, you can:

1. **Return partial data**: Only return what's available (stats from workspace)
2. **Frontend fills gaps**: Frontend can still calculate from blockchain audits
3. **Hybrid approach**: Backend provides workspace stats, frontend provides blockchain stats

### Minimum Required Fields

At minimum, the backend should provide:
```json
{
  "statistics": {
    "documents_ingested": 45,
    "audits_performed": 32,
    "workspace_size_kb": 1250.5
  }
}
```

The frontend can calculate the rest from blockchain audits if needed.

---

## Current Frontend Usage

The frontend currently:
- ✅ Gets `documents_ingested`, `audits_performed`, `workspace_size_kb` from `/memory/stats`
- ✅ Calculates blockchain audit stats from decrypted audits
- ✅ Calculates trends, status distribution, and category spending from decrypted audits
- ⚠️ Falls back to empty data if blockchain audits aren't available

---

## Recommended Implementation Priority

1. **High Priority** (Replace hardcoded fallbacks):
   - `audit_trends` - Weekly audit/document counts
   - `status_distribution` - Pass/warning/error breakdown
   - `category_spending` - Category-wise spending analysis

2. **Medium Priority** (Enhance existing data):
   - `success_rate` - Calculate from audit results
   - `total_amount_audited` - Sum of all invoice amounts
   - `recent_audits` - Recent audit summaries

3. **Low Priority** (Nice to have):
   - `additional_metrics` - Extra insights
   - `blockchain_audits` count (if trackable)

---

## Example Backend Implementation

```python
@router.get("/dashboard/stats")
async def get_dashboard_stats(
    user_id: Optional[str] = None,
    weeks: int = 4,
    limit: int = 10
):
    """
    Get comprehensive dashboard statistics
    
    Args:
        user_id: Optional user ID to filter by
        weeks: Number of weeks for trend data (default: 4)
        limit: Number of recent audits to return (default: 10)
    
    Returns:
        Dashboard statistics and charts data
    """
    # Get workspace stats
    workspace_stats = get_workspace_statistics()
    
    # Get audit data from workspace or database
    audits = get_audit_data(user_id=user_id)
    
    # Calculate statistics
    stats = {
        "documents_ingested": workspace_stats["documents_ingested"],
        "audits_performed": workspace_stats["audits_performed"],
        "workspace_size_kb": workspace_stats["size_kb"],
        "success_rate": calculate_success_rate(audits),
        "total_amount_audited": sum(a.amount for a in audits)
    }
    
    # Calculate trends
    trends = calculate_weekly_trends(audits, weeks=weeks)
    
    # Calculate status distribution
    status_dist = calculate_status_distribution(audits)
    
    # Calculate category spending
    category_spending = calculate_category_spending(audits)
    
    # Get recent audits
    recent = get_recent_audits(audits, limit=limit)
    
    return {
        "status": "success",
        "data": {
            "statistics": stats,
            "audit_trends": trends,
            "status_distribution": status_dist,
            "category_spending": category_spending,
            "recent_audits": recent
        }
    }
```

---

## Frontend Integration

Once the backend endpoint is ready, update the frontend:

```typescript
// In services/api.ts
export const dashboardAPI = {
  async getDashboardStats(userId?: string, weeks: number = 4): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/dashboard/stats`, {
      params: { user_id: userId, weeks }
    });
    return response.data;
  }
};

// In dashboard page
const dashboardData = await dashboardAPI.getDashboardStats();
// Use dashboardData.data.audit_trends, status_distribution, etc.
```

