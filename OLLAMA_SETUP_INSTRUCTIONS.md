# Ollama Setup Instructions for PROJECT LUMEN

## 🎯 Overview

Your PROJECT LUMEN backend is now configured to use **Ollama with Llama 3.1 8B** instead of Gemini API. All LLM operations (receipt parsing, email parsing, etc.) will now run on your GPU computer.

---

## 📋 What You Need to Do on Your GPU Computer

### Step 1: Install Ollama

On your **GPU computer** (same network), run:

```bash
# For Linux
curl -fsSL https://ollama.com/install.sh | sh

# For macOS
brew install ollama

# For Windows
# Download from https://ollama.com/download
```

### Step 2: Download Llama 3.1 8B Model

```bash
ollama pull lllama3.1:8b
```

This will download ~5GB. The download may take 5-15 minutes depending on your internet speed.

### Step 3: Verify Ollama is Running

```bash
# Check if Ollama is running
ollama list

# You should see:
# NAME                              ID              SIZE      MODIFIED
# lllama3.1:8b      xxx             4.7GB     X minutes ago
```

### Step 4: Configure Network Access

**Important:** Ollama by default only listens on localhost. You need to allow network connections.

#### Option A: Environment Variable (Recommended)

```bash
# On Linux/macOS - Add to ~/.bashrc or ~/.zshrc
export OLLAMA_HOST=0.0.0.0:11434

# Then restart Ollama
# On Linux with systemd:
sudo systemctl restart ollama

# On macOS/manual:
# Kill ollama process and restart
pkill ollama
ollama serve
```

#### Option B: Systemd Service (Linux Only)

```bash
# Edit systemd service
sudo systemctl edit ollama

# Add this:
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"

# Save and restart
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Step 5: Configure Firewall

Allow connections on port 11434:

```bash
# Ubuntu/Debian
sudo ufw allow 11434/tcp

# Fedora/RHEL
sudo firewall-cmd --permanent --add-port=11434/tcp
sudo firewall-cmd --reload

# macOS
# Usually no firewall config needed
```

### Step 6: Find Your GPU Computer's IP Address

```bash
# Linux/macOS
hostname -I
# or
ip addr show

# Windows
ipconfig

# Example output: 192.168.1.100
```

**Note this IP address** - you'll need it for the backend configuration.

### Step 7: Test Ollama is Accessible from Network

From **another computer on your network** (or from your backend server):

```bash
# Replace 192.168.1.100 with your GPU computer's IP
curl http://192.168.1.100:11434/api/tags

# Should return JSON with available models
# If this fails, check firewall and OLLAMA_HOST settings
```

---

## ⚙️ Configure Backend to Use Ollama

### Step 1: Update .env File

On your **backend server** (where PROJECT LUMEN runs):

```bash
cd /home/user/hackasol2

# Create/update .env file
nano .env

# Or copy from example
cp .env.example .env
```

### Step 2: Set Ollama Configuration

Edit `.env` and set:

```bash
# LLM Provider
LLM_PROVIDER=ollama

# Ollama Server URL (change IP to your GPU computer)
OLLAMA_BASE_URL=http://192.168.1.100:11434

# Model name
OLLAMA_MODEL=lllama3.1:8b
```

**IMPORTANT:** Replace `192.168.1.100` with your actual GPU computer's IP address from Step 6.

If your backend and Ollama are on the **same machine**, use:

```bash
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 🧪 Test the Integration

### Test 1: Health Check API

Start your backend:

```bash
cd /home/user/hackasol2
python -m uvicorn backend.main:app --reload
```

In another terminal, test the health check:

```bash
curl http://localhost:8000/health

# Should show:
# {
#   "status": "healthy",
#   "ollama_status": "connected",
#   "model": "lllama3.1:8b"
# }
```

### Test 2: Email Parser Test

```bash
curl -X POST http://localhost:8000/email/parse/test \
  -H "Content-Type: application/json" \
  -d '{
    "email_subject": "Your Zomato Order Confirmation",
    "email_body": "Thank you for ordering from Zomato\n\nOrder Summary:\nDate: 12/10/2024\n\nSubtotal: $52.47\nTax: $4.72\nTotal: $70"
  }'

# Should return:
# {
#   "success": true,
#   "extracted_fields": {
#     "vendor": "Zomato",
#     "amount": 70.0,
#     "date": "2024-12-10",
#     "category": "dining",
#     "method": "ollama",
#     "confidence": 0.95
#   }
# }
```

**Expected Result:** vendor should be "Zomato" and method should be "ollama" (not "regex")!

### Test 3: Receipt Upload

Upload a test receipt PDF/image through the API:

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@test_receipt.pdf" \
  -F "user_id=test_user"

