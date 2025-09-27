#ifndef MARKET_DATA_H
#define MARKET_DATA_H

#include <vector>
#include <string>
#include <chrono>
#include <cmath>

namespace MarketData {

/**
 * Basic OHLCV candlestick data structure
 */
struct Candlestick {
    std::chrono::system_clock::time_point timestamp;
    double open;
    double high;
    double low;
    double close;
    double volume;
    
    Candlestick() : open(0), high(0), low(0), close(0), volume(0) {}
    
    Candlestick(std::chrono::system_clock::time_point ts, double o, double h, double l, double c, double v)
        : timestamp(ts), open(o), high(h), low(l), close(c), volume(v) {}
    
    // Helper methods
    double typical_price() const { return (high + low + close) / 3.0; }
    double median_price() const { return (high + low) / 2.0; }
    double weighted_close() const { return (high + low + 2 * close) / 4.0; }
    double body_size() const { return std::abs(close - open); }
    double upper_shadow() const { return high - std::max(open, close); }
    double lower_shadow() const { return std::min(open, close) - low; }
    bool is_bullish() const { return close > open; }
    bool is_bearish() const { return close < open; }
};

/**
 * Time series container for market data
 */
class TimeSeries {
private:
    std::vector<Candlestick> data_;
    std::string symbol_;
    
public:
    TimeSeries(const std::string& symbol) : symbol_(symbol) {}
    
    // Data access
    void add_candle(const Candlestick& candle) { data_.push_back(candle); }
    const std::vector<Candlestick>& get_data() const { return data_; }
    size_t size() const { return data_.size(); }
    bool empty() const { return data_.empty(); }
    
    const Candlestick& operator[](size_t index) const { return data_[index]; }
    const Candlestick& at(size_t index) const { return data_.at(index); }
    const Candlestick& latest() const { return data_.back(); }
    
    // Symbol info
    const std::string& symbol() const { return symbol_; }
    
    // Price vectors for analysis
    std::vector<double> closes() const;
    std::vector<double> opens() const;
    std::vector<double> highs() const;
    std::vector<double> lows() const;
    std::vector<double> volumes() const;
    
    // Derived price series
    std::vector<double> returns() const;
    std::vector<double> log_returns() const;
    std::vector<double> price_changes() const;
    std::vector<double> percent_changes() const;
    
    // Price velocity and acceleration
    std::vector<double> price_velocity(int period = 1) const;
    std::vector<double> price_acceleration(int period = 1) const;
    
    // Utility methods
    void clear() { data_.clear(); }
    void reserve(size_t capacity) { data_.reserve(capacity); }
    
    // Statistical measures
    double mean_close() const;
    double std_close() const;
    double min_close() const;
    double max_close() const;
};

/**
 * Features extracted from market data for VGP terminals
 */
class FeatureExtractor {
public:
    static std::vector<double> extract_ohlc_features(const TimeSeries& ts, size_t lookback_window);
    static std::vector<double> extract_volume_features(const TimeSeries& ts, size_t lookback_window);
    static std::vector<double> extract_price_action_features(const TimeSeries& ts, size_t lookback_window);
    static std::vector<double> extract_time_features(const TimeSeries& ts, size_t index);
    
    // Normalize features to [-1, 1] range for GP
    static std::vector<double> normalize_features(const std::vector<double>& features);
    static std::vector<double> z_score_normalize(const std::vector<double>& features);
};

} // namespace MarketData

#endif // MARKET_DATA_H