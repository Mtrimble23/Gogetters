#!/usr/bin/env python3
"""
CBOE Volatility Calculator
Implements VIX-style volatility calculation for individual stocks
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, List


class CBOEVolatilityCalculator:
    """Calculates CBOE VIX-style volatility for individual stocks"""
    
    def __init__(self):
        self.risk_free_rate = 0.04  # 4% placeholder - should be fetched from Treasury
    
    def yearfrac(self, t1: datetime, t2: datetime) -> float:
        """Calculate year fraction between two dates"""
        return (t2 - t1).days / 365.0
    
    def pick_two_expiries(self, expiries: List[str], today: datetime, target_days: int = 30) -> List[str]:
        """Find two expiries that bracket target_days"""
        days = np.array([(datetime.strptime(e, "%Y-%m-%d") - today).days for e in expiries])
        after = np.where(days >= target_days)[0]
        before = np.where(days < target_days)[0]
        
        if len(after) == 0 or len(before) == 0:
            # Fallback: nearest two expiries
            idx = np.argsort(np.abs(days - target_days))[:2]
            idx.sort()
            return [expiries[idx[0]], expiries[idx[1]]]
        
        return [expiries[before[-1]], expiries[after[0]]]
    
    def forward_price_from_parity(self, chain_df: pd.DataFrame, r: float, T: float) -> float:
        """Calculate forward price from put-call parity"""
        df = chain_df.copy()
        df["mid_call"] = (df["call_bid"] + df["call_ask"]) / 2.0
        df["mid_put"] = (df["put_bid"] + df["put_ask"]) / 2.0
        df["abs_diff"] = (df["mid_call"] - df["mid_put"]).abs()
        
        k_star = df.loc[df["abs_diff"].idxmin(), "strike"]
        c_star = df.loc[df["abs_diff"].idxmin(), "mid_call"]
        p_star = df.loc[df["abs_diff"].idxmin(), "mid_put"]
        
        F = k_star + np.exp(r * T) * (c_star - p_star)
        return F
    
    def vix_style_variance_for_expiry(self, chain_df: pd.DataFrame, r: float, T: float) -> float:
        """Calculate model-free variance for one expiry"""
        df = chain_df.copy()
        df["mid_call"] = (df["call_bid"] + df["call_ask"]) / 2.0
        df["mid_put"] = (df["put_bid"] + df["put_ask"]) / 2.0
        
        # Forward & K0
        F = self.forward_price_from_parity(df, r, T)
        strikes = np.sort(df["strike"].values)
        K0 = strikes[strikes <= F][-1] if np.any(strikes <= F) else strikes[0]
        
        # Build Q(K): OTM premiums
        Q = []
        K = []
        for _, row in df.iterrows():
            k = row["strike"]
            if k < K0:
                q = row["mid_put"]
            elif k > K0:
                q = row["mid_call"]
            else:
                q = 0.5 * (row["mid_put"] + row["mid_call"])
            
            if np.isfinite(q) and q > 0:
                Q.append(q)
                K.append(k)
        
        K = np.array(sorted(K))
        # Reorder Q to match sorted K
        qmap = {}
        for _, row in df.iterrows():
            if row["strike"] == K0:
                qmap[row["strike"]] = 0.5 * (row["mid_put"] + row["mid_call"])
            elif row["strike"] < K0:
                qmap[row["strike"]] = row["mid_put"]
            else:
                qmap[row["strike"]] = row["mid_call"]
        
        Q = np.array([qmap[k] for k in K])
        
        # ΔK per CBOE: half-distance to neighbors
        dK = np.zeros_like(K, dtype=float)
        dK[1:-1] = (K[2:] - K[:-2]) / 2.0
        dK[0] = K[1] - K[0]
        dK[-1] = K[-1] - K[-2]
        
        # Model-free variance
        term1 = (2.0 / T) * np.sum((dK / (K**2)) * np.exp(r * T) * Q)
        term2 = (1.0 / T) * ((F / K[K <= F][-1] - 1.0) ** 2 if np.any(K <= F) else 0.0)
        
        return term1 - term2
    
    def build_chain_dataframe(self, ticker: str, expiry: str) -> pd.DataFrame:
        """Build option chain dataframe for given ticker and expiry"""
        try:
            tk = yf.Ticker(ticker)
            calls = tk.option_chain(expiry).calls
            puts = tk.option_chain(expiry).puts
            
            # Join by strike
            df = calls.merge(puts, on="strike", how="inner", suffixes=("_call", "_put"))
            return df.rename(columns={
                "bid_call": "call_bid", "ask_call": "call_ask",
                "bid_put": "put_bid", "ask_put": "put_ask"
            })[["strike", "call_bid", "call_ask", "put_bid", "put_ask"]].dropna()
            
        except Exception as e:
            print(f"Error building chain for {ticker} {expiry}: {e}")
            return pd.DataFrame()
    
    def calculate_vx_ticker_30d(self, ticker: str, target_days: int = 30) -> Tuple[float, Dict[str, Any]]:
        """Calculate VIX-style 30-day implied volatility for a ticker"""
        try:
            today = datetime.now(timezone.utc).replace(tzinfo=None)
            tk = yf.Ticker(ticker)
            expiries = tk.options
            
            if not expiries:
                return self._fallback_historical_volatility(ticker), {"error": "No options data"}
            
            e1, e2 = self.pick_two_expiries(expiries, today, target_days)
            r = self.risk_free_rate
            
            # First expiry
            df1 = self.build_chain_dataframe(ticker, e1)
            if df1.empty:
                return self._fallback_historical_volatility(ticker), {"error": "No chain data for e1"}
            
            T1 = self.yearfrac(today, datetime.strptime(e1, "%Y-%m-%d"))
            var1 = self.vix_style_variance_for_expiry(df1, r, T1)
            
            # Second expiry
            df2 = self.build_chain_dataframe(ticker, e2)
            if df2.empty:
                return self._fallback_historical_volatility(ticker), {"error": "No chain data for e2"}
            
            T2 = self.yearfrac(today, datetime.strptime(e2, "%Y-%m-%d"))
            var2 = self.vix_style_variance_for_expiry(df2, r, T2)
            
            # Interpolate to 30 days
            Tstar = target_days / 365.0
            var30 = ((T2 - Tstar) * var1 * T1 + (Tstar - T1) * var2 * T2) / (T2 - T1)
            var30 /= Tstar
            vx = 100.0 * np.sqrt(max(var30, 0))
            
            metadata = {
                "T1": T1, "T2": T2, "var1": var1, "var2": var2,
                "e1": e1, "e2": e2, "method": "CBOE_VIX_style"
            }
            
            return vx, metadata
            
        except Exception as e:
            print(f"Error calculating CBOE volatility for {ticker}: {e}")
            return self._fallback_historical_volatility(ticker), {"error": str(e)}
    
    def _fallback_historical_volatility(self, ticker: str, days: int = 30) -> float:
        """Fallback to historical volatility when options data unavailable"""
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period="3mo")
            if len(hist) < days:
                return 25.0  # Default volatility
            
            returns = hist['Close'].pct_change().dropna()
            vol = returns.std() * np.sqrt(252) * 100  # Annualized volatility
            return min(max(vol, 5.0), 100.0)  # Cap between 5% and 100%
            
        except Exception:
            return 25.0  # Default fallback
    
    def get_volatility_for_symbols(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Calculate CBOE volatility for multiple symbols"""
        results = {}
        for symbol in symbols:
            vx, metadata = self.calculate_vx_ticker_30d(symbol)
            results[symbol] = {
                'cboe_volatility': round(vx, 2),
                'metadata': metadata
            }
        return results


def test_cboe_calculator():
    """Test the CBOE volatility calculator"""
    calc = CBOEVolatilityCalculator()
    
    print("🧪 Testing CBOE Volatility Calculator")
    print("=" * 50)
    
    # Test single stock
    print("Testing AAPL volatility...")
    vx, meta = calc.calculate_vx_ticker_30d("AAPL")
    print(f"VX_AAPL(30) ≈ {vx:.2f}%")
    print(f"Method: {meta.get('method', 'Historical fallback')}")
    
    if 'error' in meta:
        print(f"Note: {meta['error']}")
    
    # Test batch
    print("\nTesting batch volatility...")
    batch_results = calc.get_volatility_for_symbols(['AAPL', 'MSFT', 'GOOGL'])
    for symbol, result in batch_results.items():
        vol = result['cboe_volatility']
        method = result['metadata'].get('method', 'fallback')
        print(f"{symbol}: {vol}% ({method})")


if __name__ == "__main__":
    test_cboe_calculator()