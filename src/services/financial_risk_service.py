#!/usr/bin/env python3
"""
Financial Risk Analysis Service
Business logic for risk assessment using real financial data
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from parsers.yahoo_finance_parser import YahooFinanceParser
from parsers.cboe_volatility_calculator import CBOEVolatilityCalculator


class FinancialRiskService:
    """Service for comprehensive financial risk analysis"""
    
    def __init__(self):
        self.yahoo_parser = YahooFinanceParser()
        self.cboe_calculator = CBOEVolatilityCalculator()
        self.supported_symbols = ['AAPL', 'AMZN', 'GOOGL', 'NVDA', 'META', 'TSLA']
    
    def analyze_single_stock(self, symbol: str, custom_factors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive analysis of a single stock"""
        symbol = symbol.upper()
        
        if symbol not in self.supported_symbols:
            return {
                'success': False,
                'symbol': symbol,
                'error': f'Symbol not supported. Supported symbols: {self.supported_symbols}'
            }
        
        try:
            # Get Yahoo Finance data
            stock_data = self.yahoo_parser.get_stock_data(symbol)
            
            # Get CBOE volatility
            cboe_volatility, vol_metadata = self.cboe_calculator.calculate_vx_ticker_30d(symbol)
            stock_data['cboe_volatility'] = round(cboe_volatility, 2)
            stock_data['volatility_method'] = vol_metadata.get('method', 'historical')
            
            # Calculate risk assessment
            risk_analysis = self._calculate_risk_level(stock_data, custom_factors)
            
            return {
                'success': True,
                'symbol': symbol,
                'financial_data': stock_data,
                'risk_analysis': risk_analysis,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'symbol': symbol,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def analyze_batch_stocks(self, symbols: List[str], custom_factors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze multiple stocks in batch"""
        results = []
        successful = 0
        failed = 0
        
        start_time = datetime.now()
        
        for symbol in symbols:
            result = self.analyze_single_stock(symbol, custom_factors)
            if result['success']:
                successful += 1
            else:
                failed += 1
            results.append(result)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            'success': True,
            'results': results,
            'summary': {
                'total_symbols': len(symbols),
                'successful': successful,
                'failed': failed,
                'processing_time_seconds': round(processing_time, 3),
                'average_time_per_symbol': round(processing_time / len(symbols), 3) if symbols else 0
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _calculate_risk_level(self, stock_data: Dict[str, Any], custom_factors: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate risk level based on financial metrics"""
        
        # Extract key metrics
        beta = stock_data.get('beta', 1.0)
        pe_ratio = stock_data.get('pe_ratio', 20.0)
        debt_to_equity = stock_data.get('debt_to_equity', 0.0)
        cboe_volatility = stock_data.get('cboe_volatility', 25.0)
        price_change = abs(stock_data.get('price_change_percent', 0.0))
        market_cap = stock_data.get('market_cap', 0)
        range_position = stock_data.get('fifty_two_week_range_position', 50.0)
        
        # Risk factors calculation
        risk_factors = {}
        
        # Beta risk (market sensitivity)
        if beta < 0.5:
            risk_factors['beta_risk'] = 'low'
            beta_score = 0.2
        elif beta < 1.2:
            risk_factors['beta_risk'] = 'medium'
            beta_score = 0.5
        else:
            risk_factors['beta_risk'] = 'high'
            beta_score = 0.8
        
        # Volatility risk
        if cboe_volatility < 20:
            risk_factors['volatility_risk'] = 'low'
            vol_score = 0.2
        elif cboe_volatility < 35:
            risk_factors['volatility_risk'] = 'medium'
            vol_score = 0.5
        else:
            risk_factors['volatility_risk'] = 'high'
            vol_score = 0.9
        
        # P/E ratio risk
        if pe_ratio == 0 or pe_ratio > 50:
            risk_factors['pe_risk'] = 'high'
            pe_score = 0.8
        elif pe_ratio < 15:
            risk_factors['pe_risk'] = 'low'
            pe_score = 0.3
        else:
            risk_factors['pe_risk'] = 'medium'
            pe_score = 0.5
        
        # Debt risk
        if debt_to_equity > 100:
            risk_factors['debt_risk'] = 'high'
            debt_score = 0.8
        elif debt_to_equity > 50:
            risk_factors['debt_risk'] = 'medium'
            debt_score = 0.5
        else:
            risk_factors['debt_risk'] = 'low'
            debt_score = 0.2
        
        # Market cap risk
        if market_cap > 1000000000000:  # $1T+
            risk_factors['size_risk'] = 'low'
            size_score = 0.1
        elif market_cap > 100000000000:  # $100B+
            risk_factors['size_risk'] = 'medium'
            size_score = 0.3
        else:
            risk_factors['size_risk'] = 'high'
            size_score = 0.7
        
        # Recent price movement risk
        if price_change > 5:
            risk_factors['momentum_risk'] = 'high'
            momentum_score = 0.8
        elif price_change > 2:
            risk_factors['momentum_risk'] = 'medium'
            momentum_score = 0.5
        else:
            risk_factors['momentum_risk'] = 'low'
            momentum_score = 0.2
        
        # Apply custom factors if provided
        if custom_factors:
            if 'beta_override' in custom_factors:
                beta_score = float(custom_factors['beta_override'])
            if 'volatility_override' in custom_factors:
                vol_score = float(custom_factors['volatility_override'])
        
        # Calculate overall risk score
        risk_score = (
            beta_score * 0.25 +
            vol_score * 0.30 +
            pe_score * 0.15 +
            debt_score * 0.15 +
            size_score * 0.10 +
            momentum_score * 0.05
        )
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = 'low'
            recommendation = 'BUY'
        elif risk_score < 0.6:
            risk_level = 'medium'
            recommendation = 'HOLD'
        else:
            risk_level = 'high'
            recommendation = 'SELL'
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 3),
            'recommendation': recommendation,
            'risk_factors': risk_factors,
            'metrics_used': {
                'beta': beta,
                'cboe_volatility': cboe_volatility,
                'pe_ratio': pe_ratio,
                'debt_to_equity': debt_to_equity,
                'market_cap': market_cap,
                'price_change_percent': price_change,
                'range_position': range_position
            },
            'custom_factors_applied': custom_factors is not None
        }
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported stock symbols"""
        return self.supported_symbols.copy()
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics and capabilities"""
        return {
            'service_name': 'VTHacks26 Financial Risk Analysis',
            'supported_symbols': self.supported_symbols,
            'total_supported_symbols': len(self.supported_symbols),
            'data_sources': [
                'Yahoo Finance (stock data)',
                'CBOE (volatility calculation)',
                'Historical data (fallback)'
            ],
            'metrics_analyzed': [
                'Current Price',
                'Price Change %',
                'Dividend Yield %',
                'Beta',
                'P/E Ratio',
                'Debt-to-Equity',
                '52-week High/Low',
                'CBOE Volatility Index',
                'Market Capitalization',
                'Price History (30 days)'
            ],
            'risk_levels': ['low', 'medium', 'high'],
            'recommendations': ['BUY', 'HOLD', 'SELL'],
            'version': '2.0.0',
            'last_updated': datetime.now(timezone.utc).isoformat()
        }


