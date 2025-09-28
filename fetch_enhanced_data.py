#!/usr/bin/env python3
"""
Enhanced Data Fetcher for Multi-Stock VGP System
Fetches comprehensive stock data for all major symbols
"""

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
import time
from typing import List, Dict

# Major stock symbols to fetch
STOCK_SYMBOLS = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft  
    'GOOGL',  # Google
    'AMZN',   # Amazon
    'TSLA',   # Tesla
    'META',   # Meta (Facebook)
    'NVDA',   # NVIDIA
    'NFLX',   # Netflix
    'AMD',    # AMD
    'INTC',   # Intel
    'ORCL',   # Oracle
    'CRM',    # Salesforce
    'ADBE',   # Adobe
    'PYPL',   # PayPal
    'SHOP',   # Shopify
    'ZM',     # Zoom
    'ROKU',   # Roku
    'SNOW',   # Snowflake
    'PLTR'    # Palantir
]

def fetch_stock_data(symbol: str, period: str = "5y") -> pd.DataFrame:
    """Fetch comprehensive stock data including financial fundamentals"""
    try:
        print(f"Fetching data for {symbol}...")
        
        # Create ticker object
        ticker = yf.Ticker(symbol)
        
        # Get price data
        price_data = ticker.history(period=period)
        if price_data.empty:
            print(f"No price data found for {symbol}")
            return None
            
        # Reset index to get date as column
        price_data.reset_index(inplace=True)
        
        # Get financial data
        try:
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            
            # Extract key financial metrics (annual data)
            financial_metrics = {}
            
            if not balance_sheet.empty:
                # Get stockholders equity
                if 'Stockholders Equity' in balance_sheet.index:
                    financial_metrics['Stockholders_Equity'] = balance_sheet.loc['Stockholders Equity']
                elif 'Total Stockholder Equity' in balance_sheet.index:
                    financial_metrics['Stockholders_Equity'] = balance_sheet.loc['Total Stockholder Equity']
                    
                # Get cash and equivalents
                if 'Cash And Cash Equivalents' in balance_sheet.index:
                    financial_metrics['Cash_And_Equivalents'] = balance_sheet.loc['Cash And Cash Equivalents']
                elif 'Cash Cash Equivalents And Short Term Investments' in balance_sheet.index:
                    financial_metrics['Cash_And_Equivalents'] = balance_sheet.loc['Cash Cash Equivalents And Short Term Investments']
                    
                # Get total assets
                if 'Total Assets' in balance_sheet.index:
                    financial_metrics['Total_Assets'] = balance_sheet.loc['Total Assets']
                    
                # Get working capital (Current Assets - Current Liabilities)
                current_assets = None
                current_liabilities = None
                if 'Current Assets' in balance_sheet.index:
                    current_assets = balance_sheet.loc['Current Assets']
                if 'Current Liabilities' in balance_sheet.index:
                    current_liabilities = balance_sheet.loc['Current Liabilities']
                if current_assets is not None and current_liabilities is not None:
                    financial_metrics['Working_Capital'] = current_assets - current_liabilities
                    
                # Get total debt
                if 'Total Debt' in balance_sheet.index:
                    financial_metrics['Total_Debt'] = balance_sheet.loc['Total Debt']
                elif 'Long Term Debt' in balance_sheet.index and 'Current Debt' in balance_sheet.index:
                    financial_metrics['Total_Debt'] = balance_sheet.loc['Long Term Debt'] + balance_sheet.loc['Current Debt']
                    
        except Exception as e:
            print(f"  Warning: Could not fetch financials for {symbol}: {e}")
            financial_metrics = {}
        
        # Create final dataframe starting with price data
        df = price_data.copy()
        
        # Standardize date column
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        # Add financial metrics by mapping annual data to daily data
        for metric_name, metric_series in financial_metrics.items():
            if not metric_series.empty:
                # Forward fill annual data to daily frequency
                annual_dates = pd.to_datetime(metric_series.index)
                daily_values = []
                
                for date in pd.to_datetime(df['Date']):
                    # Find the most recent annual data point
                    valid_dates = annual_dates[annual_dates <= date]
                    if len(valid_dates) > 0:
                        latest_date = valid_dates.max()
                        daily_values.append(metric_series[latest_date])
                    else:
                        daily_values.append(None)
                
                df[metric_name] = daily_values
                
                # Calculate growth rates (year over year)
                if len(metric_series) > 1:
                    growth_values = []
                    for date in pd.to_datetime(df['Date']):
                        valid_dates = annual_dates[annual_dates <= date]
                        if len(valid_dates) >= 2:
                            latest_date = valid_dates.max()
                            prev_date = valid_dates[valid_dates < latest_date].max()
                            current_val = metric_series[latest_date]
                            prev_val = metric_series[prev_date]
                            if prev_val != 0 and not pd.isna(prev_val) and not pd.isna(current_val):
                                growth = ((current_val - prev_val) / abs(prev_val)) * 100
                                growth_values.append(growth)
                            else:
                                growth_values.append(0)
                        else:
                            growth_values.append(0)
                    
                    df[f"{metric_name}_Growth"] = growth_values
        
        # Ensure we have all required columns with defaults if missing
        required_financial_cols = [
            'Stockholders_Equity', 'Stockholders_Equity_Growth',
            'Cash_And_Equivalents', 'Cash_And_Equivalents_Growth', 
            'Total_Assets', 'Total_Assets_Growth',
            'Working_Capital', 'Working_Capital_Growth',
            'Total_Debt', 'Total_Debt_Growth'
        ]
        
        for col in required_financial_cols:
            if col not in df.columns:
                df[col] = 0  # Default to 0 if data not available
        
        print(f"Successfully fetched {len(df)} records for {symbol}")
        print(f"Date range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
        print(f"Columns: {df.columns.tolist()}")
        
        return df
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def save_stock_data(df: pd.DataFrame, symbol: str, data_dir: str = "data"):
    """Save stock data to CSV file"""
    try:
        data_path = Path(data_dir)
        data_path.mkdir(exist_ok=True)
        
        filename = f"{symbol}_enhanced_data.csv"
        filepath = data_path / filename
        
        df.to_csv(filepath, index=False)
        print(f"Saved {symbol} data to {filepath}")
        
    except Exception as e:
        print(f"Error saving {symbol}: {e}")

def fetch_all_stocks():
    """Fetch data for all stocks"""
    print("Starting enhanced data fetch for multi-stock VGP system")
    print(f"Fetching data for {len(STOCK_SYMBOLS)} symbols...")
    print("=" * 60)
    
    successful_downloads = []
    failed_downloads = []
    
    for i, symbol in enumerate(STOCK_SYMBOLS, 1):
        print(f"\n[{i}/{len(STOCK_SYMBOLS)}] Processing {symbol}")
        
        df = fetch_stock_data(symbol)
        
        if df is not None and not df.empty:
            save_stock_data(df, symbol)
            successful_downloads.append(symbol)
        else:
            failed_downloads.append(symbol)
            
        # Rate limiting
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("DATA FETCH SUMMARY")
    print("=" * 60)
    print(f"Successfully downloaded: {len(successful_downloads)} stocks")
    print(f"Successful: {', '.join(successful_downloads)}")
    
    if failed_downloads:
        print(f"\nFailed downloads: {len(failed_downloads)} stocks")  
        print(f"Failed: {', '.join(failed_downloads)}")
    
    print(f"\nTotal files created: {len(successful_downloads)}")
    print("Data is ready for Python VGP training!")

def create_sample_data():
    """Create sample data if yfinance is not available"""
    print("Creating sample data for testing...")
    
    # Create sample data for AAPL
    dates = pd.date_range(start='2020-01-01', end='2025-01-01', freq='D')
    dates = dates[dates.dayofweek < 5]  # Weekdays only
    
    np.random.seed(42)
    n_days = len(dates)
    
    # Generate realistic price movements
    price_base = 100.0
    returns = np.random.normal(0.001, 0.02, n_days)  # Daily returns
    prices = [price_base]
    
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    
    prices = prices[1:]  # Remove initial price
    
    # Create OHLCV data
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': np.random.randint(50000000, 200000000, n_days)
    })
    
    # Ensure high >= close >= low and open is reasonable
    df['high'] = np.maximum(df['high'], df[['open', 'close']].max(axis=1))
    df['low'] = np.minimum(df['low'], df[['open', 'close']].min(axis=1))
    
    save_stock_data(df, 'AAPL_SAMPLE')
    print(f"Created sample data with {len(df)} records")

