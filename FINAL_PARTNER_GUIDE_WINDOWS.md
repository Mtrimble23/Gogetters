# VTHacks26 Financial Risk API - Complete Setup Guide (Windows Compatible)

## What You're Getting

A production-ready **Financial Risk Analysis API** with:
- Real Yahoo Finance data (AAPL, AMZN, GOOGL, NVDA, META, TSLA)
- CBOE volatility calculations (VIX-style implied volatility)
- Aerospike database caching (sub-millisecond response times)
- Comprehensive risk analysis (6-factor risk scoring)
- Production architecture (parsers -> services -> repositories -> API)
- Corrected dividend yields (forward annual dividend rates)
- Interactive API docs at http://localhost:8000/docs

---

## Prerequisites
- Git installed
- Docker installed  
- Python 3.7+ installed
- Terminal/Command Prompt access

---

## Step-by-Step Setup

### Step 1: Get the Code
```bash
# Clone the repository
git clone https://github.com/Mtrimble23/VTHacks26.git
cd VTHacks26
```

### Step 2: Install Dependencies
```bash
# Install Python packages
pip3 install --break-system-packages -r requirements.txt

# Alternative if permission issues:
pip3 install --user -r requirements.txt
```

### Step 3: Start Database
```bash
# Start Aerospike database
docker-compose up -d

# Verify it's running
docker ps
```
**Expected Output:**
```
CONTAINER ID   IMAGE                               STATUS              PORTS
915ef29fba8f   aerospike/aerospike-server:latest   Up (healthy)        0.0.0.0:3000-3003->3000-3003/tcp
```

### Step 4: Start Backend Server

**Recommended Method:**
```bash
# Start backend in background
nohup python3 financial_api_backend.py > backend.log 2>&1 &

# Verify it started
sleep 3
ps aux | grep financial_api_backend
```

**Expected Startup Output:**
```
VTHacks26 Financial Risk Analysis API
====================================================
Real-time Yahoo Finance integration
CBOE volatility calculation  
Aerospike database caching
Comprehensive risk analysis

Supported symbols: AAPL, AMZN, GOOGL, NVDA, META, TSLA
Database: Connected

API Documentation: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Load All Stock Data (CRITICAL)

**Single Command - Complete Setup:**
```bash
# Load all stocks + verify format consistency
./load_all_stocks.sh
```

**Expected Output:**
```
Loading all stocks to database...
SUCCESS: 6/6 - All stocks cached!

Verifying format consistency...
ALL STOCKS HAVE IDENTICAL FORMAT!
Common structure has 51 fields
All 6 stocks verified

Final database status: 6 cached symbols
All stocks loaded and verified!
```

### Step 6: Verify Everything Works

**Health Check:**
```bash
curl -s http://localhost:8000/health
```
**Expected:**
```json
{
  "status": "healthy",
  "service": "VTHacks26 Financial Risk Analysis API",
  "database_connected": true,
  "supported_symbols": 6
}
```

**Test Main API Endpoint:**
```bash
curl -s "http://localhost:8000/risk-level/AAPL"
```
**Key Response Fields:**
```json
{
  "success": true,
  "symbol": "AAPL",
  "financial_data": {
    "current_price": 255.46,
    "dividend_yield": 0.41,
    "beta": 1.109,
    "pe_ratio": 38.76,
    "cboe_volatility": 28.73,
    "price_history": { "30 days of data" }
  },
  "risk_analysis": {
    "risk_level": "medium",
    "risk_score": 0.49,
    "recommendation": "HOLD"
  },
  "source": "cache",
  "response_time": "< 0.001s"
}
```

**Verify Cache Status:**
```bash
curl -s "http://localhost:8000/stats"
```
**Expected:**
```json
{
  "database": {
    "cached_symbols": ["AAPL", "AMZN", "GOOGL", "NVDA", "META", "TSLA"],
    "cache_count": 6
  }
}
```

### Step 7: Run Tests (Optional)
```bash
# Comprehensive test suite
python3 test_backend_clean.py

# Data completeness verification
python3 complete_data_verification.py
```

### Step 8: Explore API Documentation
```bash
# Open interactive API docs
start http://localhost:8000/docs

# Or visit manually in browser: http://localhost:8000/docs
```

---

## Success Checklist

Your setup is complete when ALL of these are true:

- [ ] **Docker**: `docker ps` shows aerospike container (healthy)
- [ ] **Backend**: Process running, shows "Uvicorn running on http://0.0.0.0:8000"
- [ ] **Database**: Health check returns `"database_connected": true`
- [ ] **Data Loaded**: Load script shows "SUCCESS: 6/6 - All stocks cached!"
- [ ] **Cache Working**: API calls return `"source": "cache"` with `"response_time": "< 0.001s"`
- [ ] **Data Quality**: AAPL dividend yield is ~0.41% (not 41%)
- [ ] **All Stocks**: Stats show all 6 symbols cached: AAPL, AMZN, GOOGL, NVDA, META, TSLA
- [ ] **API Docs**: http://localhost:8000/docs loads properly

---

## What You Can Do Now

### Available API Endpoints:
- `GET /health` - System health check
- `GET /stats` - Database and system statistics  
- `GET /risk-level/{symbol}` - **Main endpoint** - Get comprehensive risk analysis
- `GET /docs` - Interactive API documentation

### Example Usage:
```bash
# Get Apple stock analysis
curl http://localhost:8000/risk-level/AAPL

# Get NVIDIA analysis  
curl http://localhost:8000/risk-level/NVDA

# Get Tesla analysis
curl http://localhost:8000/risk-level/TSLA
```

### Key Features Available:
- **Real-time stock prices** from Yahoo Finance
- **CBOE volatility calculations** (custom VIX-style)
- **6-factor risk analysis** (beta, volatility, PE, debt, size, momentum)
- **30-day price history** with trend analysis
- **Financial metrics** (dividend yield, beta, P/E, debt-to-equity, market cap)
- **Intelligent recommendations** (BUY/HOLD/SELL)
- **Sub-millisecond caching** via Aerospike

---

## Troubleshooting

**Port 8000 Busy:**
```bash
pkill -f financial_api_backend
netstat -ano | findstr :8000
```

**Database Issues:**
```bash
docker-compose down
docker-compose up -d
```

**Cache Issues:**
```bash
# Clear cache for specific stock
curl http://localhost:8000/cache/clear/AAPL
```

**Fresh Start:**
```bash
pkill -f financial_api_backend
docker-compose down
docker-compose up -d
nohup python3 financial_api_backend.py > backend.log 2>&1 &
./load_all_stocks.sh
```

---

## Ready to Build!

Your Financial Risk Analysis API is now fully operational with:
- **6 stocks** with complete real-time data
- **Sub-millisecond** cache performance  
- **Production-ready** architecture
- **Comprehensive** financial analysis
- **Interactive** API documentation

**Start building your application using the API endpoints!**