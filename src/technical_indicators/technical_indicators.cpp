#include "technical_indicators/technical_indicators.h"
#include <algorithm>
#include <numeric>
#include <cmath>
#include <limits>

namespace TechnicalIndicators {

// Simple Moving Average implementation
double SMA::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (index + 1 < static_cast<size_t>(period_) || ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    double sum = 0.0;
    for (int i = 0; i < period_; ++i) {
        sum += ts[index - i].close;
    }
    return sum / period_;
}

std::vector<double> SMA::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> sma_values;
    sma_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        sma_values.push_back(calculate(ts, i));
    }
    return sma_values;
}

double SMA::calculate_sma(const std::vector<double>& values, int period) {
    if (values.size() < static_cast<size_t>(period)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    double sum = 0.0;
    for (int i = 0; i < period; ++i) {
        sum += values[values.size() - 1 - i];
    }
    return sum / period;
}

// Exponential Moving Average implementation
double EMA::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    if (index == 0) {
        return ts[0].close;
    }
    
    // Calculate EMA recursively
    double prev_ema = calculate(ts, index - 1);
    if (std::isnan(prev_ema)) {
        return ts[index].close;
    }
    
    return alpha_ * ts[index].close + (1.0 - alpha_) * prev_ema;
}

std::vector<double> EMA::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> ema_values;
    ema_values.reserve(ts.size());
    
    if (ts.empty()) return ema_values;
    
    // Initialize with first close price
    ema_values.push_back(ts[0].close);
    
    for (size_t i = 1; i < ts.size(); ++i) {
        double ema = alpha_ * ts[i].close + (1.0 - alpha_) * ema_values.back();
        ema_values.push_back(ema);
    }
    
    return ema_values;
}

double EMA::calculate_ema(const std::vector<double>& values, int period) {
    if (values.empty()) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    double alpha = 2.0 / (period + 1);
    double ema = values[0];
    
    for (size_t i = 1; i < values.size(); ++i) {
        ema = alpha * values[i] + (1.0 - alpha) * ema;
    }
    
    return ema;
}

// Weighted Moving Average implementation
double WMA::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (index + 1 < static_cast<size_t>(period_) || ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    double weighted_sum = 0.0;
    double weight_sum = 0.0;
    
    for (int i = 0; i < period_; ++i) {
        int weight = period_ - i;
        weighted_sum += ts[index - i].close * weight;
        weight_sum += weight;
    }
    
    return weighted_sum / weight_sum;
}

std::vector<double> WMA::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> wma_values;
    wma_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        wma_values.push_back(calculate(ts, i));
    }
    return wma_values;
}

// RSI implementation
double RSI::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (index < static_cast<size_t>(period_) || ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    double gains = 0.0;
    double losses = 0.0;
    
    for (int i = 1; i <= period_; ++i) {
        double change = ts[index - i + 1].close - ts[index - i].close;
        if (change > 0) {
            gains += change;
        } else {
            losses += std::abs(change);
        }
    }
    
    double avg_gain = gains / period_;
    double avg_loss = losses / period_;
    
    if (avg_loss == 0.0) {
        return 100.0;
    }
    
    double rs = avg_gain / avg_loss;
    return 100.0 - (100.0 / (1.0 + rs));
}

std::vector<double> RSI::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> rsi_values;
    rsi_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        rsi_values.push_back(calculate(ts, i));
    }
    return rsi_values;
}

// MACD implementation
double MACD::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    EMA fast_ema(fast_period_);
    EMA slow_ema(slow_period_);
    
    double fast_value = fast_ema.calculate(ts, index);
    double slow_value = slow_ema.calculate(ts, index);
    
    if (std::isnan(fast_value) || std::isnan(slow_value)) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    return fast_value - slow_value;
}

std::vector<double> MACD::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> macd_values;
    macd_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        macd_values.push_back(calculate(ts, i));
    }
    return macd_values;
}

MACD::MACDValues MACD::calculate_full(const MarketData::TimeSeries& ts) const {
    MACDValues result;
    result.macd_line = calculate_series(ts);
    
    // Calculate signal line (EMA of MACD line)
    EMA signal_ema(signal_period_);
    MarketData::TimeSeries macd_ts("MACD");
    
    for (size_t i = 0; i < result.macd_line.size(); ++i) {
        if (!std::isnan(result.macd_line[i])) {
            MarketData::Candlestick macd_candle;
            macd_candle.close = result.macd_line[i];
            macd_ts.add_candle(macd_candle);
        }
    }
    
    auto signal_values = signal_ema.calculate_series(macd_ts);
    result.signal_line.reserve(result.macd_line.size());
    
    size_t signal_idx = 0;
    for (size_t i = 0; i < result.macd_line.size(); ++i) {
        if (!std::isnan(result.macd_line[i]) && signal_idx < signal_values.size()) {
            result.signal_line.push_back(signal_values[signal_idx++]);
        } else {
            result.signal_line.push_back(std::numeric_limits<double>::quiet_NaN());
        }
    }
    
    // Calculate histogram
    result.histogram.reserve(result.macd_line.size());
    for (size_t i = 0; i < result.macd_line.size(); ++i) {
        if (!std::isnan(result.macd_line[i]) && !std::isnan(result.signal_line[i])) {
            result.histogram.push_back(result.macd_line[i] - result.signal_line[i]);
        } else {
            result.histogram.push_back(std::numeric_limits<double>::quiet_NaN());
        }
    }
    
    return result;
}

