#!/usr/bin/env python3
"""
Gemini AI Summarizer for Financial News
Integrates with Google Gemini API to generate intelligent investment summaries
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# Optional imports for Gemini API
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class GeminiSummarizer:
    """Handles Gemini API integration for financial news summarization"""

    def __init__(self, api_key: Optional[str] = None):
        self.model = None
        self.available = False

        if not GEMINI_AVAILABLE:
            print("WARNING: Gemini dependencies not available")
            return

        # Load environment variables
        load_dotenv()

        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')

        if not self.api_key:
            print("WARNING: No Gemini API key found. Set GEMINI_API_KEY in .env file")
            return

        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.available = True
            print("SUCCESS: Gemini AI initialized successfully")
        except Exception as e:
            print(f"ERROR: Failed to initialize Gemini: {e}")
            self.available = False

    def generate_investment_summary(self, symbol: str, headlines: List[str], sentiment_score: float, financial_data: Optional[Dict] = None) -> str:
        """Generate an investment summary using Gemini AI"""

        if not self.available:
            return self._fallback_summary(symbol, headlines, sentiment_score)

        try:
            # Construct the prompt
            prompt = self._build_prompt(symbol, headlines, sentiment_score, financial_data)

            # Generate response
            response = self.model.generate_content(prompt)

            if response and response.text:
                return response.text.strip()
            else:
                return self._fallback_summary(symbol, headlines, sentiment_score)

        except Exception as e:
            print(f"ERROR: Gemini API call failed: {e}")
            return self._fallback_summary(symbol, headlines, sentiment_score)

    def _build_prompt(self, symbol: str, headlines: List[str], sentiment_score: float, financial_data: Optional[Dict] = None) -> str:
        """Build a comprehensive prompt for Gemini"""

        # Format headlines
        headlines_text = "\n".join([f"- {headline}" for headline in headlines[:5]])  # Top 5 headlines

        # Sentiment interpretation
        if sentiment_score > 0.2:
            sentiment_desc = "very positive"
        elif sentiment_score > 0.0:
            sentiment_desc = "positive"
        elif sentiment_score < -0.2:
            sentiment_desc = "very negative"
        elif sentiment_score < 0.0:
            sentiment_desc = "negative"
        else:
            sentiment_desc = "neutral"

        # Add financial context if available
        financial_context = ""
        if financial_data:
            financial_context = f"""
Financial Context:
- Current Price: ${financial_data.get('current_price', 'N/A')}
- P/E Ratio: {financial_data.get('pe_ratio', 'N/A')}
- Beta: {financial_data.get('beta', 'N/A')}
- 52-Week Range: ${financial_data.get('fifty_two_week_low', 'N/A')} - ${financial_data.get('fifty_two_week_high', 'N/A')}
"""

        prompt = f"""You are a professional financial analyst. Analyze the following recent news headlines for {symbol} and provide a concise investment summary.

Recent News Headlines:
{headlines_text}

Sentiment Analysis: {sentiment_desc} (score: {sentiment_score:.3f})
{financial_context}

Please provide a brief, professional investment summary (2-3 sentences) that includes:
1. Key news themes affecting the stock
2. Market sentiment interpretation
3. Brief investment outlook (bullish/bearish/neutral)

Keep it concise, factual, and suitable for everyday investors. Focus on actionable insights."""

        return prompt

    def _fallback_summary(self, symbol: str, headlines: List[str], sentiment_score: float) -> str:
        """Fallback summary when Gemini is not available"""

        if not headlines:
            return f"No recent news available for {symbol}. Consider monitoring for market developments."

        # Simple analysis based on sentiment
        if sentiment_score > 0.1:
            outlook = "positive momentum"
            recommendation = "may present buying opportunities"
        elif sentiment_score < -0.1:
            outlook = "negative sentiment"
            recommendation = "warrants caution"
        else:
            outlook = "mixed signals"
            recommendation = "suggests careful monitoring"

        # Get latest headline for context
        latest_headline = headlines[0] if headlines else "No headlines available"

        summary = f"Recent news sentiment for {symbol} shows {outlook}. "
        summary += f"Latest development: \"{latest_headline[:100]}{'...' if len(latest_headline) > 100 else ''}\" "
        summary += f"Current market sentiment {recommendation} based on {len(headlines)} recent articles."

        return summary

    def test_connection(self) -> Dict[str, Any]:
        """Test Gemini API connection"""

        if not self.available:
            return {
                "success": False,
                "error": "Gemini not available",
                "details": "API key missing or dependencies not installed"
            }

        try:
            # Simple test query
            response = self.model.generate_content("Say 'Gemini API working' if you can read this.")

            return {
                "success": True,
                "response": response.text if response else "No response",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

def test_gemini_summarizer():
    """Test the Gemini summarizer"""
    summarizer = GeminiSummarizer()

    print("Testing Gemini Summarizer")
    print("=" * 40)

    # Test connection
    connection_test = summarizer.test_connection()
    print(f"Connection test: {connection_test}")

    if connection_test['success']:
        # Test summary generation
        test_headlines = [
            "Apple reports strong iPhone sales in Q4",
            "Apple stock rises on new AI features announcement",
            "Analysts upgrade Apple price target to $250"
        ]

        summary = summarizer.generate_investment_summary(
            symbol="AAPL",
            headlines=test_headlines,
            sentiment_score=0.3
        )

        print(f"\nTest Summary:\n{summary}")

if __name__ == "__main__":
    test_gemini_summarizer()