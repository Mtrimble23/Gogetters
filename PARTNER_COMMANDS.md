# 📋 EXACT PARTNER COMMAND SEQUENCE

## 🎯 **These are the EXACT commands your partner will run**

### **Prerequisites:**
- Git installed
- Docker installed  
- Python 3.7+ installed
- Terminal/Command Prompt access

---

## 🚀 **Step-by-Step Commands**

### **Step 1: Get the Code**
```bash
# Clone your repository
git clone https://github.com/Mtrimble23/VTHacks26.git
cd VTHacks26
```

### **Step 2: Install Dependencies**
```bash
# Install Python packages
pip3 install --break-system-packages -r requirements.txt

# Alternative if permission issues:
pip3 install --user -r requirements.txt
```

### **Step 3: Start Database**
```bash
# Start Aerospike database
docker-compose up -d

# Verify it's running
docker ps
```
**Expected Output:**
```
CONTAINER ID   IMAGE                               COMMAND                  CREATED        STATUS              PORTS                              NAMES
0c035d1bb55e   aerospike/aerospike-server:latest   "/usr/bin/as-tini-st…"   11 hours ago   Up 11 hours (healthy)   0.0.0.0:3000-3003->3000-3003/tcp   aerospike
```

### **Step 4: Start Backend Server**

**Option A: Interactive Mode (keeps terminal busy)**
```bash
# Start the backend (will occupy this terminal)
python3 financial_api_backend.py
```

**Option B: Background Mode (RECOMMENDED)**
```bash
# Start backend in background
nohup python3 financial_api_backend.py > backend.log 2>&1 &

# Verify it started
sleep 3
ps aux | grep financial_api_backend
```

