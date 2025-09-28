"""
Financial Sentiment Analysis Module
Scalable sentiment analysis using HuggingFace DistilRoBERTa model
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Union, Optional
import logging
from datetime import datetime, timedelta
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import hashlib
import pickle
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SentimentResult:
    """Container for sentiment analysis results"""
    text: str
    label: str  # 'positive', 'negative', 'neutral'
    score: float  # confidence score
    normalized_score: float  # -1 to +1 range
    timestamp: datetime
    source: str = "unknown"

class SentimentAnalyzer:
    """
    Scalable financial sentiment analysis using DistilRoBERTa
    Features:
    - Batch processing for efficiency
    - Local caching to avoid re-computation
    - Normalized scoring (-1 to +1)
    - Error handling and logging
    """

    def __init__(self,
                 model_name: str = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
                 cache_dir: str = "./sentiment_cache",
                 batch_size: int = 32,
                 device: str = "auto"):

        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.batch_size = batch_size

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize model
        self.sentiment_pipeline = None
        self._load_model(device)

        # Cache for avoiding recomputation
        self.cache_file = self.cache_dir / "sentiment_cache.pkl"
        self.cache = self._load_cache()

    def _load_model(self, device: str):
        """Load the HuggingFace sentiment model"""
        try:
            self.logger.info(f"Loading sentiment model: {self.model_name}")

            # Determine device
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"

            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if device == "cuda" else -1,
                return_all_scores=True
            )

            self.logger.info(f"Model loaded successfully on {device}")

        except Exception as e:
            self.logger.error(f"Failed to load sentiment model: {e}")
            raise

    def _load_cache(self) -> Dict:
        """Load sentiment cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load cache: {e}")
        return {}

    def _save_cache(self):
        """Save sentiment cache to disk"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            self.logger.warning(f"Could not save cache: {e}")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode()).hexdigest()

    def _normalize_score(self, label: str, score: float) -> float:
        """Map sentiment labels to 0-1 scale for NEAT (0=negative, 0.5=neutral, 1=positive)"""
        if label.lower() in ['positive', 'pos']:
            return 0.5 + (score * 0.5)  # Map to 0.5-1.0 range
        elif label.lower() in ['negative', 'neg']:
            return 0.5 - (score * 0.5)  # Map to 0.0-0.5 range
        else:  # neutral
            return 0.5

    def analyze_single(self, text: str, source: str = "unknown") -> SentimentResult:
        """Analyze sentiment for a single text"""

        # Check cache first
        cache_key = self._get_cache_key(text)
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            return SentimentResult(
                text=text,
                label=cached_result['label'],
                score=cached_result['score'],
                normalized_score=cached_result['normalized_score'],
                timestamp=datetime.now(),
                source=source
            )

        try:
            # Run sentiment analysis
            results = self.sentiment_pipeline(text)

            # Extract best result
            best_result = max(results[0], key=lambda x: x['score'])
            label = best_result['label']
            score = best_result['score']
            normalized_score = self._normalize_score(label, score)

            # Cache result
            self.cache[cache_key] = {
                'label': label,
                'score': score,
                'normalized_score': normalized_score
            }

            return SentimentResult(
                text=text,
                label=label,
                score=score,
                normalized_score=normalized_score,
                timestamp=datetime.now(),
                source=source
            )

        except Exception as e:
            self.logger.error(f"Sentiment analysis failed for text: {text[:50]}... Error: {e}")
            # Return neutral sentiment as fallback
            return SentimentResult(
                text=text,
                label="neutral",
                score=0.5,
                normalized_score=0.0,
                timestamp=datetime.now(),
                source=source
            )

    def analyze_batch(self, texts: List[str], sources: Optional[List[str]] = None) -> List[SentimentResult]:
        """Analyze sentiment for multiple texts efficiently"""

        if sources is None:
            sources = ["unknown"] * len(texts)

        results = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_sources = sources[i:i + self.batch_size]

            # Check cache for batch
            uncached_texts = []
            uncached_indices = []
            batch_results = [None] * len(batch_texts)

            for j, text in enumerate(batch_texts):
                cache_key = self._get_cache_key(text)
                if cache_key in self.cache:
                    cached = self.cache[cache_key]
                    batch_results[j] = SentimentResult(
                        text=text,
                        label=cached['label'],
                        score=cached['score'],
                        normalized_score=cached['normalized_score'],
                        timestamp=datetime.now(),
                        source=batch_sources[j]
                    )
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(j)

            # Process uncached texts
            if uncached_texts:
                try:
                    pipeline_results = self.sentiment_pipeline(uncached_texts)

                    for k, pipeline_result in enumerate(pipeline_results):
                        original_index = uncached_indices[k]
                        text = uncached_texts[k]

                        # Extract best result
                        best_result = max(pipeline_result, key=lambda x: x['score'])
                        label = best_result['label']
                        score = best_result['score']
                        normalized_score = self._normalize_score(label, score)

                        # Cache result
                        cache_key = self._get_cache_key(text)
                        self.cache[cache_key] = {
                            'label': label,
                            'score': score,
                            'normalized_score': normalized_score
                        }

                        batch_results[original_index] = SentimentResult(
                            text=text,
                            label=label,
                            score=score,
                            normalized_score=normalized_score,
                            timestamp=datetime.now(),
                            source=batch_sources[original_index]
                        )

                except Exception as e:
                    self.logger.error(f"Batch sentiment analysis failed: {e}")
                    # Fill with neutral sentiment
                    for idx in uncached_indices:
                        batch_results[idx] = SentimentResult(
                            text=uncached_texts[uncached_indices.index(idx)],
                            label="neutral",
                            score=0.5,
                            normalized_score=0.0,
                            timestamp=datetime.now(),
                            source=batch_sources[idx]
                        )

            results.extend(batch_results)

        # Save cache periodically
        if len(self.cache) % 100 == 0:
            self._save_cache()

        return results

    def analyze_dataframe(self, df: pd.DataFrame, text_column: str, source_column: str = None) -> pd.DataFrame:
        """Analyze sentiment for a pandas DataFrame"""

        texts = df[text_column].tolist()
        sources = df[source_column].tolist() if source_column else None

        results = self.analyze_batch(texts, sources)

        # Add results to DataFrame
        df_results = df.copy()
        df_results['sentiment_label'] = [r.label for r in results]
        df_results['sentiment_score'] = [r.score for r in results]
        df_results['sentiment_normalized'] = [r.normalized_score for r in results]
        df_results['sentiment_timestamp'] = [r.timestamp for r in results]

        return df_results

    def get_aggregated_sentiment(self,
                               results: List[SentimentResult],
                               method: str = "weighted_average") -> float:
        """Aggregate multiple sentiment scores"""

        if not results:
            return 0.0

        if method == "simple_average":
            return np.mean([r.normalized_score for r in results])

        elif method == "weighted_average":
            # Weight by confidence score
            total_weight = sum(r.score for r in results)
            if total_weight == 0:
                return 0.0
            weighted_sum = sum(r.normalized_score * r.score for r in results)
            return weighted_sum / total_weight

        elif method == "median":
            return np.median([r.normalized_score for r in results])

        else:
            raise ValueError(f"Unknown aggregation method: {method}")

    def cleanup_cache(self, max_age_days: int = 30):
        """Clean up old cache entries"""
        # For now, just save the cache
        # In a full implementation, you'd track timestamps and remove old entries
        self._save_cache()

    def __del__(self):
        """Save cache when object is destroyed"""
        if hasattr(self, 'cache'):
            self._save_cache()