def check_data_availability():
    """Check what data files we currently have"""
    data_path = Path("data")
    
    if not data_path.exists():
        print("Data directory does not exist")
        return
        
    csv_files = list(data_path.glob("*.csv"))
    
    print(f"Found {len(csv_files)} CSV files in data directory:")
    
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path, nrows=1)  # Read just first row
            print(f"  {file_path.name}: {len(pd.read_csv(file_path))} records, columns: {df.columns.tolist()}")
        except Exception as e:
            print(f"  {file_path.name}: Error reading - {e}")

if __name__ == "__main__":
    print("Enhanced Stock Data Fetcher")
    print("=" * 40)
    
    # Check current data
    print("\nCurrent data status:")
    check_data_availability()
    
    # Ask user what to do
    print("\nOptions:")
    print("1. Fetch real data from Yahoo Finance (requires yfinance)")
    print("2. Create sample data for testing")
    print("3. Check current data only")
    
    try:
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == "1":
            try:
                import yfinance as yf
                fetch_all_stocks()
            except ImportError:
                print("yfinance not installed. Install with: pip install yfinance")
                print("Creating sample data instead...")
                create_sample_data()
                
        elif choice == "2":
            create_sample_data()
            
        elif choice == "3":
            print("Data check completed.")
            
        else:
            print("Invalid choice. Creating sample data...")
            create_sample_data()
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        print("Creating sample data as fallback...")
        create_sample_data()