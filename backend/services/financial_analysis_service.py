"""
Financial analysis service
Integrates risk analysis and sentiment analysis
"""

import asyncio
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add parent directory to path to import the original analyzers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from financial_risk_analyzer import FinancialRiskAnalyzer
from sentiment_analyzer import SentimentAnalyzer
from ..models import AnalysisResult, FinancialData, RiskMetrics, SentimentData, RiskLevel
from ..repositories import BaseRepository


class FinancialAnalysisService:
    """
    Service for comprehensive financial analysis
    Coordinates risk analysis and sentiment analysis
    """
    
    def __init__(self, repository: BaseRepository[AnalysisResult]):
        """Initialize the service with repository and analyzers"""
        self.repository = repository
        self.risk_analyzer = FinancialRiskAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        
    async def analyze_stock(self, 
                          symbol: str, 
                          include_sentiment: bool = True,
                          sentiment_sources: List[str] = None) -> AnalysisResult:
        """
        Perform comprehensive stock analysis
        
        Args:
            symbol: Stock symbol to analyze
            include_sentiment: Whether to include sentiment analysis
            sentiment_sources: List of news sources for sentiment analysis
            
        Returns:
            AnalysisResult containing all analysis data
        """
        print(f"Starting analysis for {symbol}")
        
        # Get financial risk analysis
        risk_data = self.risk_analyzer.analyze_stock(symbol)
        
        # Convert to our models
        risk_metrics = self._convert_risk_metrics(risk_data)
        financial_data = self._create_financial_data(symbol, risk_data, risk_metrics)
        
        # Create initial analysis result
        analysis_result = AnalysisResult(
            symbol=symbol,
            financial_data=financial_data,
            analysis_timestamp=datetime.now()
        )
        
        # Add sentiment analysis if requested
        if include_sentiment:
            await self._add_sentiment_analysis(analysis_result, sentiment_sources)
        
        # Generate recommendations
        self._generate_recommendations(analysis_result)
        
        # Save to repository
        analysis_id = await self.repository.save(analysis_result)
        analysis_result.analysis_id = analysis_id
        
        print(f"Analysis completed for {symbol}, saved as {analysis_id}")
        return analysis_result
    
    async def get_analysis(self, symbol: str) -> Optional[AnalysisResult]:
        """Get latest analysis for a symbol"""
        return await self.repository.get_by_symbol(symbol)
    
    async def get_analysis_history(self, symbol: str, limit: int = 10) -> List[AnalysisResult]:
        """Get analysis history for a symbol"""
        return await self.repository.get_latest_by_symbol(symbol, limit)
    
    async def search_analyses(self, filters: Dict[str, Any]) -> List[AnalysisResult]:
        """Search analyses with filters"""
        return await self.repository.search(filters)
    
    async def analyze_portfolio(self, symbols: List[str]) -> Dict[str, AnalysisResult]:
        """Analyze multiple stocks"""
        results = {}
        
        # Analyze stocks concurrently
        tasks = [self.analyze_stock(symbol) for symbol in symbols]
        analyses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for symbol, analysis in zip(symbols, analyses):
            if isinstance(analysis, Exception):
                print(f"Error analyzing {symbol}: {analysis}")
                results[symbol] = None
            else:
                results[symbol] = analysis
        
        return results
    
    def _convert_risk_metrics(self, risk_data: Dict[str, Any]) -> RiskMetrics:
        """Convert risk analyzer output to our risk metrics model"""
        # Map risk level string to enum
        risk_level_str = risk_data.get('overall_risk_level', '').lower()
        risk_level = None
        if risk_level_str in ['low', 'medium', 'high']:
            risk_level = RiskLevel(risk_level_str)
        
        return RiskMetrics(
            debt_to_equity=risk_data.get('debt_to_equity'),
            beta=risk_data.get('beta'),
            roe=risk_data.get('roe'),
            current_ratio=risk_data.get('current_ratio'),
            overall_risk_score=risk_data.get('overall_risk_score'),
            risk_level=risk_level
        )
    
    def _create_financial_data(self, symbol: str, risk_data: Dict[str, Any], risk_metrics: RiskMetrics) -> FinancialData:
        """Create financial data model from risk analyzer output"""
        return FinancialData(
            symbol=symbol,
            company_name=risk_data.get('company_name'),
            market_cap=risk_data.get('market_cap'),
            price=risk_data.get('current_price'),
            volume=risk_data.get('volume'),
            pe_ratio=risk_data.get('pe_ratio'),
            pb_ratio=risk_data.get('pb_ratio'),
            dividend_yield=risk_data.get('dividend_yield'),
            risk_metrics=risk_metrics,
            timestamp=datetime.now()
        )
    
    async def _add_sentiment_analysis(self, analysis_result: AnalysisResult, sources: List[str] = None):
        """Add sentiment analysis to the result"""
        symbol = analysis_result.symbol
        
        # Get sample news texts (in a real implementation, you'd fetch from news APIs)
        sample_texts = [
            f"{symbol} shows strong quarterly earnings growth",
            f"Market analysts upgrade {symbol} outlook",
            f"Concerns about {symbol} market position amid competition"
        ]
        
        if sources:
            # In a real implementation, fetch news from specified sources
            pass
        
        # Analyze sentiment
        sentiment_results = self.sentiment_analyzer.analyze_batch(sample_texts)
        
        # Convert to our sentiment data models
        sentiment_data_list = []
        for text, sentiment_result in zip(sample_texts, sentiment_results):
            sentiment_data = SentimentData(
                text=text,
                label=sentiment_result.label,
                score=sentiment_result.score,
                normalized_score=sentiment_result.normalized_score,
                timestamp=datetime.now(),
                source="sample_news"
            )
            sentiment_data_list.append(sentiment_data)
        
        # Add to financial data
        analysis_result.financial_data.sentiment_data = sentiment_data_list
        
        # Calculate overall sentiment score
        if sentiment_data_list:
            analysis_result.overall_sentiment_score = sum(
                s.normalized_score for s in sentiment_data_list
            ) / len(sentiment_data_list)
    
    def _generate_recommendations(self, analysis_result: AnalysisResult):
        """Generate investment recommendations based on analysis"""
        risk_metrics = analysis_result.financial_data.risk_metrics
        sentiment_score = analysis_result.overall_sentiment_score
        
        if not risk_metrics:
            analysis_result.recommendation = "Insufficient data for recommendation"
            analysis_result.confidence_level = 0.0
            return
        
        # Risk assessment
        risk_level = risk_metrics.risk_level
        risk_score = risk_metrics.overall_risk_score or 0.5
        
        # Sentiment assessment
        sentiment_weight = 0.3  # 30% weight to sentiment
        risk_weight = 0.7       # 70% weight to risk metrics
        
        # Combined score (0-1, higher is better)
        combined_score = (
            risk_weight * (1 - risk_score) +  # Invert risk score (lower risk is better)
            sentiment_weight * ((sentiment_score or 0) + 1) / 2  # Convert sentiment to 0-1 scale
        )
        
        # Generate recommendation
        if combined_score >= 0.7:
            recommendation = "BUY"
            confidence = min(0.9, combined_score)
        elif combined_score >= 0.5:
            recommendation = "HOLD"
            confidence = combined_score * 0.8
        else:
            recommendation = "SELL"
            confidence = (1 - combined_score) * 0.9
        
        analysis_result.recommendation = recommendation
        analysis_result.confidence_level = confidence
        
        # Generate summaries
        analysis_result.risk_summary = self._generate_risk_summary(risk_metrics)
        analysis_result.sentiment_summary = self._generate_sentiment_summary(analysis_result.financial_data.sentiment_data)
    
    def _generate_risk_summary(self, risk_metrics: RiskMetrics) -> str:
        """Generate human-readable risk summary"""
        if not risk_metrics or not risk_metrics.risk_level:
            return "Risk assessment incomplete"
        
        risk_level = risk_metrics.risk_level.value.upper()
        
        summaries = {
            'LOW': "Low risk investment with stable financial metrics",
            'MEDIUM': "Moderate risk investment requiring careful monitoring",
            'HIGH': "High risk investment suitable only for risk-tolerant investors"
        }
        
        return summaries.get(risk_level, f"{risk_level} risk investment")
    
    def _generate_sentiment_summary(self, sentiment_data: List[SentimentData]) -> str:
        """Generate human-readable sentiment summary"""
        if not sentiment_data:
            return "No sentiment data available"
        
        positive_count = sum(1 for s in sentiment_data if s.normalized_score > 0.1)
        negative_count = sum(1 for s in sentiment_data if s.normalized_score < -0.1)
        neutral_count = len(sentiment_data) - positive_count - negative_count
        
        if positive_count > negative_count:
            return f"Mostly positive sentiment ({positive_count} positive, {negative_count} negative)"
        elif negative_count > positive_count:
            return f"Mostly negative sentiment ({negative_count} negative, {positive_count} positive)"
        else:
            return f"Mixed sentiment ({positive_count} positive, {negative_count} negative, {neutral_count} neutral)"