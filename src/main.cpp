#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <chrono>
#include <iomanip>
#include <ctime>
#include <random>

#include "market_data/market_data.h"
#include "market_data/data_loader.h"
#include "technical_indicators/technical_indicators.h"
#include "vgp/vgp_engine.h"
#include "backtesting/fitness_evaluator.h"

class VGPTrader {
private:
    struct Config {
        // VGP parameters (reduced to prevent overfitting)
        size_t population_size = 50;   // Smaller population
        size_t chromosome_length = 30; // Simpler strategies
        size_t max_generations = 50;   // Fewer generations to reduce overfitting
        double mutation_rate = 0.15;   // Higher mutation for diversity
        double crossover_rate = 0.7;
        double elite_ratio = 0.1;
        
        // Configuration
        std::string data_file;
        size_t training_size = 1000;  // Default values, will be overridden in run_evolution
        size_t test_size = 200;
        
        // Trading parameters (more realistic)
        double initial_capital = 10000.0;
        double transaction_cost = 0.005;  // 0.5% per trade (more realistic)
        bool allow_short_selling = false;  // No short selling for simplicity
        double max_position_size = 0.1;   // Max 10% of portfolio per trade
        
        // Fitness weights (emphasize risk-adjusted returns)
        double return_weight = 0.3;
        double sharpe_weight = 0.4;        // Higher weight on risk-adjusted returns
        double drawdown_weight = 0.2;
        double stability_weight = 0.1;
        
        // Output
        std::string output_file = "results.txt";
        bool verbose = true;
        
        unsigned random_seed = 42;
    };
    
    Config config_;
    MarketData::TimeSeries data_;
    std::unique_ptr<VGP::EvolutionEngine> engine_;
    
public:
    VGPTrader() : data_("DEFAULT") {}
    
    bool load_config(const std::string& config_file) {
        // Simple configuration loading (in a real implementation, use JSON/XML)
        std::ifstream file(config_file);
        if (!file.is_open()) {
            std::cerr << "Warning: Could not open config file " << config_file 
                      << ". Using default configuration." << std::endl;
            return false;
        }
        
        std::string line;
        while (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string key, value;
            if (std::getline(iss, key, '=') && std::getline(iss, value)) {
                set_config_value(key, value);
            }
        }
        
        return true;
    }
    
    bool load_real_data(const std::string& symbol = "AAPL") {
        // Try to load real data from CSV file
        std::string csv_filename = "data/" + symbol + "_data.csv";
        
        DataLoader::CSVLoader loader;
        if (loader.load_yahoo_finance_csv(csv_filename, data_)) {
            std::cout << "Successfully loaded real data for " << symbol << std::endl;
            
            // Validate the data
            DataLoader::DataValidator validator;
            auto stats = validator.analyze_data(data_);
            validator.print_statistics(stats);
            
            if (!validator.is_data_suitable_for_trading(stats)) {
                std::cout << "Warning: Data may not be suitable for trading analysis" << std::endl;
            }
            
            return true;
        }
        
        // If loading fails, provide download instructions
        std::cout << "Could not load data from " << csv_filename << std::endl;
        
        DataLoader::YahooFinanceLoader::Config yahoo_config;
        yahoo_config.symbol = symbol;
        yahoo_config.start_date = "2017-01-01";
        yahoo_config.end_date = "2024-12-01";
        
        DataLoader::YahooFinanceLoader yahoo_loader(yahoo_config);
        std::cout << yahoo_loader.get_download_instructions() << std::endl;
        
        // Fall back to sample data
        std::cout << "\nFalling back to sample data generation..." << std::endl;
        return load_sample_data();
    }

    bool load_sample_data() {
        // Generate sample market data for demonstration
        std::mt19937 rng(config_.random_seed);
        std::normal_distribution<double> price_dist(0.0, 0.02); // 2% daily volatility
        std::normal_distribution<double> volume_dist(1000000, 200000);
        
        double base_price = 100.0;
        auto start_time = std::chrono::system_clock::now();
        
        for (size_t i = 0; i < config_.training_size + config_.test_size; ++i) {
            auto timestamp = start_time + std::chrono::hours(24 * i);
            
            // Simple random walk with trend
            double price_change = price_dist(rng);
            base_price *= (1.0 + price_change);
            
            // Create OHLC from base price
            double open = base_price;
            double high_factor = std::abs(std::normal_distribution<double>(1.01, 0.005)(rng));
            double low_factor = std::abs(std::normal_distribution<double>(0.99, 0.005)(rng));
            double high = open * high_factor;
            double low = open * low_factor;
            double close = base_price * (1.0 + price_change);
            double volume = std::abs(volume_dist(rng));
            
            MarketData::Candlestick candle(timestamp, open, high, low, close, volume);
            data_.add_candle(candle);
        }
        
        std::cout << "Generated " << data_.size() << " data points for symbol " 
                  << data_.symbol() << std::endl;
        return true;
    }
    
