# 🚀 VTHacks26 Risk Level API - Deployment Guide

## 📁 Project Overview

This is a production-ready **Financial Risk Analysis API** backend built with:
- **FastAPI** for high-performance REST API
- **Aerospike** integration for persistent data storage
- **Smart caching** and error handling
- **Comprehensive diagnostics** and monitoring

---

## 🎯 Quick Start (For Your Partner)

### 1. **Setup Environment**
```bash
# Clone/download the project files
cd VTHacks26

# Install dependencies
pip3 install --break-system-packages -r requirements.txt
```

### 2. **Start the Backend** 
```bash
# Recommended: Use the clean production version
python3 backend_server.py

# Alternative: Use enhanced startup script
python3 start_backend.py
```

### 3. **Test Everything**
```bash
# Run comprehensive test suite
python3 test_backend_clean.py

# Quick manual test
curl http://localhost:8000/health
```

---

## 📋 Available Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `backend_server.py` | **Production Backend** | Main deployment ✅ |
| `simple_backend.py` | Original working version | Backup option |
| `start_backend.py` | Enhanced startup | Troubleshooting |
| `diagnose_backend.py` | System diagnostics | Debug issues |
| `test_backend_clean.py` | Comprehensive tests | Validate deployment |

---

## 🔧 API Endpoints

### **Core Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API docs |
| GET | `/stats` | System statistics |

### **Risk Analysis**

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/risk-level/{symbol}` | Single symbol analysis | `/risk-level/AAPL` |
| POST | `/risk-level` | Batch analysis | `{"symbols": ["MSFT", "GOOGL"]}` |

### **Database**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/test-aerospike` | Test database connection |

---

## 📊 Example Usage

### **Single Stock Analysis**
```bash
curl "http://localhost:8000/risk-level/AAPL"
```
```json
{
  "success": true,
  "symbol": "AAPL",
  "risk_level": "Medium",
  "risk_score": 0.45,
  "response_time": "0.123s"
}
```

### **Batch Analysis**
```bash
curl -X POST "http://localhost:8000/risk-level" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL"]}'
```

### **Custom Risk Factors**
```bash
curl -X POST "http://localhost:8000/risk-level" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["TSLA"],
    "risk_factors": {
      "volatility": 0.9,
      "sector_risk": 0.8
    }
  }'
```

---

## 🛠 Troubleshooting

### **If Backend Won't Start**
```bash
# Run diagnostics
python3 diagnose_backend.py

# Check what's using port 8000
lsof -i :8000

# Kill conflicting processes
pkill -f "port 8000"
```

### **Common Issues & Solutions**

| Problem | Solution |
|---------|----------|
| Port 8000 in use | Change port: `uvicorn main:app --port 8001` |
| Missing dependencies | `pip3 install --break-system-packages fastapi uvicorn` |
| Permission denied | `chmod +x backend_server.py` |
| Aerospike not found | Backend works without it (graceful fallback) |

### **Enhanced Startup**
```bash
# Use this if regular startup fails
python3 start_backend.py
```

---

## 🏗 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   RiskAnalyzer   │    │   Aerospike     │
│   (Port 8000)   │───▶│   Service        │───▶│   Database      │
│                 │    │   + Caching      │    │   (Optional)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

- **FastAPI**: High-performance HTTP API server
- **RiskAnalyzer**: Smart service with caching and persistence  
- **Aerospike**: Database for persistence (graceful fallback if unavailable)

---

## 🎯 Production Features

### **Built-in Reliability**
- ✅ Comprehensive error handling
- ✅ Smart caching (30-second cache)
- ✅ Graceful database fallback
- ✅ Request/response timing
- ✅ Detailed logging

### **Performance Optimized**
- ⚡ Sub-500ms response times
- ⚡ Efficient batch processing
- ⚡ Memory-optimized caching
- ⚡ Async request handling

### **Developer Friendly**
- 📖 Interactive docs at `/docs`
- 🔍 Health monitoring at `/health`
- 📊 System stats at `/stats`
- 🧪 Comprehensive test suite

---

## 📈 Testing & Validation

### **Automated Tests**
```bash
# Run all tests
python3 test_backend_clean.py

# Expected output:
# 🧪 VTHacks26 Risk Level API - Test Suite
# ✅ Health Check - PASSED
# ✅ Single Symbol Analysis - PASSED
# ✅ Batch Analysis - PASSED
# ... (9 total tests)
# 🎉 ALL TESTS PASSED!
```

### **Manual Verification**
```bash
# 1. Check health
curl http://localhost:8000/health

# 2. View API docs
open http://localhost:8000/docs

# 3. Test risk analysis
curl http://localhost:8000/risk-level/AAPL
```

---

## 🔄 Development Workflow

1. **Start Development**: `python3 backend_server.py`
2. **View API Docs**: `http://localhost:8000/docs`
3. **Run Tests**: `python3 test_backend_clean.py`
4. **Troubleshoot**: `python3 diagnose_backend.py`
5. **Deploy**: Ready for production! 🚀

---

## 📞 Support

### **Files for Reference**
- `backend_server.py` - Main production backend
- `test_backend_clean.py` - Comprehensive test suite
- `diagnose_backend.py` - Diagnostic tools
- `README.md` - This deployment guide

### **Key URLs**
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

---

## ✅ Success Checklist

- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] Backend starts without errors (`python3 backend_server.py`)
- [ ] Health check passes (`curl http://localhost:8000/health`)
- [ ] Tests pass (`python3 test_backend_clean.py`)
- [ ] API docs accessible (`http://localhost:8000/docs`)
- [ ] Risk analysis works (`curl http://localhost:8000/risk-level/AAPL`)

**🎉 When all boxes are checked, your Risk Level API is ready for production!**