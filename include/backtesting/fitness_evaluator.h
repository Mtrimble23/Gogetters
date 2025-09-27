#ifndef FITNESS_EVALUATOR_H
#define FITNESS_EVALUATOR_H

#include <vector>
#include <functional>
#include <unordered_map>
#include "market_data/market_data.h"
#include "vgp/vgp_engine.h"

namespace Fitness {

/**
 * Represents a trading position
 */
struct Position {
    enum Type { LONG, SHORT, NONE };
    
    Type type = NONE;
    double entry_price = 0.0;
    double quantity = 0.0;
    size_t entry_time = 0;
    
    Position() = default;
    Position(Type t, double price, double qty, size_t time) 
        : type(t), entry_price(price), quantity(qty), entry_time(time) {}
    
    bool is_active() const { return type != NONE; }
    void close() { type = NONE; quantity = 0.0; }
};

/**
 * Trade execution record
 */
struct Trade {
    Position::Type type;
    double entry_price;
    double exit_price;
    double quantity;
    size_t entry_time;
    size_t exit_time;
    double pnl;
    double return_pct;
    
    Trade(Position::Type t, double entry, double exit, double qty, 
          size_t entry_t, size_t exit_t)
        : type(t), entry_price(entry), exit_price(exit), quantity(qty),
          entry_time(entry_t), exit_time(exit_t) {
        
        if (type == Position::LONG) {
            pnl = (exit_price - entry_price) * quantity;
            return_pct = (exit_price - entry_price) / entry_price;
        } else {
            pnl = (entry_price - exit_price) * quantity;
            return_pct = (entry_price - exit_price) / entry_price;
        }
    }
    
    bool is_profitable() const { return pnl > 0; }
    size_t duration() const { return exit_time - entry_time; }
};

/**
 * Portfolio state and performance metrics
 */
class Portfolio {
private:
    double initial_capital_;
    double current_capital_;
    double max_capital_;
    Position current_position_;
    std::vector<Trade> trade_history_;
    std::vector<double> equity_curve_;
    std::vector<double> returns_;
    
public:
    explicit Portfolio(double initial_capital = 10000.0) 
        : initial_capital_(initial_capital), current_capital_(initial_capital),
          max_capital_(initial_capital) {}
    
    // Position management
    bool open_long(double price, double quantity, size_t time);
    bool open_short(double price, double quantity, size_t time);
    bool close_position(double price, size_t time);
    void update_equity(double current_price);
    
    // Accessors
    const Position& get_position() const { return current_position_; }
    double get_capital() const { return current_capital_; }
    double get_initial_capital() const { return initial_capital_; }
    const std::vector<Trade>& get_trades() const { return trade_history_; }
    const std::vector<double>& get_equity_curve() const { return equity_curve_; }
    const std::vector<double>& get_returns() const { return returns_; }
    
    // Performance metrics
    double total_return() const;
    double total_return_pct() const;
    double sharpe_ratio() const;
    double sortino_ratio() const;
    double max_drawdown() const;
    double max_drawdown_pct() const;
    double calmar_ratio() const;
    double win_rate() const;
    double profit_factor() const;
    double average_trade() const;
    double average_win() const;
    double average_loss() const;
    size_t num_trades() const { return trade_history_.size(); }
    size_t num_wins() const;
    size_t num_losses() const;
    double largest_win() const;
    double largest_loss() const;
    double average_trade_duration() const;
    double volatility() const;
    
    // Reset for new simulation
    void reset();
    
private:
    void record_trade(const Trade& trade);
    void update_statistics();
};

/**
 * Strategy simulator that executes VGP individuals on historical data
 */
class StrategySimulator {
public:
    struct Config {
        double initial_capital = 10000.0;
        double transaction_cost = 0.001; // 0.1% per trade
        double slippage = 0.0001; // 0.01% slippage
        double position_size_pct = 1.0; // Use 100% of capital
        double signal_threshold = 0.1; // Signal strength threshold
        bool allow_short_selling = true;
        size_t min_holding_period = 1; // Minimum bars to hold position
        size_t max_holding_period = 100; // Maximum bars to hold position
        double stop_loss_pct = 0.05; // 5% stop loss
        double take_profit_pct = 0.10; // 10% take profit
        bool use_stop_loss = false;
        bool use_take_profit = false;
    };
    
private:
    Config config_;
    Portfolio portfolio_;
    
public:
    explicit StrategySimulator(const Config& config) 
        : config_(config), portfolio_(config.initial_capital) {}
    
    StrategySimulator() : config_(Config{}), portfolio_(10000.0) {}
    
    // Simulation
    Portfolio simulate(const VGP::Individual& individual, 
                      const MarketData::TimeSeries& data,
                      const VGP::EvaluationContext& context);
    
    // Configuration
    void set_config(const Config& config) { config_ = config; }
    const Config& get_config() const { return config_; }
    
private:
    void process_signals(const std::vector<int>& signals, 
                        const MarketData::TimeSeries& data);
    double calculate_position_size(double price, double available_capital);
    bool should_close_position(const Position& position, double current_price, 
                              size_t current_time, int signal);
};

/**
 * Multi-objective fitness evaluator
 */
class FitnessEvaluator {
public:
    struct Weights {
        double return_weight = 0.4;
        double sharpe_weight = 0.3;
        double drawdown_weight = 0.2;
        double stability_weight = 0.1;
        double trade_frequency_penalty = 0.0;
        double complexity_penalty = 0.0;
    };
    
private:
    Weights weights_;
    StrategySimulator simulator_;
    
public:
    explicit FitnessEvaluator(const Weights& weights) 
        : weights_(weights) {}
    
    FitnessEvaluator() : weights_(Weights{}) {}
    
    // Primary fitness function
    double evaluate(const VGP::Individual& individual, 
                   const MarketData::TimeSeries& data);
    
    // Component fitness functions
    double return_fitness(const Portfolio& portfolio);
    double sharpe_fitness(const Portfolio& portfolio);
    double drawdown_fitness(const Portfolio& portfolio);
    double stability_fitness(const Portfolio& portfolio);
    double trade_frequency_penalty(const Portfolio& portfolio, size_t data_length);
    double complexity_penalty(const VGP::Individual& individual);
    
    // Multi-objective fitness
    std::vector<double> evaluate_objectives(const VGP::Individual& individual,
                                           const MarketData::TimeSeries& data);
    
    // Configuration
    void set_weights(const Weights& weights) { weights_ = weights; }
    void set_simulator_config(const StrategySimulator::Config& config) {
        simulator_.set_config(config);
    }
    
    const Weights& get_weights() const { return weights_; }
    
private:
    double normalize_return(double return_val);
    double normalize_sharpe(double sharpe);
    double normalize_drawdown(double drawdown);
    double calculate_risk_adjusted_return(const Portfolio& portfolio);
};

/**
 * Fitness function factory for different trading objectives
 */
class FitnessFunctionFactory {
public:
    // Predefined fitness functions
    static std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
    create_return_maximizer();
    
    static std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
    create_sharpe_maximizer();
    
    static std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
    create_risk_adjusted();
    
    static std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
    create_balanced();
    
    static std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
    create_conservative();
    
    static std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
    create_aggressive();
    
    // Custom fitness function builder
    static std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
    create_custom(const FitnessEvaluator::Weights& weights,
                  const StrategySimulator::Config& sim_config = StrategySimulator::Config{});
};

} // namespace Fitness

#endif // FITNESS_EVALUATOR_H