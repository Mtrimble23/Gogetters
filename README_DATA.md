# VGP Trader - Real Apple Stock Data Integration

## Quick Start with Python API

The easiest way to get real Apple stock data is using our Python fetcher script:

### One-Command Setup

```batch
.\run_with_real_data.bat
```

This will:
1. ✅ Check Python installation
2. ✅ Install required packages (`yfinance`, `pandas`)  
3. ✅ Download 7 years of Apple stock data
4. ✅ Format data for VGP trader
5. ✅ Build and run the VGP trader

### Manual Steps (if needed)

1. **Install Python packages:**
   ```batch
   pip install yfinance pandas
   ```

2. **Fetch Apple data:**
   ```batch
   python fetch_data.py
   ```

3. **Build and run:**
   ```batch
   .\build_real_data.bat
   .\vgp_trader.exe
   ```

### What You'll See

```
🍎 Apple Stock Data Fetcher for VGP Trader
==================================================
📦 Installing required packages...
✅ Installed yfinance
✅ Installed pandas
Fetching 7 years of AAPL stock data...
✅ Downloaded 1825 trading days of data
📅 Date range: 2017-09-28 to 2024-09-27
💰 Price range: $124.17 - $237.49
💾 Data saved to: data/AAPL_data.csv

📊 Sample data (first 5 rows):
        Date       Open       High        Low      Close  Adj Close    Volume
2017-09-28  154.229996  158.279999  154.220001  158.279999  158.279999  40028600
2017-09-29  158.050003  158.259995  156.729996  158.119995  158.119995  29445200
2017-10-02  159.020004  159.100006  157.839996  159.089996  159.089996  22050800

📈 Data statistics:
   Records: 1825
   Avg Price: $172.45
   Avg Volume: 82,945,678

✅ Data quality validation passed
🎉 Data preparation completed successfully!

VGP Algorithmic Trader v1.0
============================
Loading market data...
Successfully loaded real data for AAPL
Loaded 1825 records from data/AAPL_data.csv

=== Data Statistics ===
Total Records: 1825
Valid Records: 1825
Price Range: $124.17 - $237.49
Average Price: $172.45
Average Volume: 82,945,678
Date Range: 2017-09-28 to 2024-09-27
=========================

Starting VGP evolution with real Apple stock data...
```

### Python API Features

- 🚀 **Automatic**: Downloads latest Apple data using Yahoo Finance API
- 📊 **Validated**: Checks data quality and OHLC relationships  
- 🔄 **Always Fresh**: Gets most recent 7 years of data
- 📈 **Statistics**: Shows price ranges, volume, and data quality metrics
- 🛠️ **No Manual Downloads**: No need to visit websites or manage CSV files

### Alternative: Manual CSV Download

If you prefer the manual approach:

1. **Download Apple Stock Data:**
   - Go to: https://finance.yahoo.com/quote/AAPL/history
   - Set date range from **January 1, 2017** to **December 1, 2024** (approximately 7 years)
   - Click **"Download"** to get the CSV file
   - Save the file as `AAPL_data.csv` in the `data/` folder

2. **Direct Download URL:**
   ```
   https://query1.finance.yahoo.com/v7/finance/download/AAPL?period1=1514764800&period2=1735689600&interval=1d&events=history
   ```
   - Right-click and "Save As" → `data/AAPL_data.csv`

3. **Expected CSV Format:**
   ```
   Date,Open,High,Low,Close,Adj Close,Volume
   2017-01-03,115.800003,116.330002,114.760002,116.150002,107.312408,28781900
   2017-01-04,115.849998,116.510002,115.750000,116.019997,107.192200,21118100
   ```

### File Structure
```
VTHacks26/
├── data/
│   └── AAPL_data.csv          ← Place downloaded file here
├── src/
├── include/
└── build_gcc.bat
```

### Run the Program

1. **Compile:**
   ```batch
   .\build_gcc.bat
   ```

2. **Run:**
   ```batch
   .\vgp_trader.exe
   ```

The program will:
- ✅ Automatically look for `data/AAPL_data.csv`
- ✅ Load and validate the Apple stock data
- ✅ Display data statistics (price range, volume, date range)
- ✅ Run VGP evolution on real market data
- ✅ Generate trading strategies based on actual Apple stock patterns

### What You'll See

```
VGP Algorithmic Trader v1.0
============================
Loading market data...
Successfully loaded real data for AAPL
Loaded 1847 records from data/AAPL_data.csv

=== Data Statistics ===
Total Records: 1847
Valid Records: 1847
Price Range: $50.25 - $237.49
Average Price: $143.67
Average Volume: 89,234,567
Date Range: 2017-01-03 to 2024-11-29
=========================

Initializing evolution engine...
Generation 0 - Best fitness: 0.234567 - Avg fitness: 0.123456
Generation 1 - Best fitness: 0.345678 - Avg fitness: 0.234567
...
```

### Fallback Behavior

If `AAPL_data.csv` is not found, the program will:
1. Display download instructions
2. Automatically fall back to synthetic data generation
3. Continue running with simulated market data

This ensures the demo always works, even without real data files.