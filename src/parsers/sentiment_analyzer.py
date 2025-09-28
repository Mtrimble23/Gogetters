#!/usr/bin/env python3
"""
Sentiment Analyzer for Financial News
Uses VADER sentiment analysis optimized for financial text
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

@dataclass
class SentimentResult:
    """Result of sentiment analysis"""
    text: str
    compound_score: float
    positive: float
    negative: float
    neutral: float
    normalized_score: float  # -1 to 1 scale
    confidence: float
    timestamp: str

class SentimentAnalyzer:
    """Financial sentiment analyzer using VADER with financial domain adjustments"""

    def __init__(self):
        if VADER_AVAILABLE:
            self.analyzer = SentimentIntensityAnalyzer()

            # Add financial-specific lexicon
            financial_lexicon_updates = {
                'bullish': 2.0,
                'bearish': -2.0,
                'rally': 1.5,
                'crash': -2.5,
                'surge': 1.8,
                'plummet': -2.2,
                'breakout': 1.5,
                'correction': -1.2,
                'moon': 2.0,
                'dump': -2.0,
                'hodl': 1.0,
                'buy': 1.2,
                'sell': -1.2,
                'upgrade': 1.8,
                'downgrade': -1.8,
                'outperform': 1.5,
                'underperform': -1.5,
                'beat': 1.3,
                'miss': -1.3,
                'exceed': 1.4,
                'disappoint': -1.4,
                'revenue': 0.2,
                'earnings': 0.2,
                'profit': 1.0,
                'loss': -1.0,
                'growth': 1.0,
                'decline': -1.0,
                'strong': 1.2,
                'weak': -1.2,
                'robust': 1.3,
                'solid': 1.1,
                'disappointing': -1.5,
                'promising': 1.4,
                'innovative': 1.2,
                'disruptive': 1.1,
                'partnership': 0.8,
                'acquisition': 0.5,
                'merger': 0.3,
                'dividend': 0.8,
                'split': 0.5,
                'volatility': -0.5,
                'stable': 0.8,
                'momentum': 0.7,
                'breakthrough': 1.6,
                'milestone': 1.2,
                'record': 1.1,
                'all-time': 1.0,
                'expansion': 1.0,
                'competition': -0.3,
                'regulation': -0.8,
                'lawsuit': -1.5,
                'investigation': -1.2,
                'fine': -1.3,
                'penalty': -1.2,
                'approval': 1.2,
                'launch': 1.0,
                'debut': 0.8,
                'optimistic': 1.3,
                'pessimistic': -1.3,
                'confident': 1.2,
                'concerned': -1.0,
                'uncertain': -0.7,
                'risky': -1.1,
                'safe': 0.9,
                'secure': 1.0,
                'vulnerable': -1.2,
                'opportunity': 1.1,
                'threat': -1.3,
                'challenge': -0.8,
                'advantage': 1.2,
                'leadership': 1.1,
                'market-leading': 1.4,
                'competitive': 0.5,
                'dominant': 1.3,
                'struggling': -1.4,
                'recovering': 0.8,
                'turnaround': 1.2,
                'restructuring': -0.3,
                'cutting': -0.5,
                'layoffs': -1.5,
                'hiring': 0.8,
                'investing': 1.0,
                'expansion': 1.1,
                'ai': 1.2,
                'artificial intelligence': 1.2,
                'machine learning': 1.0,
                'automation': 0.8,
                'digital transformation': 1.1,
                'cloud': 1.0,
                'sustainability': 1.0,
                'green': 1.0,
                'renewable': 1.1,
                'electric': 1.0,
                'clean energy': 1.2
            }

            # Update the analyzer's lexicon
            self.analyzer.lexicon.update(financial_lexicon_updates)
        else:
            self.analyzer = None
            print("Warning: VADER sentiment not available. Install with: pip install vaderSentiment")

    def clean_text(self, text: str) -> str:
        """Clean and preprocess text for better sentiment analysis"""
        if not text:
            return ""

        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # Remove stock symbols that might confuse sentiment
        text = re.sub(r'\$[A-Z]{1,5}', '', text)

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of a single text"""
        if not self.analyzer:
            return self._fallback_analysis(text)

        cleaned_text = self.clean_text(text)

        if not cleaned_text:
            return self._neutral_result(text)

        # Get VADER scores
        scores = self.analyzer.polarity_scores(cleaned_text)

        # Calculate confidence based on how far from neutral
        confidence = abs(scores['compound'])

        # Normalize compound score to -1 to 1 (it should already be, but ensure it)
        normalized_score = max(-1.0, min(1.0, scores['compound']))

        return SentimentResult(
            text=text,
            compound_score=scores['compound'],
            positive=scores['pos'],
            negative=scores['neg'],
            neutral=scores['neu'],
            normalized_score=normalized_score,
            confidence=confidence,
            timestamp=datetime.now().isoformat()
        )

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze(text) for text in texts]

    def get_aggregate_sentiment(self, texts: List[str]) -> Dict[str, Any]:
        """Get aggregate sentiment statistics for a list of texts"""
        if not texts:
            return self._neutral_aggregate()

        results = self.analyze_batch(texts)

        # Calculate aggregate statistics
        compound_scores = [r.compound_score for r in results]
        normalized_scores = [r.normalized_score for r in results]
        confidences = [r.confidence for r in results]

        # Calculate weighted average (weight by confidence)
        if confidences and sum(confidences) > 0:
            weighted_sentiment = sum(score * conf for score, conf in zip(normalized_scores, confidences)) / sum(confidences)
        else:
            weighted_sentiment = sum(normalized_scores) / len(normalized_scores) if normalized_scores else 0.0

        # Sentiment classification
        if weighted_sentiment > 0.05:
            sentiment_label = "positive"
        elif weighted_sentiment < -0.05:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        return {
            'aggregate_sentiment': weighted_sentiment,
            'sentiment_label': sentiment_label,
            'average_confidence': sum(confidences) / len(confidences) if confidences else 0.0,
            'total_analyzed': len(texts),
            'individual_scores': normalized_scores,
            'raw_compound_scores': compound_scores,
            'timestamp': datetime.now().isoformat()
        }

    def _fallback_analysis(self, text: str) -> SentimentResult:
        """Fallback analysis when VADER is not available"""
        # Simple keyword-based sentiment
        positive_words = ['good', 'great', 'excellent', 'positive', 'up', 'rise', 'gain', 'profit', 'growth', 'strong', 'buy', 'bullish']
        negative_words = ['bad', 'terrible', 'negative', 'down', 'fall', 'loss', 'decline', 'weak', 'sell', 'bearish', 'crash']

        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            normalized_score = 0.3
        elif neg_count > pos_count:
            normalized_score = -0.3
        else:
            normalized_score = 0.0

        return SentimentResult(
            text=text,
            compound_score=normalized_score,
            positive=0.3 if pos_count > 0 else 0.0,
            negative=0.3 if neg_count > 0 else 0.0,
            neutral=0.7,
            normalized_score=normalized_score,
            confidence=0.5,
            timestamp=datetime.now().isoformat()
        )

    def _neutral_result(self, text: str) -> SentimentResult:
        """Return neutral sentiment result"""
        return SentimentResult(
            text=text,
            compound_score=0.0,
            positive=0.0,
            negative=0.0,
            neutral=1.0,
            normalized_score=0.0,
            confidence=0.0,
            timestamp=datetime.now().isoformat()
        )

    def _neutral_aggregate(self) -> Dict[str, Any]:
        """Return neutral aggregate result"""
        return {
            'aggregate_sentiment': 0.0,
            'sentiment_label': 'neutral',
            'average_confidence': 0.0,
            'total_analyzed': 0,
            'individual_scores': [],
            'raw_compound_scores': [],
            'timestamp': datetime.now().isoformat()
        }

def test_sentiment_analyzer():
    """Test the sentiment analyzer"""
    analyzer = SentimentAnalyzer()

    test_texts = [
        "Apple reports record earnings and strong iPhone sales",
        "Tesla stock crashes after disappointing delivery numbers",
        "NVIDIA announces breakthrough in AI chip technology",
        "Meta faces regulatory challenges and user growth concerns",
        "Google shows solid revenue growth in cloud services"
    ]

    print("Testing Sentiment Analyzer")
    print("=" * 50)

    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"Text: {text}")
        print(f"Sentiment: {result.normalized_score:.3f} (confidence: {result.confidence:.3f})")
        print("-" * 50)

    # Test aggregate
    aggregate = analyzer.get_aggregate_sentiment(test_texts)
    print(f"Aggregate sentiment: {aggregate['aggregate_sentiment']:.3f} ({aggregate['sentiment_label']})")

if __name__ == "__main__":
    test_sentiment_analyzer()