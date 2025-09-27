#include "market_data/market_data.h"
#include <algorithm>
#include <numeric>
#include <cmath>

namespace MarketData {

// TimeSeries price vector methods
std::vector<double> TimeSeries::closes() const {
    std::vector<double> closes;
    closes.reserve(data_.size());
    for (const auto& candle : data_) {
        closes.push_back(candle.close);
    }
    return closes;
}

std::vector<double> TimeSeries::opens() const {
    std::vector<double> opens;
    opens.reserve(data_.size());
    for (const auto& candle : data_) {
        opens.push_back(candle.open);
    }
    return opens;
}

std::vector<double> TimeSeries::highs() const {
    std::vector<double> highs;
    highs.reserve(data_.size());
    for (const auto& candle : data_) {
        highs.push_back(candle.high);
    }
    return highs;
}

std::vector<double> TimeSeries::lows() const {
    std::vector<double> lows;
    lows.reserve(data_.size());
    for (const auto& candle : data_) {
        lows.push_back(candle.low);
    }
    return lows;
}

std::vector<double> TimeSeries::volumes() const {
    std::vector<double> volumes;
    volumes.reserve(data_.size());
    for (const auto& candle : data_) {
        volumes.push_back(candle.volume);
    }
    return volumes;
}

// Derived price series
std::vector<double> TimeSeries::returns() const {
    if (data_.size() < 2) return {};
    
    std::vector<double> returns;
    returns.reserve(data_.size() - 1);
    
    for (size_t i = 1; i < data_.size(); ++i) {
        double ret = data_[i].close - data_[i-1].close;
        returns.push_back(ret);
    }
    return returns;
}

std::vector<double> TimeSeries::log_returns() const {
    if (data_.size() < 2) return {};
    
    std::vector<double> log_returns;
    log_returns.reserve(data_.size() - 1);
    
    for (size_t i = 1; i < data_.size(); ++i) {
        if (data_[i-1].close > 0 && data_[i].close > 0) {
            double log_ret = std::log(data_[i].close / data_[i-1].close);
            log_returns.push_back(log_ret);
        } else {
            log_returns.push_back(0.0); // Handle edge case
        }
    }
    return log_returns;
}

std::vector<double> TimeSeries::price_changes() const {
    return returns(); // Same as returns for absolute price changes
}

std::vector<double> TimeSeries::percent_changes() const {
    if (data_.size() < 2) return {};
    
    std::vector<double> percent_changes;
    percent_changes.reserve(data_.size() - 1);
    
    for (size_t i = 1; i < data_.size(); ++i) {
        if (data_[i-1].close != 0) {
            double pct_change = (data_[i].close - data_[i-1].close) / data_[i-1].close;
            percent_changes.push_back(pct_change);
        } else {
            percent_changes.push_back(0.0);
        }
    }
    return percent_changes;
}

// Price velocity and acceleration
std::vector<double> TimeSeries::price_velocity(int period) const {
    if (data_.size() < static_cast<size_t>(period + 1)) return {};
    
    std::vector<double> velocity;
    velocity.reserve(data_.size() - period);
    
    for (size_t i = period; i < data_.size(); ++i) {
        double vel = (data_[i].close - data_[i - period].close) / period;
        velocity.push_back(vel);
    }
    return velocity;
}

std::vector<double> TimeSeries::price_acceleration(int period) const {
    auto velocity = price_velocity(period);
    if (velocity.size() < 2) return {};
    
    std::vector<double> acceleration;
    acceleration.reserve(velocity.size() - 1);
    
    for (size_t i = 1; i < velocity.size(); ++i) {
        double accel = velocity[i] - velocity[i-1];
        acceleration.push_back(accel);
    }
    return acceleration;
}

// Statistical measures
double TimeSeries::mean_close() const {
    if (data_.empty()) return 0.0;
    
    double sum = 0.0;
    for (const auto& candle : data_) {
        sum += candle.close;
    }
    return sum / data_.size();
}

double TimeSeries::std_close() const {
    if (data_.size() < 2) return 0.0;
    
    double mean = mean_close();
    double sum_sq_diff = 0.0;
    
    for (const auto& candle : data_) {
        double diff = candle.close - mean;
        sum_sq_diff += diff * diff;
    }
    
    return std::sqrt(sum_sq_diff / (data_.size() - 1));
}

double TimeSeries::min_close() const {
    if (data_.empty()) return 0.0;
    
    auto min_it = std::min_element(data_.begin(), data_.end(),
        [](const Candlestick& a, const Candlestick& b) {
            return a.close < b.close;
        });
    return min_it->close;
}

double TimeSeries::max_close() const {
    if (data_.empty()) return 0.0;
    
    auto max_it = std::max_element(data_.begin(), data_.end(),
        [](const Candlestick& a, const Candlestick& b) {
            return a.close < b.close;
        });
    return max_it->close;
}

// FeatureExtractor implementation
std::vector<double> FeatureExtractor::extract_ohlc_features(const TimeSeries& ts, size_t lookback_window) {
    std::vector<double> features;
    
    if (ts.size() < lookback_window) {
        return features;
    }
    
    size_t start_idx = ts.size() - lookback_window;
    
    for (size_t i = start_idx; i < ts.size(); ++i) {
        const auto& candle = ts[i];
        
        // Basic OHLC
        features.push_back(candle.open);
        features.push_back(candle.high);
        features.push_back(candle.low);
        features.push_back(candle.close);
        
        // Derived features
        features.push_back(candle.typical_price());
        features.push_back(candle.median_price());
        features.push_back(candle.weighted_close());
        features.push_back(candle.body_size());
        features.push_back(candle.upper_shadow());
        features.push_back(candle.lower_shadow());
        features.push_back(candle.is_bullish() ? 1.0 : -1.0);
    }
    
    return features;
}

std::vector<double> FeatureExtractor::extract_volume_features(const TimeSeries& ts, size_t lookback_window) {
    std::vector<double> features;
    
    if (ts.size() < lookback_window) {
        return features;
    }
    
    size_t start_idx = ts.size() - lookback_window;
    double volume_sum = 0.0;
    
    // Calculate average volume for normalization
    for (size_t i = start_idx; i < ts.size(); ++i) {
        volume_sum += ts[i].volume;
    }
    double avg_volume = volume_sum / lookback_window;
    
    for (size_t i = start_idx; i < ts.size(); ++i) {
        const auto& candle = ts[i];
        
        // Raw volume
        features.push_back(candle.volume);
        
        // Volume relative to average
        if (avg_volume > 0) {
            features.push_back(candle.volume / avg_volume);
        } else {
            features.push_back(1.0);
        }
        
        // Volume-weighted price
        if (candle.volume > 0) {
            features.push_back(candle.close * candle.volume);
        } else {
            features.push_back(candle.close);
        }
    }
    
    return features;
}

std::vector<double> FeatureExtractor::extract_price_action_features(const TimeSeries& ts, size_t lookback_window) {
    std::vector<double> features;
    
    if (ts.size() < lookback_window + 1) {
        return features;
    }
    
    auto returns = ts.returns();
    auto log_returns = ts.log_returns();
    auto pct_changes = ts.percent_changes();
    
    size_t start_idx = returns.size() - lookback_window;
    
    for (size_t i = start_idx; i < returns.size(); ++i) {
        // Price movements
        features.push_back(returns[i]);
        features.push_back(log_returns[i]);
        features.push_back(pct_changes[i]);
        
        // Price momentum indicators
        features.push_back(returns[i] > 0 ? 1.0 : -1.0); // Direction
        features.push_back(std::abs(returns[i])); // Magnitude
    }
    
    return features;
}

std::vector<double> FeatureExtractor::extract_time_features(const TimeSeries& ts, size_t index) {
    std::vector<double> features;
    
    if (index >= ts.size()) {
        return features;
    }
    
    auto time_point = ts[index].timestamp;
    auto time_t = std::chrono::system_clock::to_time_t(time_point);
    auto* tm = std::gmtime(&time_t);
    
    if (tm) {
        // Hour of day (0-23) normalized to [-1, 1]
        double hour_norm = (tm->tm_hour / 23.0) * 2.0 - 1.0;
        features.push_back(hour_norm);
        
        // Day of week (0-6) as sine/cosine encoding
        double day_angle = (tm->tm_wday / 7.0) * 2.0 * 3.14159265359;
        features.push_back(std::sin(day_angle));
        features.push_back(std::cos(day_angle));
        
        // Day of month (1-31) normalized
        double day_norm = ((tm->tm_mday - 1) / 30.0) * 2.0 - 1.0;
        features.push_back(day_norm);
        
        // Month (0-11) as sine/cosine encoding
        double month_angle = (tm->tm_mon / 12.0) * 2.0 * 3.14159265359;
        features.push_back(std::sin(month_angle));
        features.push_back(std::cos(month_angle));
    }
    
    return features;
}

std::vector<double> FeatureExtractor::normalize_features(const std::vector<double>& features) {
    if (features.empty()) return {};
    
    auto min_it = std::min_element(features.begin(), features.end());
    auto max_it = std::max_element(features.begin(), features.end());
    
    double min_val = *min_it;
    double max_val = *max_it;
    double range = max_val - min_val;
    
    std::vector<double> normalized;
    normalized.reserve(features.size());
    
    if (range > 0) {
        for (double feature : features) {
            double norm_val = 2.0 * (feature - min_val) / range - 1.0; // Scale to [-1, 1]
            normalized.push_back(norm_val);
        }
    } else {
        // All features are the same value
        normalized.assign(features.size(), 0.0);
    }
    
    return normalized;
}

std::vector<double> FeatureExtractor::z_score_normalize(const std::vector<double>& features) {
    if (features.size() < 2) return features;
    
    // Calculate mean
    double mean = std::accumulate(features.begin(), features.end(), 0.0) / features.size();
    
    // Calculate standard deviation
    double sum_sq_diff = 0.0;
    for (double feature : features) {
        double diff = feature - mean;
        sum_sq_diff += diff * diff;
    }
    double std_dev = std::sqrt(sum_sq_diff / (features.size() - 1));
    
    std::vector<double> normalized;
    normalized.reserve(features.size());
    
    if (std_dev > 0) {
        for (double feature : features) {
            double z_score = (feature - mean) / std_dev;
            normalized.push_back(z_score);
        }
    } else {
        // All features are the same value
        normalized.assign(features.size(), 0.0);
    }
    
    return normalized;
}

} // namespace MarketData