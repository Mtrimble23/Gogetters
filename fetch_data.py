#!/usr/bin/env python3
"""
Stock Data Fetcher for VGP Trader
Downloads stock data for any symbol and formats it for C++ VGP algorithmic trader
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
import sys
import argparse

def fetch_stock_data(symbol="AAPL", years=7):
    """
    Fetch stock data using yfinance API
    """
    print(f"Fetching {years} years of {symbol} stock data...")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    
    try:
        # Download data using yfinance
        ticker = yf.Ticker(symbol)
        data = ticker.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval='1d'
        )
        
        if data.empty:
            print(f"❌ No data found for {symbol}")
            print(f"💡 Make sure '{symbol}' is a valid stock symbol")
            return None
            
        print(f"✅ Downloaded {len(data)} trading days of data")
        print(f"📅 Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"💰 Price range: ${data['Low'].min():.2f} - ${data['High'].max():.2f}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def format_for_vgp(data, output_file):
    """
    Format data for VGP trader CSV format
    Expected format: Date,Open,High,Low,Close,Adj Close,Volume
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Prepare data with proper column names
        formatted_data = pd.DataFrame({
            'Date': data.index.strftime('%Y-%m-%d'),
            'Open': data['Open'].round(6),
            'High': data['High'].round(6),
            'Low': data['Low'].round(6),
            'Close': data['Close'].round(6),
            'Adj Close': data['Close'].round(6),  # Use Close as Adj Close for simplicity
            'Volume': data['Volume'].astype(int)
        })
        
        # Save to CSV
        formatted_data.to_csv(output_file, index=False)
        print(f"💾 Data saved to: {output_file}")
        
        # Display sample data
        print("\n📊 Sample data (first 5 rows):")
        print(formatted_data.head().to_string(index=False))
        
        print(f"\n📈 Data statistics:")
        print(f"   Records: {len(formatted_data)}")
        print(f"   Avg Price: ${formatted_data['Close'].mean():.2f}")
        print(f"   Avg Volume: {formatted_data['Volume'].mean():,.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error formatting data: {e}")
        return False

def install_dependencies():
    """
    Install required Python packages
    """
    try:
        import yfinance
        import pandas
        return True
    except ImportError:
        print("📦 Installing required packages...")
        import subprocess
        import sys
        
        packages = ['yfinance', 'pandas']
        for package in packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
        return True

def validate_data_quality(data):
    """
    Validate the quality of downloaded data
    """
    issues = []
    
    # Check for missing data
    missing_days = data.isnull().sum().sum()
    if missing_days > 0:
        issues.append(f"Missing data: {missing_days} values")
    
    # Check for unrealistic prices
    if (data['High'] < data[['Open', 'Low', 'Close']].max(axis=1)).any():
        issues.append("Invalid OHLC relationships detected")
    
    if (data['Low'] > data[['Open', 'High', 'Close']].min(axis=1)).any():
        issues.append("Invalid OHLC relationships detected")
    
    # Check for zero/negative prices
    price_cols = ['Open', 'High', 'Low', 'Close']
    if (data[price_cols] <= 0).any().any():
        issues.append("Zero or negative prices detected")
    
    # Check for zero volume (could be valid for some days)
    zero_volume_days = (data['Volume'] == 0).sum()
    if zero_volume_days > len(data) * 0.05:  # More than 5% zero volume days
        issues.append(f"High number of zero volume days: {zero_volume_days}")
    
    # Check data sufficiency for VGP
    if len(data) < 252 * 2:  # Less than 2 years of trading days
        issues.append(f"Limited data: {len(data)} days (recommend 2+ years)")
    
    if issues:
        print("\n⚠️  Data quality issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ Data quality validation passed")
    
    return len(issues) == 0

def main():
    """
    Main function to fetch and prepare stock data
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Stock Data Fetcher for VGP Trader')
    parser.add_argument('symbol', nargs='?', default='AAPL', 
                       help='Stock symbol to fetch (default: AAPL)')
    parser.add_argument('--years', type=int, default=7,
                       help='Number of years of data to fetch (default: 7)')
    parser.add_argument('--output-dir', default='data',
                       help='Output directory (default: data)')
    
    args = parser.parse_args()
    
    # Convert symbol to uppercase
    symbol = args.symbol.upper()
    
    print(f"📈 Stock Data Fetcher for VGP Trader")
    print("=" * 50)
    print(f"📊 Symbol: {symbol}")
    print(f"📅 Years: {args.years}")
    print(f"📁 Output: {args.output_dir}/{symbol}_data.csv")
    print("")
    
    # Configuration
    output_file = f"{args.output_dir}/{symbol}_data.csv"
    
    # Check/install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Exiting.")
        return False
    
    # Re-import after installation
    global yf, pd
    import yfinance as yf
    import pandas as pd
    
    # Fetch data
    data = fetch_stock_data(symbol, args.years)
    if data is None:
        return False
    
    # Validate data quality
    validate_data_quality(data)
    
    # Format and save data
    success = format_for_vgp(data, output_file)
    if not success:
        return False
    
    print(f"\n🎉 Data preparation completed successfully!")
    print(f"📁 Data saved as: {output_file}")
    print(f"🚀 Ready to run: .\\build\\VGP_AlgoTrader.exe config.txt {symbol}")
    print(f"📊 The VGP trader will now use real {symbol} stock data")
    
    return True

if __name__ == "__main__":
    try:
        # Add usage examples if no arguments provided
        if len(sys.argv) == 1:
            print("📈 Stock Data Fetcher for VGP Trader")
            print("=" * 40)
            print("\nUsage Examples:")
            print("  python fetch_data.py TSLA              # Fetch Tesla data")
            print("  python fetch_data.py MSFT              # Fetch Microsoft data") 
            print("  python fetch_data.py GOOGL --years 5   # Fetch Google data (5 years)")
            print("  python fetch_data.py --help            # Show all options")
            print("\nPress Enter to fetch AAPL data, or Ctrl+C to exit...")
            input()
        
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)