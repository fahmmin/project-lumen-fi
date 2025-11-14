# PROJECT LUMEN - Quick Start Guide

## Step 1: Restart Server (IMPORTANT!)
```bash
# Stop current server: Ctrl+C
# Then restart:
./venv/Scripts/python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 2: Verify 15 Documents Loaded
```bash
curl http://localhost:8000/info | grep -A 5 indices
```
Expected: "documents": 15 (both vector_store and bm25)

## Step 3: Test Audit
```bash
curl -X POST http://localhost:8000/audit/ -H "Content-Type: application/json" -d '{"invoice_data":{"vendor":"Office Supplies Inc.","amount":1250.00,"invoice_number":"INV-001"}}'
```

## Status: READY FOR DEMO!
- 15 chunks indexed
- 3 AI agents operational
- RAG system functional
- See FINAL_STATUS.md for details
