# VGP + NEAT Trading Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA INPUTS                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
        ▼                            ▼                            ▼
┌──────────────┐            ┌─────────────────┐          ┌─────────────────┐
│   OHLCV      │            │   NEWS/SOCIAL   │          │   MARKET DATA   │
│   Raw Data   │            │   MEDIA DATA    │          │   VIX, Sector   │
│              │            │                 │          │   SPY, etc.     │
│ • Open       │            │ • Headlines     │          │                 │
│ • High       │            │ • Social posts  │          │ • Volatility    │
│ • Low        │            │ • News articles │          │ • Market regime │
│ • Close      │            │                 │          │ • Time features │
│ • Volume     │            │                 │          │                 │
└──────────────┘            └─────────────────┘          └─────────────────┘
        │                            │                            │
        ▼                            ▼                            │
┌─────────────────────────────────────────────────────────────────┐       │
│                    VGP SYSTEM (Your Partner)                    │       │
│                                                                 │       │
│  Input: OHLCV → Genetic Programming → Optimized Weights        │       │
│                                                                 │       │
│  VGP Discovers:                                                 │       │
│  • w1*Open + w2*High + w3*Low + w4*Close + w5*Typical_Price    │       │
│  • w6*Lower_Shadow + w7*Upper_Shadow                            │       │
│  • w8*Median_Price + w9*Weighted_Close                         │       │
│                                                                 │       │
│  Output: VGP_Signal_Vector = [vgp_price, vgp_shadow, vgp_vol]  │       │
└─────────────────────────────────────────────────────────────────┘       │
        │                                                                  │
        ▼                            ▼                                     │
┌─────────────────┐          ┌─────────────────┐                          │
│  VGP SIGNALS    │          │   SENTIMENT     │                          │
│                 │          │   ANALYSIS      │                          │
│ • vgp_price     │          │                 │                          │
│ • vgp_shadow    │          │ • sentiment     │                          │
│ • vgp_volatility│          │ • confidence    │                          │
└─────────────────┘          └─────────────────┘                          │
        │                            │                                     │
        └────────────────────────────┼─────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FEATURE ENGINEERING                                  │
│                                                                         │
│  Combined Feature Vector:                                               │
│  [vgp_price, vgp_shadow, vgp_vol, sentiment, volume_ratio,            │
│   time_features, market_regime, sector_momentum, ...]                  │
│                                                                         │
│  Normalized to [-1, 1] for NEAT                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         NEAT SYSTEM                                     │
│                                                                         │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐                │
│  │ Population  │    │  Evolution   │    │  Selection  │                │
│  │ Generation  │───▶│  & Mutation  │───▶│ & Fitness   │                │
│  └─────────────┘    └──────────────┘    └─────────────┘                │
│         ▲                                        │                     │
│         └────────────────────────────────────────┘                     │
│                                                                         │
│  NEAT Discovers:                                                        │
│  • When VGP signals predict future returns                              │
│  • Market conditions where VGP works best                               │
│  • Optimal combinations: VGP + sentiment + volume                       │
│  • Timing patterns: "VGP works better at market open"                   │
│                                                                         │
│  Output: Neural Network Topology + Weights                              │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PATTERN DISCOVERY                                    │
│                                                                         │
│  Pattern Examples:                                                      │
│  • "High VGP signal + Positive sentiment + Low volatility = 73% win"    │
│  • "VGP shadow signal + Volume spike = Mean reversion opportunity"      │
│  • "VGP signals 2x stronger during first hour of trading"              │
│                                                                         │
│  Ranking & Validation:                                                  │
│  • Statistical significance testing                                     │
│  • Cross-validation across time periods                                 │
│  • Pattern persistence analysis                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    OUTPUT DASHBOARD                                     │
│                                                                         │
│  • Top 10 discovered patterns                                           │
│  • Pattern strength over time                                           │
│  • Feature importance rankings                                          │
│  • When patterns are most active                                        │
│  • Risk/return metrics for each pattern                                 │
│  • Educational explanations of why patterns work                        │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Relationships:

1. **VGP → Optimized Price Math**: Your partner finds the best mathematical combinations of OHLC
2. **VGP Signals → NEAT Inputs**: Those optimized formulas become features for NEAT
3. **NEAT → Pattern Discovery**: NEAT learns when/how to use VGP signals effectively
4. **Combined System → Market Insights**: Discovers timing and context patterns

## Data Flow Summary:
```
Raw OHLCV → VGP Weights → VGP Signals → NEAT Features → Pattern Discovery → Insights
```

The magic happens when NEAT finds that **VGP signal X + market condition Y = predictive pattern Z**!