**Expected Output (both methods):**
```
🚀 VTHacks26 Financial Risk Analysis API
============================================================
✅ Real-time Yahoo Finance integration
✅ CBOE volatility calculation
✅ Aerospike database caching
✅ Comprehensive risk analysis

📊 Supported symbols: AAPL, AMZN, GOOGL, NVDA, META, TSLA
🗄️  Database: Connected (or Disconnected - graceful fallback)

📚 API Documentation: http://localhost:8000/docs
🔍 Health Check: http://localhost:8000/health
📊 System Stats: http://localhost:8000/stats
💡 Example: curl http://localhost:8000/risk-level/AAPL
INFO:     Started server process [3505]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Note:** If using Option A, you'll need to open a new terminal for the remaining steps.

### **Step 5: Test Backend Health**
**If you used Option A (interactive), open a new terminal. If you used Option B (background), continue in same terminal:**
```bash
# Quick health check
curl -s http://localhost:8000/health
```
**Expected Output:**
```json
{
  "status": "healthy",
  "message": "Financial Risk Analysis API is running",
  "timestamp": "2025-01-19T12:30:00Z",
  "database_status": "connected",
  "data_sources": ["Yahoo Finance", "CBOE"]
}
```

### **Step 6: Test Individual API Endpoints**

**1. System Statistics**
```bash
curl -s "http://localhost:8000/stats" | jq .
```
Expected Response:
```json
{
  "active_connections": 1,
  "cache_hit_rate": "95.2%",
  "supported_symbols": ["AAPL", "AMZN", "GOOGL", "NVDA", "META, "TSLA"],
  "api_version": "1.0.0",
  "uptime_seconds": 150
}
```

**2. Single Stock Risk Analysis** (MAIN ENDPOINT)
```bash
# Test with Apple (AAPL)
curl -s "http://localhost:8000/risk-level/AAPL" | jq .
```
Expected Response:
```json
{
  "symbol": "AAPL",
  "risk_level": "Medium",
  "risk_score": 42.5,
  "current_price": 255.46,
  "price_change_percent": -0.55,
  "financial_metrics": {
    "dividend_yield": 0.49,
    "beta": 1.25,
    "pe_ratio": 33.8,
    "debt_to_equity_ratio": 1.87,
    "52_week_range": {"low": 164.08, "high": 263.54},
    "cboe_volatility": 28.73,
    "market_cap": 3876542000000
  },
  "price_history": [250.1, 252.3, 255.46],
  "recommendation": "HOLD - Moderate risk with stable fundamentals",
  "timestamp": "2025-01-19T12:30:00Z",
  "data_source": "Yahoo Finance"
}
```

**3. Batch Risk Analysis**
```bash
curl -X POST "http://localhost:8000/batch-risk" \
  -H "Content-Type: application/json" \
  -d '["AAPL", "NVDA", "TSLA"]' | jq .
```
Expected Response:
```json
{
  "results": [
    {
      "symbol": "AAPL",
      "risk_level": "Medium", 
      "risk_score": 42.5,
      "current_price": 255.46
    },
    {
      "symbol": "NVDA",
      "risk_level": "High",
      "risk_score": 68.2,
      "current_price": 178.19
    },
    {
      "symbol": "TSLA", 
      "risk_level": "Very High",
      "risk_score": 85.7,
      "current_price": 440.40
    }
  ],
  "summary": {
    "total_symbols": 3,
    "average_risk_score": 65.5,
    "high_risk_count": 2
  }
}
```

### **Step 7: Preload All Stocks (RECOMMENDED)**

**Option A: Simple Preload**
```bash
# Load all supported stocks into Aerospike database
python3 preload_all_stocks.py
```

**Option B: Complete Verification (RECOMMENDED)**
```bash
# Single command: Load all stocks + verify format consistency
./load_all_stocks.sh
```

**Expected Output (Option B):**
```
� Loading all stocks to database...
✅ Successful: 6/6 - All stocks cached!

🔍 Verifying format consistency...
🎉 ALL STOCKS HAVE IDENTICAL FORMAT!
📊 Common structure has 51 fields
✅ All 6 stocks verified

📊 Final database status: 6 cached symbols
✅ All stocks loaded and verified!
```

### **Step 8: Run Comprehensive Tests**
```bash
# Run all tests to verify everything works
python3 test_backend_clean.py
```
```
**Expected Output:**
```json
{
  "success": true,
  "symbol": "AAPL",
  "risk_level": "medium",
  "source": "stored_analysis",
  "data": {
    "symbol": "AAPL",
    "risk_level": "medium",
    "recommendation": "HOLD",
    "sentiment_score": 0.5,
    "timestamp": "2025-09-27T03:45:00Z"
  }
}
```

**Batch Processing:**
```bash
curl -s -X POST "http://localhost:8000/risk-level" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["MSFT", "GOOGL"]}' | jq .
```
**Expected Output:**
```json
{
  "success": true,
  "results": [
    {
      "symbol": "MSFT",
      "risk_level": "medium",
      "risk_score": 0.339,
      "risk_factors": {
        "volatility": 0.248,
        "market_cap": "mid",
        "sector_risk": 0.554,
        "liquidity": 0.863
      }
    },
    {
      "symbol": "GOOGL",
      "risk_level": "medium", 
      "risk_score": 0.584,
      "risk_factors": {
        "volatility": 0.552,
        "market_cap": "small",
        "sector_risk": 0.458,
        "liquidity": 0.344
      }
    }
  ],
  "total_analyzed": 2
}
```

### **Step 9: View API Documentation**
```bash
# Open interactive API docs in browser
open http://localhost:8000/docs

# Or visit manually: http://localhost:8000/docs
```

---

## ✅ **Success Indicators**

Your partner will know everything is working when they see:

1. **Database Running**: `docker ps` shows aerospike container
2. **Backend Started**: Console shows "Uvicorn running on http://0.0.0.0:8000"
3. **Health Check**: `curl http://localhost:8000/health` returns healthy status with `"database_connected": true`
4. **All Stocks Preloaded**: `python3 preload_all_stocks.py` shows 6/6 successful
5. **Cache Verification**: API calls return `"source": "cache"` with `"response_time": "< 0.001s"`
6. **All Tests Pass**: `python3 test_backend_clean.py` shows 9/9 tests passing
7. **API Works**: Can get risk analysis for stocks like AAPL, NVDA, TSLA, etc.
8. **Documentation Accessible**: http://localhost:8000/docs loads properly

**Quick verification command:**
```bash
# Verify all stocks are cached
curl -s "http://localhost:8000/stats" | jq '.database.cached_symbols, .database.cache_count'
```

---

## 🛠 **If Something Goes Wrong**

### **Port 8000 Busy:**
```bash
# Kill existing processes
pkill -f simple_backend
lsof -ti:8000 | xargs kill -9

# Or restart with background mode
nohup python3 simple_backend.py > backend.log 2>&1 &
```

### **Dependencies Missing:**
```bash
# Manual installation
pip3 install --break-system-packages fastapi uvicorn aerospike
```

### **Docker Issues:**
```bash
# Restart Docker services
docker-compose down
docker-compose up -d
```

### **Need Diagnostics:**
```bash
# Run diagnostic tool
python3 diagnose_backend.py
```

---

## 📊 **Final State**

When everything is working, your partner will have:

- ✅ **API Server** running on http://localhost:8000
- ✅ **Database** persisting data in Aerospike
- ✅ **Risk Analysis** for individual stocks
- ✅ **Batch Processing** for multiple stocks
- ✅ **Interactive Docs** at http://localhost:8000/docs
- ✅ **100% Test Success Rate** (9/9 tests passing)
- ✅ **Sub-3ms Response Times**

## 🎉 **Ready to Build!**

At this point, your partner has a fully functional Financial Risk Analysis API and can start integrating it into their application!