// Bollinger Bands implementation
double BollingerBands::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    // Returns middle band (SMA)
    SMA sma(period_);
    return sma.calculate(ts, index);
}

std::vector<double> BollingerBands::calculate_series(const MarketData::TimeSeries& ts) const {
    SMA sma(period_);
    return sma.calculate_series(ts);
}

BollingerBands::BBValues BollingerBands::calculate_full(const MarketData::TimeSeries& ts) const {
    BBValues result;
    
    SMA sma(period_);
    result.middle_band = sma.calculate_series(ts);
    
    result.upper_band.reserve(ts.size());
    result.lower_band.reserve(ts.size());
    result.bandwidth.reserve(ts.size());
    result.percent_b.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        if (i + 1 >= static_cast<size_t>(period_)) {
            // Calculate standard deviation for the period
            double sum = 0.0;
            double mean = result.middle_band[i];
            
            for (int j = 0; j < period_; ++j) {
                double diff = ts[i - j].close - mean;
                sum += diff * diff;
            }
            
            double std_dev = std::sqrt(sum / period_);
            
            result.upper_band.push_back(mean + std_dev_ * std_dev);
            result.lower_band.push_back(mean - std_dev_ * std_dev);
            result.bandwidth.push_back(2.0 * std_dev_ * std_dev / mean);
            
            // %B calculation
            double price = ts[i].close;
            if (result.upper_band.back() != result.lower_band.back()) {
                double percent_b = (price - result.lower_band.back()) / 
                                 (result.upper_band.back() - result.lower_band.back());
                result.percent_b.push_back(percent_b);
            } else {
                result.percent_b.push_back(0.5);
            }
        } else {
            result.upper_band.push_back(std::numeric_limits<double>::quiet_NaN());
            result.lower_band.push_back(std::numeric_limits<double>::quiet_NaN());
            result.bandwidth.push_back(std::numeric_limits<double>::quiet_NaN());
            result.percent_b.push_back(std::numeric_limits<double>::quiet_NaN());
        }
    }
    
    return result;
}

// ATR implementation
double ATR::true_range(const MarketData::Candlestick& current, 
                      const MarketData::Candlestick& previous) const {
    double tr1 = current.high - current.low;
    double tr2 = std::abs(current.high - previous.close);
    double tr3 = std::abs(current.low - previous.close);
    
    return std::max({tr1, tr2, tr3});
}

double ATR::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (index < static_cast<size_t>(period_) || ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    double sum_tr = 0.0;
    for (int i = 1; i <= period_; ++i) {
        double tr = true_range(ts[index - i + 1], ts[index - i]);
        sum_tr += tr;
    }
    
    return sum_tr / period_;
}

std::vector<double> ATR::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> atr_values;
    atr_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        atr_values.push_back(calculate(ts, i));
    }
    return atr_values;
}

// Stochastic Oscillator implementation
double StochasticOscillator::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    // Returns %K value
    if (index + 1 < static_cast<size_t>(k_period_) || ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    double lowest_low = std::numeric_limits<double>::max();
    double highest_high = std::numeric_limits<double>::lowest();
    
    for (int i = 0; i < k_period_; ++i) {
        const auto& candle = ts[index - i];
        lowest_low = std::min(lowest_low, candle.low);
        highest_high = std::max(highest_high, candle.high);
    }
    
    double current_close = ts[index].close;
    
    if (highest_high == lowest_low) {
        return 50.0; // Avoid division by zero
    }
    
    return 100.0 * (current_close - lowest_low) / (highest_high - lowest_low);
}

std::vector<double> StochasticOscillator::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> stoch_values;
    stoch_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        stoch_values.push_back(calculate(ts, i));
    }
    return stoch_values;
}

