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
from services.advanced_risk_calculator import AdvancedRiskCalculator

# Try to import ML model
# ML model will be loaded lazily to avoid circular imports
ML_MODEL_AVAILABLE = False


class FinancialRiskService:
    """Service for comprehensive financial risk analysis"""
    
    def __init__(self):
        self.yahoo_parser = YahooFinanceParser()
        self.cboe_calculator = CBOEVolatilityCalculator()
        self.risk_calculator = AdvancedRiskCalculator()
        self.supported_symbols = ['AAPL', 'AMZN', 'GOOGL', 'NVDA', 'META', 'TSLA']
        
        # ML model will be loaded lazily when needed
        self.ml_predictor = None
        self._ml_model_attempted = False
    
    def _get_ml_predictor(self):
        """Lazily load ML predictor to avoid circular imports"""
        if not self._ml_model_attempted:
            self._ml_model_attempted = True
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from models.simple_risk_predictor import SimpleRiskPredictor
                
                self.ml_predictor = SimpleRiskPredictor()
                model_path = os.path.join('models', 'simple_risk_model.pkl')
                if os.path.exists(model_path):
                    try:
                        self.ml_predictor.load_model(model_path)
                        print("✅ ML risk prediction model loaded successfully")
                        return self.ml_predictor
                    except Exception as e:
                        print(f"⚠️ Failed to load ML model: {e}")
                        self.ml_predictor = None
                else:
                    print("⚠️ ML model file not found")
                    self.ml_predictor = None
            except ImportError as e:
                print(f"⚠️ Could not import ML predictor: {e}")
                self.ml_predictor = None
        
        return self.ml_predictor
    
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
    
    def predict_stock_risk_ml(self, symbol: str) -> Dict[str, Any]:
        """
        Use machine learning model with ALL advanced risk equations
        Returns: Enhanced risk prediction using all our sophisticated metrics
        """
        ml_predictor = self._get_ml_predictor()
        if not ml_predictor or not hasattr(ml_predictor, 'is_trained') or not ml_predictor.is_trained:
            return {
                'success': False,
                'error': 'ML risk prediction model not available or not trained',
                'fallback_suggestion': 'Use analyze_advanced_risk() for traditional analysis'
            }
        
        try:
            result = ml_predictor.predict_risk(symbol, self)
            
            # Add explanation of which advanced metrics were used
            if result['success']:
                result['advanced_metrics_used'] = [
                    'Annualized Volatility (σ)',
                    'Skewness (Asymmetry Risk)', 
                    'Excess Kurtosis (Tail Risk)',
                    'Value at Risk (95% & 99%)',
                    'Conditional VaR (Expected Shortfall)',
                    'Maximum Drawdown',
                    'Sortino Ratio',
                    'Calmar Ratio',
                    'Omega Ratio',
                    'Beta (Systematic Risk)',
                    'Extreme Value Theory Metrics',
                    'P/E Ratio & Debt-to-Equity',
                    'CBOE Volatility & Market Cap'
                ]
                result['model_type'] = 'Logistic Regression with Advanced Risk Features'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'ML prediction failed: {str(e)}'
            }
    
    def get_comprehensive_risk_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get BOTH traditional analysis AND ML prediction using all advanced equations
        This is the full power analysis!
        """
        symbol = symbol.upper()
        
        # Get traditional advanced risk analysis (uses all equations)
        advanced_analysis = self.analyze_advanced_risk(symbol)
        
        # Get ML prediction (also uses all equations as features)
        ml_prediction = None
        ml_predictor = self._get_ml_predictor()
        if ml_predictor and hasattr(ml_predictor, 'is_trained') and ml_predictor.is_trained:
            ml_prediction = self.predict_stock_risk_ml(symbol)
        
        # Get basic analysis for comparison
        basic_analysis = self.analyze_single_stock(symbol)
        
        return {
            'symbol': symbol,
            'comprehensive_analysis': {
                'basic_risk_analysis': basic_analysis,
                'advanced_risk_analysis': advanced_analysis,  # Uses all equations
                'ml_risk_prediction': ml_prediction,          # Uses all equations as features
            },
            'analysis_methods': {
                'basic': 'Traditional financial ratios',
                'advanced': 'All mathematical risk equations (VaR, skewness, kurtosis, etc.)',
                'ml_prediction': 'Machine learning model trained on all advanced equations'
            },
            'equations_used': [
                'Standard Deviation of Returns (σ)',
                'Skewness = (1/N) * Σ(ri - r̄)³ / σ³',
                'Excess Kurtosis = (1/N) * Σ(ri - r̄)⁴ / σ⁴ - 3',
                'VaR = μ + zα * σ',
                'CVaR = E[R | R ≤ VaR]',
                'Max Drawdown = max((Peak - Trough) / Peak)',
                'Calmar Ratio = Annual Return / Max Drawdown',
                'Sortino Ratio = (Rp - Rf) / σd',
                'Omega Ratio = Gains above threshold / Losses below threshold',
                'Beta = Cov(Ri, Rm) / σm²',
                'Extreme Value Theory (GPD fitting)'
            ],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def analyze_advanced_risk(self, symbol: str, period: str = "2y") -> Dict[str, Any]:
        """
        Perform advanced risk analysis using sophisticated risk metrics
        
        Args:
            symbol: Stock symbol to analyze
            period: Historical data period ("1y", "2y", "5y")
            
        Returns:
            Dictionary containing comprehensive risk analysis
        """
        symbol = symbol.upper()
        
        if symbol not in self.supported_symbols:
            return {
                'success': False,
                'symbol': symbol,
                'error': f'Symbol not supported. Supported symbols: {self.supported_symbols}'
            }
        
        try:
            # Get historical price data
            prices, dates = self.yahoo_parser.get_extended_historical_data(symbol, period)
            
            if len(prices) < 30:
                return {
                    'success': False,
                    'symbol': symbol,
                    'error': 'Insufficient historical data for advanced risk analysis'
                }
            
            # Get market data for beta calculation
            market_prices, _ = self.yahoo_parser.get_market_data("SPY", period)
            
            # Calculate ALL advanced risk metrics using our equations
            risk_metrics = self.risk_calculator.calculate_all_risk_metrics(
                prices=prices,
                market_prices=market_prices if len(market_prices) == len(prices) else None
            )
            
            # Get basic stock information
            basic_stock_data = self.yahoo_parser.get_stock_data(symbol)
            
            # Combine results
            result = {
                'success': True,
                'symbol': symbol,
                'period': period,
                'data_points': len(prices),
                'basic_metrics': {
                    'current_price': basic_stock_data.get('current_price', 0),
                    'price_change_percent': basic_stock_data.get('price_change_percent', 0),
                    'market_cap': basic_stock_data.get('market_cap', 0),
                    'pe_ratio': basic_stock_data.get('pe_ratio', 0),
                    'debt_to_equity': basic_stock_data.get('debt_to_equity', 0)
                },
                'advanced_risk_metrics': risk_metrics,  # ALL OUR EQUATIONS!
                'risk_interpretation': self._interpret_advanced_risk_metrics(risk_metrics),
                'equations_calculated': [
                    'Annualized Volatility (Standard Deviation)',
                    'Skewness (Asymmetry Risk)',
                    'Kurtosis (Tail Risk)', 
                    'Value at Risk (95% & 99%)',
                    'Conditional VaR (Expected Shortfall)',
                    'Maximum Drawdown',
                    'Calmar Ratio',
                    'Sortino Ratio',
                    'Omega Ratio',
                    'Beta (Systematic Risk)',
                    'Extreme Value Theory Metrics'
                ],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'symbol': symbol,
                'error': f'Advanced risk analysis failed: {str(e)}'
            }
    
    def _interpret_advanced_risk_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret advanced risk metrics and provide risk assessments
        
        Args:
            metrics: Dictionary of calculated risk metrics
            
        Returns:
            Dictionary with risk interpretations and recommendations
        """
        interpretation = {}
        
        # Volatility interpretation
        vol = metrics.get('annualized_volatility', 0)
        if vol < 0.15:
            interpretation['volatility_assessment'] = 'Low volatility - relatively stable'
        elif vol < 0.30:
            interpretation['volatility_assessment'] = 'Moderate volatility - normal market risk'
        else:
            interpretation['volatility_assessment'] = 'High volatility - significant price swings expected'
        
        # Skewness interpretation
        skew = metrics.get('skewness', 0)
        if skew < -0.5:
            interpretation['skewness_assessment'] = 'Negative skew - higher downside risk'
        elif skew > 0.5:
            interpretation['skewness_assessment'] = 'Positive skew - higher upside potential'
        else:
            interpretation['skewness_assessment'] = 'Symmetric distribution - balanced risk'
        
        # Kurtosis interpretation
        excess_kurtosis = metrics.get('excess_kurtosis', 0)
        if excess_kurtosis > 3:
            interpretation['tail_risk_assessment'] = 'High tail risk - prone to extreme moves'
        elif excess_kurtosis > 1:
            interpretation['tail_risk_assessment'] = 'Moderate tail risk - occasional large moves'
        else:
            interpretation['tail_risk_assessment'] = 'Low tail risk - rare extreme events'
        
        # VaR interpretation (99% confidence)
        var_99 = metrics.get('var', {}).get('99%', {}).get('historical', 0)
        if abs(var_99) > 0.05:
            interpretation['var_assessment'] = f'High risk - potential daily loss of {abs(var_99)*100:.1f}%'
        elif abs(var_99) > 0.02:
            interpretation['var_assessment'] = f'Moderate risk - potential daily loss of {abs(var_99)*100:.1f}%'
        else:
            interpretation['var_assessment'] = f'Low risk - potential daily loss of {abs(var_99)*100:.1f}%'
        
        # Drawdown interpretation
        max_dd = metrics.get('max_drawdown', 0)
        if max_dd > 0.3:
            interpretation['drawdown_assessment'] = 'High drawdown risk - large peak-to-trough declines'
        elif max_dd > 0.15:
            interpretation['drawdown_assessment'] = 'Moderate drawdown risk - manageable declines'
        else:
            interpretation['drawdown_assessment'] = 'Low drawdown risk - limited peak-to-trough losses'
        
        # Beta interpretation (if available)
        beta = metrics.get('beta', 0)
        if beta != 0:
            if beta > 1.5:
                interpretation['market_risk_assessment'] = 'High market sensitivity - amplified market moves'
            elif beta > 0.5:
                interpretation['market_risk_assessment'] = 'Moderate market sensitivity - follows market trends'
            else:
                interpretation['market_risk_assessment'] = 'Low market sensitivity - less affected by market moves'
        
        # Overall risk score calculation
        risk_components = []
        if vol > 0:
            risk_components.append(min(vol / 0.5, 1.0))  # Cap at 1.0
        if abs(var_99) > 0:
            risk_components.append(min(abs(var_99) / 0.1, 1.0))
        if max_dd > 0:
            risk_components.append(min(max_dd / 0.5, 1.0))
        
        if risk_components:
            overall_risk_score = sum(risk_components) / len(risk_components)
            if overall_risk_score > 0.7:
                interpretation['overall_risk'] = 'High Risk'
            elif overall_risk_score > 0.4:
                interpretation['overall_risk'] = 'Moderate Risk'
            else:
                interpretation['overall_risk'] = 'Low Risk'
        else:
            interpretation['overall_risk'] = 'Unable to assess'
        
        return interpretation
    
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