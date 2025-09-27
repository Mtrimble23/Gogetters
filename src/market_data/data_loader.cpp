#include "market_data/data_loader.h"
#include <algorithm>
#include <numeric>
#include <ctime>
#include <iomanip>

namespace DataLoader {

// CSVLoader implementation
bool CSVLoader::load_from_file(const std::string& filename, MarketData::TimeSeries& ts) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return false;
    }
    
    std::string line;
    size_t line_number = 0;
    size_t loaded_count = 0;
    size_t skipped_count = 0;
    
    // Skip header if present
    if (config_.has_header && std::getline(file, line)) {
        line_number++;
    }
    
    while (std::getline(file, line)) {
        line_number++;
        
        if (line.empty()) continue;
        
        auto fields = split_line(line, config_.delimiter);
        
        // Validate field count
        int min_fields = std::max({config_.date_col, config_.open_col, config_.high_col, 
                                  config_.low_col, config_.close_col, config_.volume_col}) + 1;
        
        if (static_cast<int>(fields.size()) < min_fields) {
            if (config_.skip_invalid_rows) {
                skipped_count++;
                continue;
            } else {
                std::cerr << "Error: Line " << line_number << " has insufficient fields" << std::endl;
                return false;
            }
        }
        
        try {
            // Parse date
            auto timestamp = parse_date(fields[config_.date_col]);
            
            // Parse prices
            double open = std::stod(fields[config_.open_col]);
            double high = std::stod(fields[config_.high_col]);
            double low = std::stod(fields[config_.low_col]);
            double close = std::stod(fields[config_.close_col]);
            double volume = std::stod(fields[config_.volume_col]);
            
            // Use adjusted close if available and valid
            if (config_.adj_close_col >= 0 && config_.adj_close_col < static_cast<int>(fields.size())) {
                try {
                    double adj_close = std::stod(fields[config_.adj_close_col]);
                    if (is_valid_price(adj_close)) {
                        close = adj_close; // Use adjusted close
                    }
                } catch (...) {
                    // Use regular close if adj_close parsing fails
                }
            }
            
            // Validate data
            if (!is_valid_price(open) || !is_valid_price(high) || 
                !is_valid_price(low) || !is_valid_price(close) || 
                !is_valid_volume(volume)) {
                
                if (config_.skip_invalid_rows) {
                    skipped_count++;
                    continue;
                } else {
                    std::cerr << "Error: Invalid price/volume data at line " << line_number << std::endl;
                    return false;
                }
            }
            
            // Basic OHLC validation
            if (high < std::max({open, low, close}) || low > std::min({open, high, close})) {
                if (config_.skip_invalid_rows) {
                    skipped_count++;
                    continue;
                } else {
                    std::cerr << "Error: Invalid OHLC relationship at line " << line_number << std::endl;
                    return false;
                }
            }
            
            // Create candlestick and add to time series
            MarketData::Candlestick candle(timestamp, open, high, low, close, volume);
            ts.add_candle(candle);
            loaded_count++;
            
        } catch (const std::exception& e) {
            if (config_.skip_invalid_rows) {
                skipped_count++;
                continue;
            } else {
                std::cerr << "Error parsing line " << line_number << ": " << e.what() << std::endl;
                return false;
            }
        }
    }
    
    std::cout << "Loaded " << loaded_count << " records";
    if (skipped_count > 0) {
        std::cout << " (skipped " << skipped_count << " invalid records)";
    }
    std::cout << " from " << filename << std::endl;
    
    return loaded_count > 0;
}

bool CSVLoader::load_yahoo_finance_csv(const std::string& filename, MarketData::TimeSeries& ts) {
    // Yahoo Finance format: Date,Open,High,Low,Close,Adj Close,Volume
    Config yahoo_config;
    yahoo_config.date_col = 0;
    yahoo_config.open_col = 1;
    yahoo_config.high_col = 2;
    yahoo_config.low_col = 3;
    yahoo_config.close_col = 4;
    yahoo_config.adj_close_col = 5;
    yahoo_config.volume_col = 6;
    yahoo_config.has_header = true;
    yahoo_config.delimiter = ',';
    
    Config old_config = config_;
    config_ = yahoo_config;
    
    bool result = load_from_file(filename, ts);
    
    config_ = old_config; // Restore original config
    return result;
}

std::chrono::system_clock::time_point CSVLoader::parse_date(const std::string& date_str) const {
    std::tm tm = {};
    std::istringstream ss(date_str);
    
    // Try to parse YYYY-MM-DD format
    if (sscanf(date_str.c_str(), "%d-%d-%d", &tm.tm_year, &tm.tm_mon, &tm.tm_mday) == 3) {
        tm.tm_year -= 1900; // Years since 1900
        tm.tm_mon -= 1;     // Months since January (0-11)
        tm.tm_hour = 0;
        tm.tm_min = 0;
        tm.tm_sec = 0;
        
        auto time_t = std::mktime(&tm);
        return std::chrono::system_clock::from_time_t(time_t);
    }
    
    // If parsing fails, return current time (fallback)
    return std::chrono::system_clock::now();
}

std::vector<std::string> CSVLoader::split_line(const std::string& line, char delimiter) const {
    std::vector<std::string> fields;
    std::istringstream iss(line);
    std::string field;
    
    while (std::getline(iss, field, delimiter)) {
        // Trim whitespace
        field.erase(0, field.find_first_not_of(" \t\r\n"));
        field.erase(field.find_last_not_of(" \t\r\n") + 1);
        fields.push_back(field);
    }
    
    return fields;
}

