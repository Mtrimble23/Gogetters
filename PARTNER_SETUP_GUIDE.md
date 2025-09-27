# 🚀 Partner Setup Guide - Risk Level HTTP API

## 📋 Quick Start Checklist

Your partner needs to do **ONLY 3 things** to get everything working:

### ✅ **Step 1: Install Dependencies**
```bash
pip3 install --break-system-packages fastapi uvicorn requests aerospike
```

### ✅ **Step 2: Start Aerospike (if not already running)**
```bash
docker-compose up -d
```

### ✅ **Step 3: Start the Backend**
```bash
python3 simple_backend.py
```

**That's it!** The Risk Level HTTP API will be running at `http://localhost:8000`

---

## 🎯 **What Your Partner Gets Immediately**

### **📊 Working Risk Level API Endpoints:**
- `GET /risk-level/{symbol}` - Get risk for any stock symbol
- `POST /risk-level` - Batch analysis with custom risk factors
- `GET /health` - Health check
- `GET /test-aerospike` - Test database connection
- `GET /docs` - Interactive API documentation

### **💾 Database Integration:**
- ✅ **Aerospike connected** on port 3000
- ✅ **Namespace**: `test`, **Set**: `finance`
- ✅ **Auto-indexing** on symbol, timestamp, risk_level, sentiment_score
- ✅ **Data persistence** - all risk analyses saved automatically

### **🧪 Test Scripts Ready:**
- `python3 test_risk_api.py` - Comprehensive API tests
- `python3 final_verification.py` - Full system verification
- `./curl_examples.sh` - Ready-to-use curl commands

---

## 📚 **API Usage Examples**

### **Get Risk Level for Single Stock:**
```bash
curl http://localhost:8000/risk-level/AAPL
```

### **Batch Analysis for Multiple Stocks:**
```bash
curl -X POST http://localhost:8000/risk-level \
  -H "Content-Type: application/json" \
  -d '{"symbols":["AAPL","TSLA","MSFT"]}'
```

### **Custom Risk Factors:**
```bash
curl -X POST http://localhost:8000/risk-level \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["HIGH_RISK_TEST"],
    "risk_factors": {
      "volatility": 0.9,
      "market_cap": "small",
      "sector_risk": 0.8,
      "liquidity": 0.1
    }
  }'
```

---

## 🔧 **File Structure (All Ready)**

```
VTHacks26/
├── simple_backend.py          ← Main backend server (START THIS)
├── docker-compose.yml         ← Aerospike container config
├── requirements.txt           ← All dependencies listed
├── test_risk_api.py          ← Comprehensive tests
├── final_verification.py     ← System verification
├── curl_examples.sh          ← Ready curl commands
├── backend/                  ← Full backend architecture (optional)
│   ├── config/
│   ├── models/
│   ├── repositories/
│   └── services/
└── [other supporting files]
```

---

## 🎯 **Expected Results After Setup**

Running `python3 test_risk_api.py` should show:
```
🎯 TESTING RISK LEVEL HTTP API
==================================================

1. 📊 Testing GET /risk-level/{symbol}
   ✅ SUCCESS for AAPL
   🎯 Risk Level: medium
   📈 Risk Score: N/A
   📊 Source: stored_analysis

[... more tests ...]

🎉 Risk Level API Testing Complete!
Success Rate: 100.0%
```

---

## 🚨 **Troubleshooting (If Issues)**

### **Issue: "Connection refused"**
```bash
# Check if Aerospike is running
docker ps | grep aerospike

# If not running, start it
docker-compose up -d
```

### **Issue: "Module not found"**
```bash
# Install missing dependencies
pip3 install --break-system-packages [module_name]
```

### **Issue: "Port 8000 already in use"**
```bash
# Kill existing process
pkill -f simple_backend.py

# Then restart
python3 simple_backend.py
```

---

## 📈 **What They Can Do Immediately**

1. **Test Individual Stocks**: `curl http://localhost:8000/risk-level/AAPL`
2. **Batch Process Multiple Stocks**: Use the POST endpoint with an array of symbols
3. **View Interactive Documentation**: `http://localhost:8000/docs`
4. **Run Comprehensive Tests**: `python3 test_risk_api.py`
5. **Verify Everything Works**: `python3 final_verification.py`

---

## 🎉 **Success Indicators**

Your partner will know it's working when they see:

- ✅ Backend starts without errors
- ✅ `http://localhost:8000/health` returns `{"status":"healthy"}`
- ✅ `http://localhost:8000/test-aerospike` shows successful connection
- ✅ Risk level API returns actual risk calculations
- ✅ Data gets saved to Aerospike automatically

---

## 📞 **If They Need Help**

The setup is **extremely straightforward**, but if they run into issues:

1. **Check the logs** - `simple_backend.py` shows all errors in terminal
2. **Run the verification script** - `python3 final_verification.py`
3. **Test Aerospike directly** - `python3 test_aerospike_direct.py`

**Everything is pre-configured and ready to go!** 🚀