# Should parse the receipt using Ollama LLM
```

---

## 🔍 Troubleshooting

### Issue 1: "Cannot connect to Ollama at http://..."

**Symptoms:**

```
Exception: Cannot connect to Ollama server at http://192.168.1.100:11434
```

**Solutions:**

1. Check Ollama is running on GPU computer: `ollama list`
2. Check firewall allows port 11434
3. Verify `OLLAMA_HOST=0.0.0.0:11434` is set
4. Test connectivity: `curl http://<GPU_IP>:11434/api/tags`
5. Check both computers are on same network

### Issue 2: "Model 'lllama3.1:8b' not found"

**Solutions:**

1. Pull the model: `ollama pull lllama3.1:8b`
2. Check model is downloaded: `ollama list`
3. Verify model name in `.env` matches exactly

### Issue 3: Slow Response Times

**Symptoms:**

- Requests taking > 10 seconds
- "Ollama request timed out"

**Solutions:**

1. Check GPU is being used: `nvidia-smi` (should show ollama process)
2. Ensure model is fully loaded (first request loads model into VRAM)
3. Increase timeout in code if needed (default is 60 seconds)
4. Consider using smaller model if GPU has limited VRAM

### Issue 4: Still Using "regex" method instead of "ollama"

**Symptoms:**

```json
{
  "method": "regex",
  "confidence": 0.6
}
```

**Solutions:**

1. Check `.env` has `LLM_PROVIDER=ollama`
2. Restart backend server after changing `.env`
3. Check backend logs for Ollama connection errors
4. Verify Ollama is accessible from backend server

---

## 📊 Performance Expectations

### With GPU (NVIDIA RTX 3060 or better):

| Metric              | Value                       |
| ------------------- | --------------------------- |
| First Request       | 3-5 seconds (model loading) |
| Subsequent Requests | 0.5-2 seconds               |
| Throughput          | 20-50 tokens/sec            |
| VRAM Usage          | ~5-6 GB                     |

### With CPU (Fallback):

| Metric              | Value          |
| ------------------- | -------------- |
| First Request       | 10-20 seconds  |
| Subsequent Requests | 5-10 seconds   |
| Throughput          | 2-5 tokens/sec |
| RAM Usage           | ~8-10 GB       |

---

## 🔒 Security Notes

1. **Firewall:** Only allow port 11434 from trusted IPs
2. **Local Network Only:** Don't expose Ollama to the internet
3. **Data Privacy:** All financial data stays on your network (never sent to cloud)

---

## 🚀 What Changed in the Code

### Files Updated:

1. **`backend/utils/ollama_client.py`** (NEW)

   - Unified client for Ollama API
   - Handles connection, generation, JSON parsing
   - Health checks

2. **`backend/utils/llm_parser.py`** (UPDATED)

   - Now uses Ollama instead of OpenAI/Gemini
   - Simplified code, no cloud API dependencies

3. **`backend/utils/email_parser.py`** (UPDATED)

   - Primary: Ollama LLM
   - Fallback: Regex extraction
   - Better Indian vendor recognition

4. **`backend/config.py`** (UPDATED)

   - Added `OLLAMA_BASE_URL` and `OLLAMA_MODEL` settings
   - Changed default `LLM_PROVIDER` to "ollama"

5. **`.env.example`** (UPDATED)
   - Added Ollama configuration examples
   - Network setup instructions

---

## ✅ Quick Verification Checklist

- [ ] Ollama installed on GPU computer
- [ ] Llama 3.1 8B model downloaded (`ollama pull`)
- [ ] Ollama listening on `0.0.0.0:11434`
- [ ] Firewall allows port 11434
- [ ] Can access Ollama from backend server (`curl test`)
- [ ] `.env` file updated with correct IP address
- [ ] Backend server restarted
- [ ] Health check passes
- [ ] Email parser test returns `"method": "ollama"`

---

## 🎓 Next Steps

1. **Test with real receipts** - Upload PDFs and check Zomato/Swiggy recognition
2. **Monitor performance** - Check logs for latency
3. **Fine-tune (optional)** - See `FINE_TUNING_PLAN.md` for better accuracy
4. **Scale up** - Use `mistral:7b` for faster inference or `llama3.1:70b` for better accuracy

---

## 💡 Tips

- **Keep Ollama updated:** `curl -fsSL https://ollama.com/install.sh | sh`
- **Try different models:** `ollama pull mistral:7b-instruct`
- **Monitor GPU:** Use `nvidia-smi -l 1` to watch VRAM usage
- **Check logs:** Backend logs show Ollama connection status

---

## 🆘 Need Help?

1. Check Ollama logs: `journalctl -u ollama -f` (Linux)
2. Check backend logs: Look for "Ollama" messages
3. Test Ollama directly: `curl http://localhost:11434/api/generate ...`

---

**Everything is configured! Just follow the steps above on your GPU computer and you're ready to go!** 🚀