StochasticOscillator::StochValues StochasticOscillator::calculate_full(const MarketData::TimeSeries& ts) const {
    StochValues result;
    result.percent_k = calculate_series(ts);
    
    // Calculate %D as SMA of %K
    SMA d_sma(d_period_);
    MarketData::TimeSeries k_ts("StochK");
    
    for (double k_value : result.percent_k) {
        if (!std::isnan(k_value)) {
            MarketData::Candlestick k_candle;
            k_candle.close = k_value;
            k_ts.add_candle(k_candle);
        }
    }
    
    auto d_values = d_sma.calculate_series(k_ts);
    result.percent_d.reserve(result.percent_k.size());
    
    size_t d_idx = 0;
    for (size_t i = 0; i < result.percent_k.size(); ++i) {
        if (!std::isnan(result.percent_k[i]) && d_idx < d_values.size()) {
            result.percent_d.push_back(d_values[d_idx++]);
        } else {
            result.percent_d.push_back(std::numeric_limits<double>::quiet_NaN());
        }
    }
    
    return result;
}

// OBV implementation
double OBV::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (ts.size() <= index || index == 0) {
        return ts.size() > index ? ts[index].volume : 0.0;
    }
    
    double prev_obv = calculate(ts, index - 1);
    double price_change = ts[index].close - ts[index - 1].close;
    
    if (price_change > 0) {
        return prev_obv + ts[index].volume;
    } else if (price_change < 0) {
        return prev_obv - ts[index].volume;
    } else {
        return prev_obv;
    }
}

std::vector<double> OBV::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> obv_values;
    obv_values.reserve(ts.size());
    
    if (ts.empty()) return obv_values;
    
    obv_values.push_back(ts[0].volume);
    
    for (size_t i = 1; i < ts.size(); ++i) {
        double price_change = ts[i].close - ts[i - 1].close;
        
        if (price_change > 0) {
            obv_values.push_back(obv_values.back() + ts[i].volume);
        } else if (price_change < 0) {
            obv_values.push_back(obv_values.back() - ts[i].volume);
        } else {
            obv_values.push_back(obv_values.back());
        }
    }
    
    return obv_values;
}

// CMF implementation
double CMF::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (index + 1 < static_cast<size_t>(period_) || ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    double sum_mfv = 0.0;
    double sum_volume = 0.0;
    
    for (int i = 0; i < period_; ++i) {
        const auto& candle = ts[index - i];
        
        // Money Flow Multiplier
        double mfm = 0.0;
        if (candle.high != candle.low) {
            mfm = ((candle.close - candle.low) - (candle.high - candle.close)) / (candle.high - candle.low);
        }
        
        // Money Flow Volume
        double mfv = mfm * candle.volume;
        
        sum_mfv += mfv;
        sum_volume += candle.volume;
    }
    
    if (sum_volume == 0.0) return 0.0;
    
    return sum_mfv / sum_volume;
}

std::vector<double> CMF::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> cmf_values;
    cmf_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        cmf_values.push_back(calculate(ts, i));
    }
    return cmf_values;
}

// ADX implementation (simplified)
double ADX::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (index < static_cast<size_t>(period_ + 1) || ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    // Simplified ADX calculation
    std::vector<double> dx_values;
    
    for (int i = 1; i <= period_; ++i) {
        const auto& current = ts[index - i + 1];
        const auto& previous = ts[index - i];
        
        double dm_plus = (current.high - previous.high > previous.low - current.low) ? 
                         std::max(0.0, current.high - previous.high) : 0.0;
        double dm_minus = (previous.low - current.low > current.high - previous.high) ? 
                          std::max(0.0, previous.low - current.low) : 0.0;
        
        ATR atr(1);
        double tr = atr.calculate(ts, index - i + 1);
        if (tr == 0.0) continue;
        
        double di_plus = 100.0 * dm_plus / tr;
        double di_minus = 100.0 * dm_minus / tr;
        
        if (di_plus + di_minus != 0) {
            double dx = 100.0 * std::abs(di_plus - di_minus) / (di_plus + di_minus);
            dx_values.push_back(dx);
        }
    }
    
    if (dx_values.empty()) return std::numeric_limits<double>::quiet_NaN();
    
    return std::accumulate(dx_values.begin(), dx_values.end(), 0.0) / dx_values.size();
}

std::vector<double> ADX::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> adx_values;
    adx_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        adx_values.push_back(calculate(ts, i));
    }
    return adx_values;
}

// CCI implementation
double CCI::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (index + 1 < static_cast<size_t>(period_) || ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    // Calculate typical price SMA
    double tp_sum = 0.0;
    std::vector<double> typical_prices;
    
    for (int i = 0; i < period_; ++i) {
        double tp = ts[index - i].typical_price();
        typical_prices.push_back(tp);
        tp_sum += tp;
    }
    
    double tp_sma = tp_sum / period_;
    
    // Calculate mean deviation
    double sum_deviations = 0.0;
    for (double tp : typical_prices) {
        sum_deviations += std::abs(tp - tp_sma);
    }
    double mean_deviation = sum_deviations / period_;
    
    if (mean_deviation == 0.0) return 0.0;
    
    double current_tp = ts[index].typical_price();
    return (current_tp - tp_sma) / (0.015 * mean_deviation);
}

