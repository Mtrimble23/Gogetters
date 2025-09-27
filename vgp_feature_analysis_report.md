# VGP Trading System - Feature Analysis Report
==================================================
Generated: 2025-09-27 18:13:59
Total samples analyzed: 23,767
Total features analyzed: 49

## Executive Summary
--------------------
• **32 features** are highly significant (p < 0.01)
• **36 features** are statistically significant (p < 0.05)
• **186 feature pairs** are highly correlated (r > 0.8)
• **Top 5 features** achieve 51.0% accuracy
• **Performance loss** with reduced features: 0.025

## Top 15 Most Important Features
-----------------------------------
| Rank | Feature | Importance | P-value | Significance |
|------|---------|------------|---------|--------------|
|  1 | bb_upper_10          | 0.6299 | 0.0000 | *** |
|  2 | sma_5                | 0.6261 | 0.0000 | *** |
|  3 | sma_200              | 0.6112 | 0.0000 | *** |
|  4 | bb_lower_10          | 0.5546 | 0.0000 | *** |
|  5 | sma_10_ratio         | 0.5466 | 0.0000 | *** |
|  6 | sma_10               | 0.5226 | 0.0000 | *** |
|  7 | bb_upper_20          | 0.5184 | 0.0000 | *** |
|  8 | ema_50               | 0.4924 | 0.0000 | *** |
|  9 | bb_lower_20          | 0.4871 | 0.0000 | *** |
| 10 | ema_21               | 0.4858 | 0.0000 | *** |
| 11 | sma_20               | 0.4829 | 0.0000 | *** |
| 12 | sma_50               | 0.4769 | 0.0000 | *** |
| 13 | open                 | 0.4740 | 0.0000 | *** |
| 14 | ema_12               | 0.4653 | 0.0000 | *** |
| 15 | ema_8                | 0.4599 | 0.0000 | *** |

## Highly Correlated Feature Pairs (r > 0.8)
----------------------------------------
| Feature 1 | Feature 2 | Correlation |
|-----------|-----------|-------------|
| ema_21               | ema_26               | 1.000 |
| ema_8                | ema_12               | 1.000 |
| close                | low                  | 1.000 |
| open                 | high                 | 1.000 |
| close                | high                 | 1.000 |
| open                 | low                  | 1.000 |
| high                 | low                  | 1.000 |
| ema_12               | ema_21               | 1.000 |
| close                | open                 | 1.000 |
| sma_10               | bb_upper_10          | 0.999 |
| ... and 176 more pairs ... | | |

## Model Performance with Reduced Features
------------------------------------------
| Features | Accuracy | Loss vs Full | Recommended |
|----------|----------|--------------|-------------|
|       49 | 0.5345 | +nan |             |
|        5 | 0.5099 | +0.0246 |             |
|       10 | 0.5105 | +0.0240 |             |
|       15 | 0.5103 | +0.0242 |             |
|       20 | 0.5133 | +0.0212 |             |
|       25 | 0.5271 | +0.0074 | ✓           |

## Recommendations
-----------------
1. **Recommended reduced model**: Use top 25 features
   - Maintains 52.7% accuracy
   - Reduces complexity by 49%
2. **Remove highly correlated features** to reduce multicollinearity:
   - Remove 'ema_26' (correlated with 1.00)
   - Remove 'ema_8' (correlated with 1.00)
   - Remove 'low' (correlated with 1.00)
   - Remove 'high' (correlated with 1.00)
   - Remove 'high' (correlated with 1.00)
3. **Consider removing 13 non-significant features** (p ≥ 0.05)

## Notes
- *** p < 0.001, ** p < 0.01, * p < 0.05
- Composite score combines correlation, mutual information, F-statistic, and logistic regression coefficients
- Analysis based on 5-day forward return prediction