    bool load_data_from_csv(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Error: Could not open data file " << filename << std::endl;
            return false;
        }
        
        std::string line;
        std::getline(file, line); // Skip header
        
        while (std::getline(file, line)) {
            std::istringstream iss(line);
            std::string date_str, open_str, high_str, low_str, close_str, volume_str;
            
            if (std::getline(iss, date_str, ',') &&
                std::getline(iss, open_str, ',') &&
                std::getline(iss, high_str, ',') &&
                std::getline(iss, low_str, ',') &&
                std::getline(iss, close_str, ',') &&
                std::getline(iss, volume_str)) {
                
                try {
                    double open = std::stod(open_str);
                    double high = std::stod(high_str);
                    double low = std::stod(low_str);
                    double close = std::stod(close_str);
                    double volume = std::stod(volume_str);
                    
                    // Simple date parsing (you might want to use a proper date library)
                    auto timestamp = std::chrono::system_clock::now(); // Placeholder
                    
                    MarketData::Candlestick candle(timestamp, open, high, low, close, volume);
                    data_.add_candle(candle);
                    
                } catch (const std::exception& e) {
                    std::cerr << "Error parsing line: " << line << std::endl;
                    continue;
                }
            }
        }
        
        std::cout << "Loaded " << data_.size() << " data points from " << filename << std::endl;
        return !data_.empty();
    }
    
    void initialize_engine() {
        engine_ = std::make_unique<VGP::EvolutionEngine>(
            config_.population_size, 
            config_.chromosome_length, 
            config_.random_seed
        );
        
        // Configure evolution parameters
        engine_->set_max_generations(config_.max_generations);
        engine_->get_population().set_mutation_rate(config_.mutation_rate);
        engine_->get_population().set_crossover_rate(config_.crossover_rate);
        engine_->get_population().set_elite_ratio(config_.elite_ratio);
        
        // Set fitness function
        Fitness::FitnessEvaluator::Weights weights;
        weights.return_weight = config_.return_weight;
        weights.sharpe_weight = config_.sharpe_weight;
        weights.drawdown_weight = config_.drawdown_weight;
        weights.stability_weight = config_.stability_weight;
        
        Fitness::StrategySimulator::Config sim_config;
        sim_config.initial_capital = config_.initial_capital;
        sim_config.transaction_cost = config_.transaction_cost;
        sim_config.slippage = 0.002;  // 0.2% slippage (more realistic)
        sim_config.allow_short_selling = config_.allow_short_selling;
        sim_config.position_size_pct = 0.10;  // Only use 10% of capital per trade
        sim_config.signal_threshold = 0.3;    // Higher threshold for trades
        
        auto fitness_func = Fitness::FitnessFunctionFactory::create_custom(weights, sim_config);
        engine_->set_fitness_function(fitness_func);
        
        // Set progress callback
        if (config_.verbose) {
            engine_->progress_callback = [](size_t generation, const VGP::Individual& best, double avg_fitness) {
                std::cout << "Generation " << generation 
                          << " - Best fitness: " << std::fixed << std::setprecision(6) << best.get_fitness()
                          << " - Avg fitness: " << std::fixed << std::setprecision(6) << avg_fitness
                          << std::endl;
            };
        }
    }
    
    void run_evolution() {
        if (!engine_) {
            std::cerr << "Error: Engine not initialized!" << std::endl;
            return;
        }
        
        if (data_.size() < 100) {
            std::cerr << "Error: Not enough data for training!" << std::endl;
            return;
        }
        
        // Use 80-20 split based on actual data size
        double train_ratio = 0.8;
        size_t total_size = data_.size();
        size_t actual_training_size = static_cast<size_t>(total_size * train_ratio);
        size_t actual_test_size = total_size - actual_training_size;
        
        // Split data into training and test sets (chronological)
        MarketData::TimeSeries training_data(data_.symbol() + "_train");
        MarketData::TimeSeries test_data(data_.symbol() + "_test");
        
        // Training data: first 80% of the time series
        for (size_t i = 0; i < actual_training_size; ++i) {
            training_data.add_candle(data_[i]);
        }
        
        // Test data: last 20% of the time series (future unseen data)
        for (size_t i = actual_training_size; i < total_size; ++i) {
            test_data.add_candle(data_[i]);
        }
        
        std::cout << "\nStarting VGP evolution..." << std::endl;
        std::cout << "Total data points: " << total_size << std::endl;
        std::cout << "Training data: " << actual_training_size << " points (" << (train_ratio * 100) << "%)" << std::endl;
        std::cout << "Test data: " << actual_test_size << " points (" << ((1.0 - train_ratio) * 100) << "%)" << std::endl;
        std::cout << "Population size: " << config_.population_size << std::endl;
        std::cout << "Max generations: " << config_.max_generations << std::endl;
        std::cout << "---------------------------------------------------" << std::endl;
        
        auto start_time = std::chrono::high_resolution_clock::now();
        
        // Run evolution on training data
        engine_->evolve(training_data);
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::seconds>(end_time - start_time);
        
        std::cout << "\nEvolution completed in " << duration.count() << " seconds!" << std::endl;
        
        // Get best strategy
        VGP::Individual best_strategy = engine_->get_best_individual();
        std::cout << "Best strategy: " << best_strategy.to_string() << std::endl;
        
        // Evaluate on test data
        evaluate_strategy(best_strategy, training_data, test_data);
        
        // Save results
        save_results(best_strategy, training_data, test_data);
    }
    
    void evaluate_strategy(const VGP::Individual& strategy, 
                          const MarketData::TimeSeries& training_data,
                          const MarketData::TimeSeries& test_data) {
        
        std::cout << "\n=== Strategy Evaluation ===" << std::endl;
        
        // Evaluate on training data
        auto fitness_func = Fitness::FitnessFunctionFactory::create_balanced();
        double training_fitness = fitness_func(strategy, training_data);
        
        std::cout << "Training fitness: " << std::fixed << std::setprecision(6) << training_fitness << std::endl;
        
        // Detailed evaluation on test data
        Fitness::StrategySimulator simulator;
        Fitness::StrategySimulator::Config sim_config;
        sim_config.initial_capital = config_.initial_capital;
        sim_config.transaction_cost = config_.transaction_cost;
        sim_config.allow_short_selling = config_.allow_short_selling;
        simulator.set_config(sim_config);
        
        // Build feature context for test data
        VGP::FeatureBuilder feature_builder;
        feature_builder.add_sma(10);
        feature_builder.add_sma(50);
        feature_builder.add_ema(12);
        feature_builder.add_ema(26);
        feature_builder.add_rsi(14);
        feature_builder.add_macd();
        feature_builder.add_momentum_features();
        feature_builder.add_volume_features();
        
        VGP::EvaluationContext context = feature_builder.build_context(test_data);
        
        Fitness::Portfolio test_portfolio = simulator.simulate(strategy, test_data, context);
        
        std::cout << "\n--- Test Results ---" << std::endl;
        std::cout << "Total Return: " << std::fixed << std::setprecision(2) 
                  << test_portfolio.total_return_pct() * 100 << "%" << std::endl;
        std::cout << "Sharpe Ratio: " << std::fixed << std::setprecision(4) 
                  << test_portfolio.sharpe_ratio() << std::endl;
        std::cout << "Max Drawdown: " << std::fixed << std::setprecision(2) 
                  << test_portfolio.max_drawdown_pct() * 100 << "%" << std::endl;
        std::cout << "Win Rate: " << std::fixed << std::setprecision(2) 
                  << test_portfolio.win_rate() * 100 << "%" << std::endl;
        std::cout << "Number of Trades: " << test_portfolio.num_trades() << std::endl;
        std::cout << "Profit Factor: " << std::fixed << std::setprecision(4) 
                  << test_portfolio.profit_factor() << std::endl;
        std::cout << "Average Trade: $" << std::fixed << std::setprecision(2) 
                  << test_portfolio.average_trade() << std::endl;
    }
    
    void save_results(const VGP::Individual& best_strategy,
                     const MarketData::TimeSeries& training_data,
                     const MarketData::TimeSeries& test_data) {
        
        std::ofstream file(config_.output_file);
        if (!file.is_open()) {
            std::cerr << "Warning: Could not save results to " << config_.output_file << std::endl;
            return;
        }
        
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        
        file << "VGP Algorithmic Trading Results" << std::endl;
        file << "Generated on: " << std::ctime(&time_t) << std::endl;
        file << "==============================" << std::endl << std::endl;
        
        file << "Configuration:" << std::endl;
        file << "- Population size: " << config_.population_size << std::endl;
        file << "- Chromosome length: " << config_.chromosome_length << std::endl;
        file << "- Max generations: " << config_.max_generations << std::endl;
        file << "- Training data size: " << training_data.size() << std::endl;
        file << "- Test data size: " << test_data.size() << std::endl;
        file << std::endl;
        
        file << "Best Strategy: " << best_strategy.to_string() << std::endl;
        file << "Training Fitness: " << std::fixed << std::setprecision(6) << best_strategy.get_fitness() << std::endl;
        file << std::endl;
        
        // Evolution statistics
        const auto& best_fitness_history = engine_->get_best_fitness_history();
        const auto& avg_fitness_history = engine_->get_avg_fitness_history();
        
        file << "Evolution Progress:" << std::endl;
        for (size_t i = 0; i < best_fitness_history.size(); ++i) {
            file << "Gen " << i << ": Best=" << std::fixed << std::setprecision(6) 
                 << best_fitness_history[i] << ", Avg=" << avg_fitness_history[i] << std::endl;
        }
        
        file.close();
        std::cout << "\nResults saved to " << config_.output_file << std::endl;
    }
    
    void run(int argc, char* argv[]) {
        std::cout << "VGP Algorithmic Trader v1.0" << std::endl;
        std::cout << "============================" << std::endl;
        
        // Load configuration
        std::string config_file = "config.txt";
        if (argc > 1) {
            config_file = argv[1];
        }
        load_config(config_file);
        
        // Load data - prioritize real Apple stock data
        std::cout << "Loading market data..." << std::endl;
        bool data_loaded = load_real_data("AAPL");
        
        if (!data_loaded) {
            std::cout << "Failed to load real data. Generating sample data..." << std::endl;
            load_sample_data();
        }
        
        // Initialize and run evolution
        initialize_engine();
        run_evolution();
    }
    