bool CSVLoader::is_valid_price(double price) const {
    return price > 0.0 && price < 1000000.0 && std::isfinite(price);
}

bool CSVLoader::is_valid_volume(double volume) const {
    return volume >= 0.0 && volume < 1e12 && std::isfinite(volume);
}

bool CSVLoader::validate_data(const MarketData::TimeSeries& ts) const {
    if (ts.empty()) {
        std::cerr << "Error: No data loaded" << std::endl;
        return false;
    }
    
    if (ts.size() < 100) {
        std::cerr << "Warning: Limited data (" << ts.size() << " records). "
                  << "Consider using more data for better results." << std::endl;
    }
    
    return true;
}

// YahooFinanceLoader implementation
std::string YahooFinanceLoader::get_download_instructions() const {
    std::ostringstream instructions;
    instructions << "\n=== Yahoo Finance Data Download Instructions ===" << std::endl;
    instructions << "1. Go to: https://finance.yahoo.com/quote/" << config_.symbol << "/history" << std::endl;
    instructions << "2. Set date range: " << config_.start_date << " to " << config_.end_date << std::endl;
    instructions << "3. Click 'Download' to get CSV file" << std::endl;
    instructions << "4. Save as: " << config_.symbol << "_data.csv" << std::endl;
    instructions << "5. Place file in the 'data' folder" << std::endl;
    instructions << "\nAlternatively, use this URL:" << std::endl;
    instructions << get_yahoo_finance_url() << std::endl;
    
    return instructions.str();
}

std::string YahooFinanceLoader::get_yahoo_finance_url() const {
    // Convert dates to Unix timestamps (approximate)
    // This is a simplified implementation
    std::ostringstream url;
    url << "https://query1.finance.yahoo.com/v7/finance/download/" << config_.symbol;
    url << "?period1=1514764800"; // 2018-01-01 (approximate)
    url << "&period2=1735689600"; // 2025-01-01 (approximate)
    url << "&interval=1d&events=history";
    
    return url.str();
}

bool YahooFinanceLoader::load_if_exists(const std::string& filename, MarketData::TimeSeries& ts) {
    CSVLoader loader;
    return loader.load_yahoo_finance_csv(filename, ts);
}

// DataValidator implementation
DataValidator::Statistics DataValidator::analyze_data(const MarketData::TimeSeries& ts) {
    Statistics stats;
    
    if (ts.empty()) {
        stats.issues.push_back("No data available");
        return stats;
    }
    
    stats.total_records = ts.size();
    stats.valid_records = ts.size(); // Assume all loaded data is valid
    
    // Analyze prices
    auto closes = ts.closes();
    if (!closes.empty()) {
        stats.min_price = *std::min_element(closes.begin(), closes.end());
        stats.max_price = *std::max_element(closes.begin(), closes.end());
        stats.avg_price = std::accumulate(closes.begin(), closes.end(), 0.0) / closes.size();
    }
    
    // Analyze volumes
    auto volumes = ts.volumes();
    if (!volumes.empty()) {
        stats.min_volume = *std::min_element(volumes.begin(), volumes.end());
        stats.max_volume = *std::max_element(volumes.begin(), volumes.end());
        stats.avg_volume = std::accumulate(volumes.begin(), volumes.end(), 0.0) / volumes.size();
    }
    
    // Date range
    if (ts.size() > 0) {
        stats.start_date = ts[0].timestamp;
        stats.end_date = ts[ts.size() - 1].timestamp;
    }
    
    // Data quality checks
    if (ts.size() < 100) {
        stats.issues.push_back("Limited data points (< 100)");
    }
    
    if (ts.size() < 252 * 2) { // Less than 2 years of daily data
        stats.issues.push_back("Limited historical data (< 2 years)");
    }
    
    return stats;
}

void DataValidator::print_statistics(const Statistics& stats) {
    std::cout << "\n=== Data Statistics ===" << std::endl;
    std::cout << "Total Records: " << stats.total_records << std::endl;
    std::cout << "Valid Records: " << stats.valid_records << std::endl;
    
    if (stats.total_records > 0) {
        std::cout << "Price Range: $" << std::fixed << std::setprecision(2) 
                  << stats.min_price << " - $" << stats.max_price << std::endl;
        std::cout << "Average Price: $" << stats.avg_price << std::endl;
        std::cout << "Average Volume: " << std::fixed << std::setprecision(0) 
                  << stats.avg_volume << std::endl;
        
        // Date range
        auto start_time_t = std::chrono::system_clock::to_time_t(stats.start_date);
        auto end_time_t = std::chrono::system_clock::to_time_t(stats.end_date);
        std::cout << "Date Range: " << std::put_time(std::localtime(&start_time_t), "%Y-%m-%d")
                  << " to " << std::put_time(std::localtime(&end_time_t), "%Y-%m-%d") << std::endl;
    }
    
    if (!stats.issues.empty()) {
        std::cout << "\nData Quality Issues:" << std::endl;
        for (const auto& issue : stats.issues) {
            std::cout << "- " << issue << std::endl;
        }
    }
    std::cout << "=========================" << std::endl;
}

bool DataValidator::is_data_suitable_for_trading(const Statistics& stats) {
    return stats.total_records >= 100 && stats.issues.empty();
}

} // namespace DataLoader