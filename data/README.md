# Sample Market Data CSV Format

The VGP Algorithmic Trader can read market data from CSV files with the following format:

## CSV Structure
```
Date,Open,High,Low,Close,Volume
2024-01-01,100.00,102.50,99.50,101.25,1500000
2024-01-02,101.25,103.00,100.75,102.50,1650000
2024-01-03,102.50,104.25,102.00,103.75,1800000
...
```

## Field Descriptions
- **Date**: Trading date (format: YYYY-MM-DD)
- **Open**: Opening price for the period
- **High**: Highest price during the period  
- **Low**: Lowest price during the period
- **Close**: Closing price for the period
- **Volume**: Number of shares/contracts traded

## Notes
- The first row must contain headers
- Prices should be in decimal format
- Volume should be a positive integer
- Data should be sorted chronologically (oldest first)
- Missing or invalid rows will be skipped

## Example Usage
To use your own data file, modify the `config.txt` file:
```
data_file=your_market_data.csv
```

If no data file is specified, the system will generate synthetic market data for demonstration purposes.