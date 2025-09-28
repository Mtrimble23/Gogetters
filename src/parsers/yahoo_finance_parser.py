#!/usr/bin/env python3
"""
Yahoo Finance Data Parser
Extracts financial metrics for stock analysis
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple


class YahooFinanceParser:
    """Handles all Yahoo Finance data extraction"""
    
    def __init__(self):
        self.supported_tickers = ['AAPL', 'AMZN', 'GOOGL', 'NVDA', 'META', 'TSLA']
    
    def get_extended_historical_data(self, symbol: str, period: str = "2y") -> Tuple[np.ndarray, np.ndarray]:
        """
        Get extended historical price data for risk calculations
        
        Args:
            symbol: Stock symbol
            period: Period for historical data ("1y", "2y", "5y", "max")
            
        Returns:
            Tuple of (prices, dates) as numpy arrays
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return np.array([]), np.array([])
            
            prices = hist['Close'].values
            dates = hist.index.values
            
            return prices, dates
            
        except Exception as e:
            print(f"Error fetching extended historical data for {symbol}: {e}")
            return np.array([]), np.array([])
    
    def get_market_data(self, symbol: str = "SPY", period: str = "2y") -> Tuple[np.ndarray, np.ndarray]:
        """
        Get market index data for beta calculations
        
        Args:
            symbol: Market index symbol (default: SPY)
            period: Period for historical data
            
        Returns:
            Tuple of (prices, dates) as numpy arrays
        """
        return self.get_extended_historical_data(symbol, period)
    
    def get_returns_data(self, symbol: str, period: str = "2y") -> np.ndarray:
        """
        Get returns data directly
        
        Args:
            symbol: Stock symbol
            period: Period for historical data
            
        Returns:
            Array of log returns
        """
        prices, _ = self.get_extended_historical_data(symbol, period)
        if len(prices) < 2:
            return np.array([])
        
        # Calculate log returns
        returns = np.diff(np.log(prices))
        return returns
    
    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1y")
            
            # Get current price and change
            current_price = info.get('currentPrice', 0)
            previous_close = info.get('previousClose', 0)
            price_change = ((current_price - previous_close) / previous_close * 100) if previous_close > 0 else 0
            
            # Extract key metrics
            stock_data = {
                'symbol': symbol,
                'current_price': current_price,
                'price_change_percent': round(price_change, 2),
                'dividend_yield': info.get('dividendYield', 0) if info.get('dividendYield') else 0,
                'beta': info.get('beta', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'market_cap': info.get('marketCap', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Add 52-week range calculation
            if stock_data['fifty_two_week_high'] > 0 and stock_data['fifty_two_week_low'] > 0:
                range_position = ((current_price - stock_data['fifty_two_week_low']) / 
                                (stock_data['fifty_two_week_high'] - stock_data['fifty_two_week_low']) * 100)
                stock_data['fifty_two_week_range_position'] = round(range_position, 2)
            
            # Add historical price data for graph
            if not hist.empty:
                stock_data['price_history'] = {
                    'dates': hist.index[-30:].strftime('%Y-%m-%d').tolist(),
                    'prices': hist['Close'][-30:].round(2).tolist()
                }
            
            return stock_data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return self._get_fallback_data(symbol)
    
    def get_batch_stock_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get stock data for multiple symbols"""
        results = {}
        for symbol in symbols:
            if symbol in self.supported_tickers:
                results[symbol] = self.get_stock_data(symbol)
            else:
                print(f"Warning: {symbol} not in supported tickers")
                results[symbol] = self._get_fallback_data(symbol)
        return results
    
    def _get_fallback_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback data when Yahoo Finance fails"""
        return {
            'symbol': symbol,
            'current_price': 0,
            'price_change_percent': 0,
            'dividend_yield': 0,
            'beta': 0,
            'pe_ratio': 0,
            'debt_to_equity': 0,
            'market_cap': 0,
            'volume': 0,
            'avg_volume': 0,
            'fifty_two_week_high': 0,
            'fifty_two_week_low': 0,
            'fifty_two_week_range_position': 0,
            'cboe_volatility': 0,
            'price_history': {'dates': [], 'prices': []},
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': 'Data unavailable'
        }


def test_parser():
    """Test the Yahoo Finance parser"""
    parser = YahooFinanceParser()
    
    print("🧪 Testing Yahoo Finance Parser")
    print("=" * 40)
    
    # Test single stock
    print("Testing AAPL...")
    data = parser.get_stock_data('AAPL')
    print(f"Current Price: ${data['current_price']}")
    print(f"Price Change: {data['price_change_percent']}%")
    print(f"P/E Ratio: {data['pe_ratio']}")
    print(f"Beta: {data['beta']}")
    print(f"52-week range: ${data['fifty_two_week_low']} - ${data['fifty_two_week_high']}")
    
    # Test batch
    print("\nTesting batch fetch...")
    batch_data = parser.get_batch_stock_data(['AAPL', 'MSFT', 'GOOGL'])
    for symbol, stock_data in batch_data.items():
        print(f"{symbol}: ${stock_data['current_price']} ({stock_data['price_change_percent']}%)")


if __name__ == "__main__":
    test_parser()