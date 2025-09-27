#include "backtesting/fitness_evaluator.h"
#include <algorithm>
#include <numeric>
#include <cmath>
#include <limits>

namespace Fitness {

// Portfolio implementation
bool Portfolio::open_long(double price, double quantity, size_t time) {
    if (current_position_.is_active()) {
        return false; // Already have position
    }
    
    double cost = price * quantity;
    if (cost > current_capital_) {
        return false; // Not enough capital
    }
    
    current_position_ = Position(Position::LONG, price, quantity, time);
    current_capital_ -= cost;
    return true;
}

bool Portfolio::open_short(double price, double quantity, size_t time) {
    if (current_position_.is_active()) {
        return false; // Already have position
    }
    
    current_position_ = Position(Position::SHORT, price, quantity, time);
    current_capital_ += price * quantity; // Receive cash from short sale
    return true;
}

bool Portfolio::close_position(double price, size_t time) {
    if (!current_position_.is_active()) {
        return false; // No position to close
    }
    
    // Create trade record
    Trade trade(current_position_.type, current_position_.entry_price, price,
                current_position_.quantity, current_position_.entry_time, time);
    
    // Update capital
    if (current_position_.type == Position::LONG) {
        current_capital_ += price * current_position_.quantity;
    } else { // SHORT
        current_capital_ -= price * current_position_.quantity;
    }
    
    record_trade(trade);
    current_position_.close();
    return true;
}

void Portfolio::update_equity(double current_price) {
    double equity = current_capital_;
    
    if (current_position_.is_active()) {
        if (current_position_.type == Position::LONG) {
            equity += current_price * current_position_.quantity;
        } else { // SHORT
            equity += (2 * current_position_.entry_price - current_price) * current_position_.quantity;
        }
    }
    
    equity_curve_.push_back(equity);
    max_capital_ = std::max(max_capital_, equity);
    
    // Calculate return
    if (!equity_curve_.empty() && equity_curve_.size() > 1) {
        double prev_equity = equity_curve_[equity_curve_.size() - 2];
        if (prev_equity > 0) {
            double return_val = (equity - prev_equity) / prev_equity;
            returns_.push_back(return_val);
        }
    }
}

double Portfolio::total_return() const {
    if (equity_curve_.empty()) return 0.0;
    return equity_curve_.back() - initial_capital_;
}

double Portfolio::total_return_pct() const {
    return total_return() / initial_capital_;
}

double Portfolio::sharpe_ratio() const {
    if (returns_.size() < 2) return 0.0;
    
    double mean_return = std::accumulate(returns_.begin(), returns_.end(), 0.0) / returns_.size();
    
    double variance = 0.0;
    for (double ret : returns_) {
        double diff = ret - mean_return;
        variance += diff * diff;
    }
    variance /= (returns_.size() - 1);
    
    double std_dev = std::sqrt(variance);
    if (std_dev == 0.0) return 0.0;
    
    // Annualized Sharpe ratio (assuming daily data)
    return (mean_return * 252) / (std_dev * std::sqrt(252));
}

double Portfolio::sortino_ratio() const {
    if (returns_.empty()) return 0.0;
    
    double mean_return = std::accumulate(returns_.begin(), returns_.end(), 0.0) / returns_.size();
    
    // Calculate downside deviation
    double downside_variance = 0.0;
    size_t negative_count = 0;
    
    for (double ret : returns_) {
        if (ret < 0) {
            downside_variance += ret * ret;
            negative_count++;
        }
    }
    
    if (negative_count == 0) return std::numeric_limits<double>::max();
    
    downside_variance /= negative_count;
    double downside_dev = std::sqrt(downside_variance);
    
    if (downside_dev == 0.0) return 0.0;
    
    return (mean_return * 252) / (downside_dev * std::sqrt(252));
}

double Portfolio::max_drawdown() const {
    if (equity_curve_.size() < 2) return 0.0;
    
    double max_dd = 0.0;
    double peak = equity_curve_[0];
    
    for (size_t i = 1; i < equity_curve_.size(); ++i) {
        if (equity_curve_[i] > peak) {
            peak = equity_curve_[i];
        } else {
            double drawdown = peak - equity_curve_[i];
            max_dd = std::max(max_dd, drawdown);
        }
    }
    
    return max_dd;
}

double Portfolio::max_drawdown_pct() const {
    if (equity_curve_.size() < 2) return 0.0;
    
    double max_dd_pct = 0.0;
    double peak = equity_curve_[0];
    
    for (size_t i = 1; i < equity_curve_.size(); ++i) {
        if (equity_curve_[i] > peak) {
            peak = equity_curve_[i];
        } else if (peak > 0) {
            double dd_pct = (peak - equity_curve_[i]) / peak;
            max_dd_pct = std::max(max_dd_pct, dd_pct);
        }
    }
    
    return max_dd_pct;
}

double Portfolio::calmar_ratio() const {
    double max_dd = max_drawdown_pct();
    if (max_dd == 0.0) return std::numeric_limits<double>::max();
    
    double annual_return = total_return_pct() * 252 / equity_curve_.size();
    return annual_return / max_dd;
}

double Portfolio::win_rate() const {
    if (trade_history_.empty()) return 0.0;
    
    size_t wins = num_wins();
    return static_cast<double>(wins) / trade_history_.size();
}

double Portfolio::profit_factor() const {
    double gross_profit = 0.0;
    double gross_loss = 0.0;
    
    for (const auto& trade : trade_history_) {
        if (trade.is_profitable()) {
            gross_profit += trade.pnl;
        } else {
            gross_loss += std::abs(trade.pnl);
        }
    }
    
    if (gross_loss == 0.0) {
        return gross_profit > 0 ? std::numeric_limits<double>::max() : 1.0;
    }
    
    return gross_profit / gross_loss;
}

double Portfolio::average_trade() const {
    if (trade_history_.empty()) return 0.0;
    
    double total_pnl = 0.0;
    for (const auto& trade : trade_history_) {
        total_pnl += trade.pnl;
    }
    
    return total_pnl / trade_history_.size();
}

double Portfolio::average_win() const {
    double total_wins = 0.0;
    size_t win_count = 0;
    
    for (const auto& trade : trade_history_) {
        if (trade.is_profitable()) {
            total_wins += trade.pnl;
            win_count++;
        }
    }
    
    return win_count > 0 ? total_wins / win_count : 0.0;
}

double Portfolio::average_loss() const {
    double total_losses = 0.0;
    size_t loss_count = 0;
    
    for (const auto& trade : trade_history_) {
        if (!trade.is_profitable()) {
            total_losses += std::abs(trade.pnl);
            loss_count++;
        }
    }
    
    return loss_count > 0 ? -total_losses / loss_count : 0.0;
}

size_t Portfolio::num_wins() const {
    return std::count_if(trade_history_.begin(), trade_history_.end(),
                        [](const Trade& t) { return t.is_profitable(); });
}

size_t Portfolio::num_losses() const {
    return trade_history_.size() - num_wins();
}

double Portfolio::largest_win() const {
    if (trade_history_.empty()) return 0.0;
    
    auto max_it = std::max_element(trade_history_.begin(), trade_history_.end(),
                                  [](const Trade& a, const Trade& b) {
                                      return a.pnl < b.pnl;
                                  });
    return max_it->pnl;
}

double Portfolio::largest_loss() const {
    if (trade_history_.empty()) return 0.0;
    
    auto min_it = std::min_element(trade_history_.begin(), trade_history_.end(),
                                  [](const Trade& a, const Trade& b) {
                                      return a.pnl < b.pnl;
                                  });
    return min_it->pnl;
}

double Portfolio::average_trade_duration() const {
    if (trade_history_.empty()) return 0.0;
    
    double total_duration = 0.0;
    for (const auto& trade : trade_history_) {
        total_duration += trade.duration();
    }
    
    return total_duration / trade_history_.size();
}

double Portfolio::volatility() const {
    if (returns_.size() < 2) return 0.0;
    
    double mean_return = std::accumulate(returns_.begin(), returns_.end(), 0.0) / returns_.size();
    
    double variance = 0.0;
    for (double ret : returns_) {
        double diff = ret - mean_return;
        variance += diff * diff;
    }
    variance /= (returns_.size() - 1);
    
    // Annualized volatility
    return std::sqrt(variance * 252);
}

void Portfolio::reset() {
    current_capital_ = initial_capital_;
    max_capital_ = initial_capital_;
    current_position_.close();
    trade_history_.clear();
    equity_curve_.clear();
    returns_.clear();
}

void Portfolio::record_trade(const Trade& trade) {
    trade_history_.push_back(trade);
    update_statistics();
}

void Portfolio::update_statistics() {
    // This method can be used for real-time statistics updates
    // Currently, statistics are calculated on-demand
}

// StrategySimulator implementation
Portfolio StrategySimulator::simulate(const VGP::Individual& individual,
                                     const MarketData::TimeSeries& data,
                                     const VGP::EvaluationContext& context) {
    portfolio_.reset();
    
    // Generate signals for the entire time series
    auto signals = individual.generate_signals(context, data.size());
    
    // Process signals
    process_signals(signals, data);
    
    return portfolio_;
}

void StrategySimulator::process_signals(const std::vector<int>& signals,
                                       const MarketData::TimeSeries& data) {
    for (size_t i = 1; i < signals.size() && i < data.size(); ++i) {
        int signal = signals[i];
        double current_price = data[i].close;
        
        portfolio_.update_equity(current_price);
        
        const Position& position = portfolio_.get_position();
        
        // Check if we should close existing position
        if (position.is_active()) {
            bool should_close = should_close_position(position, current_price, i, signal);
            
            if (should_close) {
                // Apply both slippage AND transaction costs on exit
                double exit_price = current_price * (1.0 - config_.slippage - config_.transaction_cost);
                if (position.type == Position::SHORT) {
                    exit_price = current_price * (1.0 + config_.slippage + config_.transaction_cost);
                }
                
                portfolio_.close_position(exit_price, i);
            }
        }
        
        // Check if we should open new position
        if (!portfolio_.get_position().is_active()) {
            double available_capital = portfolio_.get_capital();
            
            if (signal == 1 && std::abs(signals[i]) > config_.signal_threshold) {
                // Buy signal
                double position_size = calculate_position_size(current_price, available_capital);
                if (position_size > 0) {
                    double entry_price = current_price * (1.0 + config_.slippage + config_.transaction_cost);
                    portfolio_.open_long(entry_price, position_size / entry_price, i);
                }
            } else if (signal == -1 && config_.allow_short_selling && 
                      std::abs(signals[i]) > config_.signal_threshold) {
                // Sell signal
                double position_size = calculate_position_size(current_price, available_capital);
                if (position_size > 0) {
                    double entry_price = current_price * (1.0 - config_.slippage - config_.transaction_cost);
                    portfolio_.open_short(entry_price, position_size / entry_price, i);
                }
            }
        }
    }
    
    // Close any remaining position at the end
    if (portfolio_.get_position().is_active() && !data.empty()) {
        double final_price = data.latest().close;
        portfolio_.close_position(final_price, data.size() - 1);
    }
}

double StrategySimulator::calculate_position_size(double price, double available_capital) {
    // Use configurable position sizing
    double max_position_value = available_capital * config_.position_size_pct; 
    double shares = max_position_value / price;
    
    // Don't allow positions smaller than $100 or larger than 50% of capital
    double min_position = 100.0;
    double max_capital_pct = 0.50;
    
    if (max_position_value < min_position) {
        return 0.0; // Skip trade if too small
    }
    
    // Cap at 50% of available capital
    return std::min(max_position_value, available_capital * max_capital_pct);
}

bool StrategySimulator::should_close_position(const Position& position, double current_price,
                                             size_t current_time, int signal) {
    // Opposite signal
    if ((position.type == Position::LONG && signal == -1) ||
        (position.type == Position::SHORT && signal == 1)) {
        return true;
    }
    
    // Minimum holding period
    if (current_time - position.entry_time < config_.min_holding_period) {
        return false;
    }
    
    // Maximum holding period
    if (current_time - position.entry_time >= config_.max_holding_period) {
        return true;
    }
    
    // Stop loss
    if (config_.use_stop_loss) {
        double loss_pct = 0.0;
        if (position.type == Position::LONG) {
            loss_pct = (position.entry_price - current_price) / position.entry_price;
        } else {
            loss_pct = (current_price - position.entry_price) / position.entry_price;
        }
        
        if (loss_pct >= config_.stop_loss_pct) {
            return true;
        }
    }
    
    // Take profit
    if (config_.use_take_profit) {
        double profit_pct = 0.0;
        if (position.type == Position::LONG) {
            profit_pct = (current_price - position.entry_price) / position.entry_price;
        } else {
            profit_pct = (position.entry_price - current_price) / position.entry_price;
        }
        
        if (profit_pct >= config_.take_profit_pct) {
            return true;
        }
    }
    
    return false;
}

// FitnessEvaluator implementation
double FitnessEvaluator::evaluate(const VGP::Individual& individual,
                                 const MarketData::TimeSeries& data) {
    // Build evaluation context
    VGP::FeatureBuilder feature_builder;
    feature_builder.add_sma(10);
    feature_builder.add_sma(50);
    feature_builder.add_ema(12);
    feature_builder.add_ema(26);
    feature_builder.add_rsi(14);
    feature_builder.add_macd();
    feature_builder.add_momentum_features();
    feature_builder.add_volume_features();
    
    VGP::EvaluationContext context = feature_builder.build_context(data);
    
    // Simulate strategy
    Portfolio portfolio = simulator_.simulate(individual, data, context);
    
    // Calculate component fitness scores
    double return_score = return_fitness(portfolio);
    double sharpe_score = sharpe_fitness(portfolio);
    double drawdown_score = drawdown_fitness(portfolio);
    double stability_score = stability_fitness(portfolio);
    
    // Calculate penalties
    double freq_penalty = trade_frequency_penalty(portfolio, data.size());
    double complexity_penalty_score = complexity_penalty(individual);
    
    // Combine scores using weights
    double total_fitness = 
        return_score * weights_.return_weight +
        sharpe_score * weights_.sharpe_weight +
        drawdown_score * weights_.drawdown_weight +
        stability_score * weights_.stability_weight -
        freq_penalty * weights_.trade_frequency_penalty -
        complexity_penalty_score * weights_.complexity_penalty;
    
    // Ensure fitness is non-negative
    return std::max(0.0, total_fitness);
}

double FitnessEvaluator::return_fitness(const Portfolio& portfolio) {
    double total_return = portfolio.total_return_pct();
    return normalize_return(total_return);
}

double FitnessEvaluator::sharpe_fitness(const Portfolio& portfolio) {
    double sharpe = portfolio.sharpe_ratio();
    return normalize_sharpe(sharpe);
}

double FitnessEvaluator::drawdown_fitness(const Portfolio& portfolio) {
    double max_dd = portfolio.max_drawdown_pct();
    return normalize_drawdown(max_dd);
}

double FitnessEvaluator::stability_fitness(const Portfolio& portfolio) {
    // Measure stability based on volatility and consistency
    double vol = portfolio.volatility();
    double returns_consistency = 0.0;
    
    const auto& returns = portfolio.get_returns();
    if (returns.size() > 1) {
        // Calculate stability as inverse of return volatility
        double mean_return = std::accumulate(returns.begin(), returns.end(), 0.0) / returns.size();
        double variance = 0.0;
        
        for (double ret : returns) {
            double diff = ret - mean_return;
            variance += diff * diff;
        }
        variance /= (returns.size() - 1);
        
        returns_consistency = 1.0 / (1.0 + std::sqrt(variance));
    }
    
    double vol_score = 1.0 / (1.0 + vol);
    
    return (vol_score + returns_consistency) / 2.0;
}

double FitnessEvaluator::trade_frequency_penalty(const Portfolio& portfolio, size_t data_length) {
    if (data_length == 0) return 0.0;
    
    double trade_frequency = static_cast<double>(portfolio.num_trades()) / data_length;
    
    // Penalize excessive trading (> 10% of bars)
    if (trade_frequency > 0.1) {
        return (trade_frequency - 0.1) * 10.0;
    }
    
    // Penalize too little trading (< 0.5% of bars)
    if (trade_frequency < 0.005) {
        return (0.005 - trade_frequency) * 100.0;
    }
    
    return 0.0;
}

double FitnessEvaluator::complexity_penalty(const VGP::Individual& individual) {
    // Penalize overly complex strategies
    size_t num_operations = 0;
    
    const auto& chromosome = individual.get_chromosome();
    for (const auto& gene : chromosome) {
        if (gene.type == VGP::GeneType::OPERATION) {
            num_operations++;
        }
    }
    
    // Penalty for too many operations
    if (num_operations > 20) {
        return static_cast<double>(num_operations - 20) * 0.01;
    }
    
    return 0.0;
}

std::vector<double> FitnessEvaluator::evaluate_objectives(const VGP::Individual& individual,
                                                         const MarketData::TimeSeries& data) {
    // Build evaluation context
    VGP::FeatureBuilder feature_builder;
    feature_builder.add_sma(10);
    feature_builder.add_sma(50);
    feature_builder.add_ema(12);
    feature_builder.add_ema(26);
    feature_builder.add_rsi(14);
    feature_builder.add_macd();
    feature_builder.add_momentum_features();
    feature_builder.add_volume_features();
    
    VGP::EvaluationContext context = feature_builder.build_context(data);
    
    // Simulate strategy
    Portfolio portfolio = simulator_.simulate(individual, data, context);
    
    // Return individual objective scores
    return {
        return_fitness(portfolio),
        sharpe_fitness(portfolio),
        drawdown_fitness(portfolio),
        stability_fitness(portfolio)
    };
}

double FitnessEvaluator::normalize_return(double return_val) {
    // Normalize returns to [0, 1] range
    // Assumes reasonable returns are between -50% and +200%
    double clamped = std::max(-0.5, std::min(2.0, return_val));
    return (clamped + 0.5) / 2.5;
}

double FitnessEvaluator::normalize_sharpe(double sharpe) {
    // Normalize Sharpe ratio to [0, 1] range
    // Assumes reasonable Sharpe ratios are between -2 and +4
    double clamped = std::max(-2.0, std::min(4.0, sharpe));
    return (clamped + 2.0) / 6.0;
}

double FitnessEvaluator::normalize_drawdown(double drawdown) {
    // Invert and normalize drawdown (lower is better)
    // Assumes max acceptable drawdown is 50%
    double clamped = std::min(0.5, drawdown);
    return 1.0 - (clamped / 0.5);
}

double FitnessEvaluator::calculate_risk_adjusted_return(const Portfolio& portfolio) {
    double total_return = portfolio.total_return_pct();
    double max_dd = portfolio.max_drawdown_pct();
    
    if (max_dd == 0.0) {
        return total_return > 0 ? 1000.0 : 0.0;
    }
    
    return total_return / max_dd;
}

// FitnessFunctionFactory implementation
std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
FitnessFunctionFactory::create_return_maximizer() {
    FitnessEvaluator::Weights weights;
    weights.return_weight = 1.0;
    weights.sharpe_weight = 0.0;
    weights.drawdown_weight = 0.0;
    weights.stability_weight = 0.0;
    
    return create_custom(weights);
}

std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
FitnessFunctionFactory::create_sharpe_maximizer() {
    FitnessEvaluator::Weights weights;
    weights.return_weight = 0.1;
    weights.sharpe_weight = 0.9;
    weights.drawdown_weight = 0.0;
    weights.stability_weight = 0.0;
    
    return create_custom(weights);
}

std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
FitnessFunctionFactory::create_risk_adjusted() {
    FitnessEvaluator::Weights weights;
    weights.return_weight = 0.3;
    weights.sharpe_weight = 0.4;
    weights.drawdown_weight = 0.3;
    weights.stability_weight = 0.0;
    
    return create_custom(weights);
}

std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
FitnessFunctionFactory::create_balanced() {
    FitnessEvaluator::Weights weights; // Use default weights
    return create_custom(weights);
}

std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
FitnessFunctionFactory::create_conservative() {
    FitnessEvaluator::Weights weights;
    weights.return_weight = 0.2;
    weights.sharpe_weight = 0.3;
    weights.drawdown_weight = 0.4;
    weights.stability_weight = 0.1;
    
    return create_custom(weights);
}

std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
FitnessFunctionFactory::create_aggressive() {
    FitnessEvaluator::Weights weights;
    weights.return_weight = 0.7;
    weights.sharpe_weight = 0.2;
    weights.drawdown_weight = 0.1;
    weights.stability_weight = 0.0;
    
    return create_custom(weights);
}

std::function<double(const VGP::Individual&, const MarketData::TimeSeries&)>
FitnessFunctionFactory::create_custom(const FitnessEvaluator::Weights& weights,
                                     const StrategySimulator::Config& sim_config) {
    return [weights, sim_config](const VGP::Individual& individual, 
                                const MarketData::TimeSeries& data) -> double {
        FitnessEvaluator evaluator(weights);
        evaluator.set_simulator_config(sim_config);
        return evaluator.evaluate(individual, data);
    };
}

} // namespace Fitness
