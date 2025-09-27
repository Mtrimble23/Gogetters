# Financial Risk Analyzer Backend

A comprehensive backend service for financial risk analysis with sentiment analysis capabilities. Built with FastAPI and designed to integrate with Aerospike database.

## 🏗️ Architecture

```
backend/
├── models/           # Data models and schemas
├── repositories/     # Data access layer
├── services/         # Business logic layer
├── api/             # FastAPI routes and endpoints
└── config/          # Configuration management
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Backend
```bash
python run_backend.py
```

### 3. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Interactive API**: http://localhost:8000/docs

## 📊 Features

### Financial Analysis
- **Risk Metrics**: Debt-to-Equity, Beta, ROE, Current Ratio
- **Sentiment Analysis**: Financial news sentiment using DistilRoBERTa
- **Investment Recommendations**: AI-generated buy/sell/hold recommendations
- **Batch Processing**: Analyze multiple stocks simultaneously

### Data Management
- **Dual Repository**: Aerospike (primary) + In-memory (fallback)
- **Auto-Fallback**: Seamlessly falls back when Aerospike is unavailable
- **Data Migration**: Tools to migrate between repositories
- **Real-time Sync**: Synchronization between repositories

### API Endpoints

#### Analysis Endpoints
- `POST /api/v1/analysis/analyze` - Analyze single stock
- `POST /api/v1/analysis/analyze/batch` - Batch stock analysis
- `GET /api/v1/analysis/result/{symbol}` - Get latest analysis
- `GET /api/v1/analysis/history/{symbol}` - Get analysis history
- `POST /api/v1/analysis/search` - Search analyses with filters

#### Data Management Endpoints
- `GET /api/v1/data/status` - Repository status
- `POST /api/v1/data/migrate` - Migrate data between repositories
- `POST /api/v1/data/sync` - Synchronize repositories
- `POST /api/v1/data/switch/primary` - Switch to Aerospike
- `POST /api/v1/data/switch/fallback` - Switch to in-memory

#### Health Endpoints
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system status
- `GET /api/v1/health/readiness` - Readiness probe
- `GET /api/v1/health/liveness` - Liveness probe

## 🗄️ Database Integration

### Aerospike Setup
The backend is ready to connect to Aerospike once your VM is set up:

1. **Install Aerospike Python Client** (when ready):
   ```bash
   pip install aerospike
   ```

2. **Configure Connection**:
   ```bash
   export AEROSPIKE_HOSTS="your-vm-ip:3000"
   export AEROSPIKE_NAMESPACE="financial_data"
   ```

3. **Switch to Primary Repository**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/data/switch/primary
   ```

### Current Status
- ✅ **In-Memory Repository**: Active (fallback)
- 🔄 **Aerospike Repository**: Ready to connect
- 🛠️ **Migration Tools**: Available for data transfer

## 🧪 Testing

### Run Test Client
```bash
python test_backend.py
```

### Example API Usage
```python
import aiohttp
import asyncio

async def analyze_stock():
    async with aiohttp.ClientSession() as session:
        payload = {"symbol": "AAPL", "include_sentiment": True}
        
        async with session.post(
            "http://localhost:8000/api/v1/analysis/analyze",
            json=payload
        ) as response:
            result = await response.json()
            print(result)

asyncio.run(analyze_stock())
```

## 🔧 Configuration

### Environment Variables
```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=info

# Aerospike Settings
AEROSPIKE_HOSTS=127.0.0.1:3000
AEROSPIKE_NAMESPACE=financial_data
AEROSPIKE_SET=analysis_results
AEROSPIKE_TIMEOUT=5000

# Analysis Settings
SENTIMENT_MODEL=mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis
SENTIMENT_BATCH_SIZE=32
MAX_BATCH_SIZE=20

# CORS Settings
CORS_ORIGINS=*
```

## 📋 API Response Examples

### Stock Analysis Response
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "financial_data": {
      "risk_metrics": {
        "debt_to_equity": 1.73,
        "beta": 1.29,
        "roe": 26.31,
        "current_ratio": 1.01,
        "risk_level": "medium"
      },
      "sentiment_data": [
        {
          "text": "AAPL shows strong quarterly earnings growth",
          "label": "positive",
          "score": 0.89,
          "normalized_score": 0.78
        }
      ]
    },
    "recommendation": "BUY",
    "confidence_level": 0.82,
    "overall_sentiment_score": 0.45
  }
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "repositories": {
    "active_repository": "fallback",
    "primary_available": false,
    "repositories": {
      "primary": {
        "type": "aerospike",
        "available": false
      },
      "fallback": {
        "type": "in_memory",
        "available": true,
        "total_records": 15,
        "unique_symbols": 8
      }
    }
  }
}
```

## 🔄 Data Flow

1. **Analysis Request** → Service Layer
2. **Service Layer** → Risk Analyzer + Sentiment Analyzer
3. **Combined Analysis** → Repository Layer
4. **Repository** → Aerospike (primary) or In-Memory (fallback)
5. **Results** → API Response

## 🛟 Error Handling

- **Automatic Fallback**: Switches to in-memory when Aerospike is unavailable
- **Graceful Degradation**: Continues operation with reduced functionality
- **Detailed Error Messages**: Clear error responses for debugging
- **Retry Logic**: Automatic retries for transient failures

## 📈 Performance Features

- **Async/Await**: Full asynchronous operation
- **Batch Processing**: Efficient multi-stock analysis
- **Caching**: Sentiment analysis caching
- **Connection Pooling**: Efficient database connections

## 🔐 Production Considerations

- **CORS Configuration**: Restrict origins in production
- **Rate Limiting**: Implement rate limiting middleware
- **Authentication**: Add JWT or API key authentication
- **Monitoring**: Add metrics and logging
- **Health Checks**: Use for load balancer configuration

## 📚 Integration Guide

### With Your Existing Scripts
The backend integrates your existing `financial_risk_analyzer.py` and `sentiment_analyzer.py`:

```python
from backend.services import FinancialAnalysisService
from backend.repositories import FinancialDataRepository

# Use your existing analyzers through the service
repository = FinancialDataRepository()
service = FinancialAnalysisService(repository)

# Analyze stocks
result = await service.analyze_stock("AAPL")
```

### When Aerospike is Ready
1. Uncomment `aerospike>=11.0.0` in requirements.txt
2. Install: `pip install aerospike`
3. Configure connection with your VM details
4. Use migration tools to transfer existing data
5. Switch to primary repository

This backend is production-ready and scales with your needs!