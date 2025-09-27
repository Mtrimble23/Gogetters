#ifndef DATA_LOADER_H
#define DATA_LOADER_H

#include <string>
#include <vector>
#include <chrono>
#include <fstream>
#include <sstream>
#include <iostream>
#include "market_data/market_data.h"

namespace DataLoader {

/**
 * CSV data loader for stock market data
 */
class CSVLoader {
public:
    struct Config {
        // Format options
        std::string date_format;
        char delimiter;
        bool has_header;
        bool skip_invalid_rows;
        
        // Column indices (0-based)
        int date_col;
        int open_col;
        int high_col;
        int low_col;
        int close_col;
        int volume_col;
        int adj_close_col; // Optional, use -1 to ignore
        
        Config() : date_format("YYYY-MM-DD"), delimiter(','), 
                  has_header(true), skip_invalid_rows(true),
                  date_col(0), open_col(1), high_col(2), low_col(3),
                  close_col(4), volume_col(5), adj_close_col(6) {}
    };
    
private:
    Config config_;
    
public:
    CSVLoader() {}
    CSVLoader(const Config& config) : config_(config) {}
    
    // Load data from CSV file
    bool load_from_file(const std::string& filename, MarketData::TimeSeries& ts);
    
    // Load data from Yahoo Finance format
    bool load_yahoo_finance_csv(const std::string& filename, MarketData::TimeSeries& ts);
    
    // Parse date string to time_point
    std::chrono::system_clock::time_point parse_date(const std::string& date_str) const;
    
    // Validate data integrity
    bool validate_data(const MarketData::TimeSeries& ts) const;
    
    // Configuration
    void set_config(const Config& config) { config_ = config; }
    const Config& get_config() const { return config_; }
    
private:
    std::vector<std::string> split_line(const std::string& line, char delimiter) const;
    bool is_valid_price(double price) const;
    bool is_valid_volume(double volume) const;
};

/**
 * Yahoo Finance data downloader (mock implementation - in real project would use curl/HTTP)
 */
class YahooFinanceLoader {
public:
    struct Config {
        std::string symbol;
        std::string start_date = "2018-01-01"; // 7 years ago
        std::string end_date = "2025-01-01";   // Current
        std::string interval = "1d";           // Daily data
    };
    
private:
    Config config_;
    
public:
    YahooFinanceLoader(const Config& config) : config_(config) {}
    
    // Generate instructions for downloading data
    std::string get_download_instructions() const;
    
    // Generate Yahoo Finance CSV URL
    std::string get_yahoo_finance_url() const;
    
    // Load data if file exists
    bool load_if_exists(const std::string& filename, MarketData::TimeSeries& ts);
    
    const Config& get_config() const { return config_; }
};

/**
 * Data statistics and validation
 */
class DataValidator {
public:
    struct Statistics {
        size_t total_records = 0;
        size_t valid_records = 0;
        size_t invalid_records = 0;
        
        double min_price = 0.0;
        double max_price = 0.0;
        double avg_price = 0.0;
        
        double min_volume = 0.0;
        double max_volume = 0.0;
        double avg_volume = 0.0;
        
        std::chrono::system_clock::time_point start_date;
        std::chrono::system_clock::time_point end_date;
        
        std::vector<std::string> issues;
    };
    
    static Statistics analyze_data(const MarketData::TimeSeries& ts);
    static void print_statistics(const Statistics& stats);
    static bool is_data_suitable_for_trading(const Statistics& stats);
};

} // namespace DataLoader

#endif // DATA_LOADER_H