def test_financial_service():
    """Test the financial risk service"""
    service = FinancialRiskService()
    
    print("🧪 Testing Financial Risk Service")
    print("=" * 50)
    
    # Test single stock analysis
    print("Testing AAPL analysis...")
    result = service.analyze_single_stock('AAPL')
    if result['success']:
        financial_data = result['financial_data']
        risk_analysis = result['risk_analysis']
        
        print(f"Current Price: ${financial_data['current_price']}")
        print(f"Price Change: {financial_data['price_change_percent']}%")
        print(f"CBOE Volatility: {financial_data['cboe_volatility']}%")
        print(f"Beta: {financial_data['beta']}")
        print(f"P/E Ratio: {financial_data['pe_ratio']}")
        print(f"Risk Level: {risk_analysis['risk_level']}")
        print(f"Risk Score: {risk_analysis['risk_score']}")
        print(f"Recommendation: {risk_analysis['recommendation']}")
    else:
        print(f"Error: {result['error']}")
    
    # Test batch analysis
    print("\nTesting batch analysis...")
    batch_result = service.analyze_batch_stocks(['AAPL', 'MSFT'])
    if batch_result['success']:
        summary = batch_result['summary']
        print(f"Processed {summary['successful']}/{summary['total_symbols']} successfully")
        print(f"Processing time: {summary['processing_time_seconds']}s")
        
        for result in batch_result['results']:
            if result['success']:
                symbol = result['symbol']
                risk = result['risk_analysis']['risk_level']
                print(f"{symbol}: {risk} risk")


if __name__ == "__main__":
    test_financial_service()