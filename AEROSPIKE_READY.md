# 🚀 Aerospike-Powered Financial Risk Analyzer Backend

Your comprehensive backend is now **fully integrated** with Aerospike running on port 3000! This setup uses your specified namespace `VTHacks` and set `finance` with double indexing for optimal performance.

## ⚡ Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Verify Aerospike Connection**
```bash
python test_aerospike_direct.py
```

### 3. **Start the Backend**
```bash
python run_backend.py
```

### 4. **Run Integration Tests**
```bash
python test_aerospike_integration.py
```

## 🗄️ Aerospike Configuration

Your backend is configured for:
- **Host**: `127.0.0.1:3000` 
- **Namespace**: `VTHacks`
- **Set**: `finance`
- **Double Indexing**: Each bin is indexed for efficient queries

### Indexes Created Automatically:
- `symbol_idx` - String index on symbol field
- `timestamp_idx` - Numeric index on timestamp field  
- `risk_level_idx` - String index on risk_level field
- `sentiment_score_idx` - Numeric index on sentiment_score field

## 📊 API Endpoints

### Financial Analysis
```bash
# Analyze single stock (saves to Aerospike)
curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "include_sentiment": true}'

# Batch analysis (saves multiple to Aerospike)
curl -X POST "http://localhost:8000/api/v1/analysis/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL"], "include_sentiment": true}'

# Get latest analysis (retrieves from Aerospike)
curl "http://localhost:8000/api/v1/analysis/result/AAPL"

# Get analysis history (queries Aerospike with indexes)
curl "http://localhost:8000/api/v1/analysis/history/AAPL?limit=10"

# Search analyses (uses Aerospike secondary indexes)
curl -X POST "http://localhost:8000/api/v1/analysis/search" \
  -H "Content-Type: application/json" \
  -d '{"risk_level": "medium"}'
```

### Data Management
```bash
# Check repository status
curl "http://localhost:8000/api/v1/data/status"

# Switch to Aerospike (if not already active)
curl -X POST "http://localhost:8000/api/v1/data/switch/primary"

# Get all analyzed symbols
curl "http://localhost:8000/api/v1/analysis/symbols"
```

### Health Checks
```bash
# Basic health check
curl "http://localhost:8000/api/v1/health"

# Detailed health with Aerospike status
curl "http://localhost:8000/api/v1/health/detailed"
```

## 🧪 Testing Scripts

### 1. **Direct Aerospike Test**
```bash
python test_aerospike_direct.py
```
- Tests direct connection to Aerospike
- Creates and validates indexes
- Tests read/write operations
- Verifies namespace and set configuration

### 2. **Backend Integration Test**
```bash
python test_aerospike_integration.py
```
- Comprehensive 25+ test suite
- Tests all API endpoints
- Validates Aerospike integration
- Performance benchmarking
- Real-world scenario testing

### 3. **Quick Backend Test**
```bash
python test_backend.py
```
- Simple functionality test
- Good for quick verification

## 📁 Data Storage Structure

Each analysis result is stored in Aerospike with the following bins:

```json
{
  "symbol": "AAPL",
  "analysis_data": "{...complete analysis JSON...}",
  "timestamp": 1695832800,
  "risk_level": "medium", 
  "sentiment_score": 0.45,
  "recommendation": "BUY",
  "confidence_level": 0.82,
  "debt_to_equity": 1.73,
  "beta": 1.29,
  "roe": 26.31,
  "current_ratio": 1.01,
  "overall_risk_score": 0.55,
  "company_name": "Apple Inc.",
  "market_cap": 2800000000000,
  "price": 175.43,
  "created_at": 1695832800
}
```

## 🔄 Repository Architecture

### **Automatic Failover**
- **Primary**: Aerospike (preferred, high-performance)
- **Fallback**: In-memory (backup, always available)
- **Auto-switch**: Detects Aerospike availability and switches automatically

### **Repository Operations**
```python
# The service automatically uses Aerospike when available
from backend.services import FinancialAnalysisService, DataIntegrationService

# Initialize (tries Aerospike first, falls back if needed)
data_service = DataIntegrationService()
await data_service.initialize()  # ✅ Will connect to your Aerospike

analysis_service = FinancialAnalysisService(data_service.get_active_repository())

# All operations automatically use Aerospike
result = await analysis_service.analyze_stock("AAPL")  # ✅ Saved to Aerospike
```

## 🛠️ Management Commands

Use the included management script:

```bash
./manage.sh setup          # Complete setup and testing
./manage.sh start          # Start backend server  
./manage.sh test-aerospike # Test direct Aerospike connection
./manage.sh test-full      # Run comprehensive test suite
./manage.sh check-aerospike # Verify Aerospike is running
```

## 📈 Performance Features

### **Optimized for Aerospike**
- **Secondary Indexes**: Fast queries on symbol, timestamp, risk_level, sentiment_score
- **Batch Operations**: Efficient multi-stock analysis
- **Connection Pooling**: Persistent Aerospike connections
- **Async Operations**: Full async/await support

### **Query Performance**
- Symbol lookup: **O(log n)** with secondary index
- Time-range queries: **O(log n)** with timestamp index
- Risk-level filtering: **O(log n)** with risk_level index
- Full-text search: **O(n)** scan with client-side filtering

## 🚦 Status Monitoring

### **Check Backend Status**
```bash
# Health check shows Aerospike status
curl "http://localhost:8000/api/v1/health/detailed" | jq
```

### **Repository Status**
```bash
# Detailed repository information
curl "http://localhost:8000/api/v1/data/status" | jq
```

### **Live Monitoring**
- Backend logs show all Aerospike operations
- Connection status is displayed on startup
- Failed operations automatically fall back

## 🔧 Configuration

### **Environment Variables**
```bash
export AEROSPIKE_HOSTS="127.0.0.1:3000"
export AEROSPIKE_NAMESPACE="VTHacks"  
export AEROSPIKE_SET="finance"
export AEROSPIKE_TIMEOUT="5000"
```

### **Custom Configuration**
```python
from backend.config import get_settings

settings = get_settings()
# Automatically uses your VTHacks namespace and finance set
```

## 🎯 Example Workflow

1. **Start Aerospike** (already done with `docker-compose up -d`)
2. **Install & Setup**:
   ```bash
   pip install -r requirements.txt
   python test_aerospike_direct.py  # Verify connection
   ```

3. **Start Backend**:
   ```bash
   python run_backend.py
   # ✅ Connected to Aerospike at [('127.0.0.1', 3000)]
   # 📦 Namespace: VTHacks, Set: finance
   # 🎯 Primary repository active
   ```

4. **Analyze Stocks**:
   ```bash
   # This will save to your Aerospike instance
   curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "AAPL"}'
   ```

5. **Query Results**:
   ```bash
   # This will query from your Aerospike instance using indexes
   curl "http://localhost:8000/api/v1/analysis/result/AAPL"
   ```

## 🎉 You're All Set!

Your backend is now **fully integrated** with Aerospike using:
- ✅ **Namespace**: `VTHacks`  
- ✅ **Set**: `finance`
- ✅ **Double Indexing**: All key fields indexed
- ✅ **High Performance**: Optimized queries and operations
- ✅ **Production Ready**: Proper error handling and fallbacks

**Visit the API docs**: http://localhost:8000/docs

**Need help?** Run `./manage.sh help` or check the test scripts!