private:
    void set_config_value(const std::string& key, const std::string& value) {
        // Trim whitespace
        std::string trimmed_key = key;
        std::string trimmed_value = value;
        trimmed_key.erase(0, trimmed_key.find_first_not_of(" \t"));
        trimmed_key.erase(trimmed_key.find_last_not_of(" \t") + 1);
        trimmed_value.erase(0, trimmed_value.find_first_not_of(" \t"));
        trimmed_value.erase(trimmed_value.find_last_not_of(" \t") + 1);
        
        // Set configuration values
        if (trimmed_key == "population_size") {
            config_.population_size = std::stoull(trimmed_value);
        } else if (trimmed_key == "chromosome_length") {
            config_.chromosome_length = std::stoull(trimmed_value);
        } else if (trimmed_key == "max_generations") {
            config_.max_generations = std::stoull(trimmed_value);
        } else if (trimmed_key == "mutation_rate") {
            config_.mutation_rate = std::stod(trimmed_value);
        } else if (trimmed_key == "crossover_rate") {
            config_.crossover_rate = std::stod(trimmed_value);
        } else if (trimmed_key == "data_file") {
            config_.data_file = trimmed_value;
        } else if (trimmed_key == "training_size") {
            config_.training_size = std::stoull(trimmed_value);
        } else if (trimmed_key == "test_size") {
            config_.test_size = std::stoull(trimmed_value);
        } else if (trimmed_key == "initial_capital") {
            config_.initial_capital = std::stod(trimmed_value);
        } else if (trimmed_key == "return_weight") {
            config_.return_weight = std::stod(trimmed_value);
        } else if (trimmed_key == "sharpe_weight") {
            config_.sharpe_weight = std::stod(trimmed_value);
        } else if (trimmed_key == "drawdown_weight") {
            config_.drawdown_weight = std::stod(trimmed_value);
        } else if (trimmed_key == "stability_weight") {
            config_.stability_weight = std::stod(trimmed_value);
        } else if (trimmed_key == "output_file") {
            config_.output_file = trimmed_value;
        } else if (trimmed_key == "verbose") {
            config_.verbose = (trimmed_value == "true" || trimmed_value == "1");
        } else if (trimmed_key == "random_seed") {
            config_.random_seed = std::stoul(trimmed_value);
        }
    }
};

int main(int argc, char* argv[]) {
    try {
        VGPTrader trader;
        trader.run(argc, argv);
        
        std::cout << "\nTrading strategy evolution completed successfully!" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}