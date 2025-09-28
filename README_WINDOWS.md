# VTHacks26 Financial Risk API - Windows Compatible Setup

## Quick Start for Partners

**Option 1: Automatic Setup (Recommended)**
```bash
./partner_quick_setup_windows.sh
```

**Option 2: Manual Setup**
See `FINAL_PARTNER_GUIDE_WINDOWS.md` for step-by-step instructions.

## What You Get

- **Real-time financial data** for 6 stocks (AAPL, AMZN, GOOGL, NVDA, META, TSLA)
- **CBOE volatility calculations** (VIX-style implied volatility)
- **Sub-millisecond API responses** via Aerospike caching
- **Production-ready architecture** with comprehensive risk analysis
- **Interactive API docs** at http://localhost:8000/docs

## Example API Usage

```bash
# Get Apple stock risk analysis
curl http://localhost:8000/risk-level/AAPL

# API Documentation  
start http://localhost:8000/docs
```

## Documentation

- **FINAL_PARTNER_GUIDE_WINDOWS.md** - Complete setup guide (Windows compatible)
- **PARTNER_COMMANDS.md** - Detailed command reference
- **API Docs:** http://localhost:8000/docs (after setup)

## Success Indicators

Setup is complete when:
- Backend shows "Uvicorn running on http://0.0.0.0:8000"
- Health check: `curl http://localhost:8000/health` returns `"database_connected": true`
- All 6 stocks cached: `curl http://localhost:8000/stats` shows 6 cached symbols

**Ready to build!**