std::vector<double> CCI::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> cci_values;
    cci_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        cci_values.push_back(calculate(ts, i));
    }
    return cci_values;
}

// Williams %R implementation
double WilliamsR::calculate(const MarketData::TimeSeries& ts, size_t index) const {
    if (index + 1 < static_cast<size_t>(period_) || ts.size() <= index) {
        return std::numeric_limits<double>::quiet_NaN();
    }
    
    double highest_high = std::numeric_limits<double>::lowest();
    double lowest_low = std::numeric_limits<double>::max();
    
    for (int i = 0; i < period_; ++i) {
        const auto& candle = ts[index - i];
        highest_high = std::max(highest_high, candle.high);
        lowest_low = std::min(lowest_low, candle.low);
    }
    
    double current_close = ts[index].close;
    
    if (highest_high == lowest_low) {
        return -50.0;
    }
    
    return -100.0 * (highest_high - current_close) / (highest_high - lowest_low);
}

std::vector<double> WilliamsR::calculate_series(const MarketData::TimeSeries& ts) const {
    std::vector<double> willr_values;
    willr_values.reserve(ts.size());
    
    for (size_t i = 0; i < ts.size(); ++i) {
        willr_values.push_back(calculate(ts, i));
    }
    return willr_values;
}

// Utility functions
namespace Utils {

double standard_deviation(const std::vector<double>& values) {
    if (values.size() < 2) return 0.0;
    
    double mean = std::accumulate(values.begin(), values.end(), 0.0) / values.size();
    double sum_sq_diff = 0.0;
    
    for (double value : values) {
        double diff = value - mean;
        sum_sq_diff += diff * diff;
    }
    
    return std::sqrt(sum_sq_diff / (values.size() - 1));
}

double correlation(const std::vector<double>& x, const std::vector<double>& y) {
    if (x.size() != y.size() || x.size() < 2) {
        return 0.0;
    }
    
    double mean_x = std::accumulate(x.begin(), x.end(), 0.0) / x.size();
    double mean_y = std::accumulate(y.begin(), y.end(), 0.0) / y.size();
    
    double sum_xy = 0.0;
    double sum_x2 = 0.0;
    double sum_y2 = 0.0;
    
    for (size_t i = 0; i < x.size(); ++i) {
        double dx = x[i] - mean_x;
        double dy = y[i] - mean_y;
        sum_xy += dx * dy;
        sum_x2 += dx * dx;
        sum_y2 += dy * dy;
    }
    
    double denominator = std::sqrt(sum_x2 * sum_y2);
    if (denominator == 0.0) return 0.0;
    
    return sum_xy / denominator;
}

std::vector<double> rolling_max(const std::vector<double>& values, int period) {
    std::vector<double> result;
    result.reserve(values.size());
    
    for (size_t i = 0; i < values.size(); ++i) {
        if (i + 1 < static_cast<size_t>(period)) {
            result.push_back(std::numeric_limits<double>::quiet_NaN());
        } else {
            double max_val = std::numeric_limits<double>::lowest();
            for (int j = 0; j < period; ++j) {
                max_val = std::max(max_val, values[i - j]);
            }
            result.push_back(max_val);
        }
    }
    
    return result;
}

std::vector<double> rolling_min(const std::vector<double>& values, int period) {
    std::vector<double> result;
    result.reserve(values.size());
    
    for (size_t i = 0; i < values.size(); ++i) {
        if (i + 1 < static_cast<size_t>(period)) {
            result.push_back(std::numeric_limits<double>::quiet_NaN());
        } else {
            double min_val = std::numeric_limits<double>::max();
            for (int j = 0; j < period; ++j) {
                min_val = std::min(min_val, values[i - j]);
            }
            result.push_back(min_val);
        }
    }
    
    return result;
}

std::vector<double> rolling_std(const std::vector<double>& values, int period) {
    std::vector<double> result;
    result.reserve(values.size());
    
    for (size_t i = 0; i < values.size(); ++i) {
        if (i + 1 < static_cast<size_t>(period)) {
            result.push_back(std::numeric_limits<double>::quiet_NaN());
        } else {
            std::vector<double> window;
            for (int j = 0; j < period; ++j) {
                window.push_back(values[i - j]);
            }
            result.push_back(standard_deviation(window));
        }
    }
    
    return result;
}

} // namespace Utils

} // namespace TechnicalIndicators