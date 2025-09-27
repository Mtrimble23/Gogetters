#ifndef TECHNICAL_INDICATORS_H
#define TECHNICAL_INDICATORS_H

#include <vector>
#include <deque>
#include <algorithm>
#include <numeric>
#include <cmath>
#include "market_data/market_data.h"

namespace TechnicalIndicators {

/**
 * Base class for technical indicators
 */
class Indicator {
public:
    virtual ~Indicator() = default;
    virtual double calculate(const MarketData::TimeSeries& ts, size_t index) const = 0;
    virtual std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const = 0;
    virtual std::string name() const = 0;
};

/**
 * Simple Moving Average
 */
class SMA : public Indicator {
private:
    int period_;
    
public:
    explicit SMA(int period) : period_(period) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "SMA(" + std::to_string(period_) + ")"; }
    
    static double calculate_sma(const std::vector<double>& values, int period);
};

/**
 * Exponential Moving Average
 */
class EMA : public Indicator {
private:
    int period_;
    double alpha_;
    
public:
    explicit EMA(int period) : period_(period), alpha_(2.0 / (period + 1)) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "EMA(" + std::to_string(period_) + ")"; }
    
    static double calculate_ema(const std::vector<double>& values, int period);
};

/**
 * Weighted Moving Average
 */
class WMA : public Indicator {
private:
    int period_;
    
public:
    explicit WMA(int period) : period_(period) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "WMA(" + std::to_string(period_) + ")"; }
};

/**
 * Relative Strength Index
 */
class RSI : public Indicator {
private:
    int period_;
    
public:
    explicit RSI(int period = 14) : period_(period) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "RSI(" + std::to_string(period_) + ")"; }
};

/**
 * Moving Average Convergence Divergence
 */
class MACD : public Indicator {
private:
    int fast_period_;
    int slow_period_;
    int signal_period_;
    
public:
    MACD(int fast = 12, int slow = 26, int signal = 9) 
        : fast_period_(fast), slow_period_(slow), signal_period_(signal) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { 
        return "MACD(" + std::to_string(fast_period_) + "," + 
               std::to_string(slow_period_) + "," + std::to_string(signal_period_) + ")"; 
    }
    
    struct MACDValues {
        std::vector<double> macd_line;
        std::vector<double> signal_line;
        std::vector<double> histogram;
    };
    
    MACDValues calculate_full(const MarketData::TimeSeries& ts) const;
};

/**
 * Bollinger Bands
 */
class BollingerBands : public Indicator {
private:
    int period_;
    double std_dev_;
    
public:
    BollingerBands(int period = 20, double std_dev = 2.0) 
        : period_(period), std_dev_(std_dev) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { 
        return "BB(" + std::to_string(period_) + "," + std::to_string(std_dev_) + ")"; 
    }
    
    struct BBValues {
        std::vector<double> upper_band;
        std::vector<double> middle_band;
        std::vector<double> lower_band;
        std::vector<double> bandwidth;
        std::vector<double> percent_b;
    };
    
    BBValues calculate_full(const MarketData::TimeSeries& ts) const;
};

/**
 * Average True Range
 */
class ATR : public Indicator {
private:
    int period_;
    
public:
    explicit ATR(int period = 14) : period_(period) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "ATR(" + std::to_string(period_) + ")"; }
    
private:
    double true_range(const MarketData::Candlestick& current, 
                     const MarketData::Candlestick& previous) const;
};

/**
 * Stochastic Oscillator
 */
class StochasticOscillator : public Indicator {
private:
    int k_period_;
    int d_period_;
    
public:
    StochasticOscillator(int k_period = 14, int d_period = 3) 
        : k_period_(k_period), d_period_(d_period) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { 
        return "STOCH(" + std::to_string(k_period_) + "," + std::to_string(d_period_) + ")"; 
    }
    
    struct StochValues {
        std::vector<double> percent_k;
        std::vector<double> percent_d;
    };
    
    StochValues calculate_full(const MarketData::TimeSeries& ts) const;
};

/**
 * On-Balance Volume
 */
class OBV : public Indicator {
public:
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "OBV"; }
};

/**
 * Chaikin Money Flow
 */
class CMF : public Indicator {
private:
    int period_;
    
public:
    explicit CMF(int period = 20) : period_(period) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "CMF(" + std::to_string(period_) + ")"; }
};

/**
 * Average Directional Index
 */
class ADX : public Indicator {
private:
    int period_;
    
public:
    explicit ADX(int period = 14) : period_(period) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "ADX(" + std::to_string(period_) + ")"; }
};

/**
 * Commodity Channel Index
 */
class CCI : public Indicator {
private:
    int period_;
    
public:
    explicit CCI(int period = 20) : period_(period) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "CCI(" + std::to_string(period_) + ")"; }
};

/**
 * Williams %R
 */
class WilliamsR : public Indicator {
private:
    int period_;
    
public:
    explicit WilliamsR(int period = 14) : period_(period) {}
    
    double calculate(const MarketData::TimeSeries& ts, size_t index) const override;
    std::vector<double> calculate_series(const MarketData::TimeSeries& ts) const override;
    std::string name() const override { return "WILLR(" + std::to_string(period_) + ")"; }
};

/**
 * Utility functions for technical analysis
 */
namespace Utils {
    double standard_deviation(const std::vector<double>& values);
    double correlation(const std::vector<double>& x, const std::vector<double>& y);
    std::vector<double> rolling_max(const std::vector<double>& values, int period);
    std::vector<double> rolling_min(const std::vector<double>& values, int period);
    std::vector<double> rolling_std(const std::vector<double>& values, int period);
}

} // namespace TechnicalIndicators

#endif // TECHNICAL_INDICATORS_H