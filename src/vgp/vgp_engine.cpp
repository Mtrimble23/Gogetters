#include "vgp/vgp_engine.h"
#include <algorithm>
#include <numeric>
#include <cmath>
#include <limits>
#include <sstream>
#include <iomanip>

namespace VGP {

// Individual implementation
double Individual::evaluate(const EvaluationContext& context) const {
    if (chromosome_.empty()) return 0.0;
    
    execution_stack_.clear();
    
    // Execute genes in order (vector-based GP)
    for (const auto& gene : chromosome_) {
        switch (gene.type) {
            case GeneType::CONSTANT:
                execution_stack_.push_back(gene.constant_value);
                break;
                
            case GeneType::TERMINAL:
                execution_stack_.push_back(context.get_feature(gene.terminal_name));
                break;
                
            case GeneType::OPERATION: {
                if (execution_stack_.size() >= static_cast<size_t>(gene.arity)) {
                    std::vector<double> args;
                    for (int i = 0; i < gene.arity; ++i) {
                        args.push_back(execution_stack_.back());
                        execution_stack_.pop_back();
                    }
                    std::reverse(args.begin(), args.end()); // Correct argument order
                    
                    double result = execute_operation(gene.operation, args);
                    execution_stack_.push_back(result);
                } else {
                    // Not enough arguments, push a default value
                    execution_stack_.push_back(0.0);
                }
                break;
            }
        }
    }
    
    return execution_stack_.empty() ? 0.0 : execution_stack_.back();
}

std::vector<double> Individual::evaluate_series(const EvaluationContext& context, size_t series_length) const {
    std::vector<double> results;
    results.reserve(series_length);
    
    for (size_t i = 0; i < series_length; ++i) {
        // Create context for this time point
        EvaluationContext point_context;
        
        for (const auto& feature_pair : context.feature_series) {
            const std::string& name = feature_pair.first;
            const std::vector<double>& series = feature_pair.second;
            
            if (i < series.size()) {
                point_context.add_feature(name, series[i]);
            } else {
                point_context.add_feature(name, 0.0);
            }
        }
        
        results.push_back(evaluate(point_context));
    }
    
    return results;
}

double Individual::generate_signal(const EvaluationContext& context) const {
    double raw_output = evaluate(context);
    
    // Normalize to [-1, 1] range using tanh
    return std::tanh(raw_output);
}

std::vector<int> Individual::generate_signals(const EvaluationContext& context, size_t length) const {
    auto raw_signals = evaluate_series(context, length);
    std::vector<int> signals;
    signals.reserve(length);
    
    for (double signal : raw_signals) {
        double normalized = std::tanh(signal);
        
        if (normalized > 0.1) {
            signals.push_back(1);  // Buy
        } else if (normalized < -0.1) {
            signals.push_back(-1); // Sell
        } else {
            signals.push_back(0);  // Hold
        }
    }
    
    return signals;
}

double Individual::execute_operation(OperationType op, const std::vector<double>& args) const {
    const double EPSILON = 1e-10;
    
    switch (op) {
        case OperationType::ADD:
            return args.size() >= 2 ? args[0] + args[1] : 0.0;
            
        case OperationType::SUBTRACT:
            return args.size() >= 2 ? args[0] - args[1] : 0.0;
            
        case OperationType::MULTIPLY:
            return args.size() >= 2 ? args[0] * args[1] : 0.0;
            
        case OperationType::DIVIDE:
            if (args.size() >= 2 && std::abs(args[1]) > EPSILON) {
                return args[0] / args[1];
            }
            return 1.0; // Protected division
            
        case OperationType::SIN:
            return args.size() >= 1 ? std::sin(args[0]) : 0.0;
            
        case OperationType::COS:
            return args.size() >= 1 ? std::cos(args[0]) : 0.0;
            
        case OperationType::TANH:
            return args.size() >= 1 ? std::tanh(args[0]) : 0.0;
            
        case OperationType::LOG:
            if (args.size() >= 1 && args[0] > EPSILON) {
                return std::log(args[0]);
            }
            return 0.0; // Protected log
            
        case OperationType::EXP:
            if (args.size() >= 1) {
                double exp_val = std::exp(std::min(args[0], 10.0)); // Prevent overflow
                return std::isfinite(exp_val) ? exp_val : 10.0;
            }
            return 1.0;
            
        case OperationType::ABS:
            return args.size() >= 1 ? std::abs(args[0]) : 0.0;
            
        case OperationType::SQRT:
            return args.size() >= 1 && args[0] >= 0 ? std::sqrt(args[0]) : 0.0;
            
        case OperationType::POWER:
            if (args.size() >= 2) {
                double base = args[0];
                double exp = std::min(std::max(args[1], -10.0), 10.0); // Limit exponent
                if (base == 0.0 && exp < 0) return 0.0; // Avoid division by zero
                double result = std::pow(std::abs(base), exp);
                return std::isfinite(result) ? result : 1.0;
            }
            return 1.0;
            
        case OperationType::MAX:
            return args.size() >= 2 ? std::max(args[0], args[1]) : 0.0;
            
        case OperationType::MIN:
            return args.size() >= 2 ? std::min(args[0], args[1]) : 0.0;
            
        case OperationType::IF_GREATER:
            if (args.size() >= 4) {
                return args[0] > args[1] ? args[2] : args[3];
            }
            return 0.0;
            
        case OperationType::IF_LESS:
            if (args.size() >= 4) {
                return args[0] < args[1] ? args[2] : args[3];
            }
            return 0.0;
            
        case OperationType::AND_OP:
            if (args.size() >= 2) {
                return (args[0] > 0 && args[1] > 0) ? 1.0 : 0.0;
            }
            return 0.0;
            
        case OperationType::OR_OP:
            if (args.size() >= 2) {
                return (args[0] > 0 || args[1] > 0) ? 1.0 : 0.0;
            }
            return 0.0;
            
        case OperationType::NOT_OP:
            return args.size() >= 1 ? (args[0] > 0 ? 0.0 : 1.0) : 0.0;
            
        default:
            return 0.0;
    }
}

void Individual::mutate(double mutation_rate, std::mt19937& rng) {
    std::uniform_real_distribution<double> prob_dist(0.0, 1.0);
    std::uniform_real_distribution<double> constant_dist(-10.0, 10.0);
    
    for (auto& gene : chromosome_) {
        if (prob_dist(rng) < mutation_rate) {
            switch (gene.type) {
                case GeneType::CONSTANT:
                    gene.constant_value += std::normal_distribution<double>(0.0, 1.0)(rng);
                    gene.constant_value = std::max(-100.0, std::min(100.0, gene.constant_value));
                    break;
                    
                case GeneType::OPERATION:
                    // Could mutate to different operation
                    break;
                    
                case GeneType::TERMINAL:
                    // Terminals don't typically mutate
                    break;
            }
        }
    }
    
    clear_fitness(); // Invalidate fitness after mutation
}

Individual Individual::crossover(const Individual& other, std::mt19937& rng) const {
    std::uniform_int_distribution<size_t> point_dist(1, std::min(chromosome_.size(), other.chromosome_.size()) - 1);
    size_t crossover_point = point_dist(rng);
    
    std::vector<Gene> child_genes;
    child_genes.reserve(chromosome_.size());
    
    // Copy first part from this individual
    for (size_t i = 0; i < crossover_point && i < chromosome_.size(); ++i) {
        child_genes.push_back(chromosome_[i]);
    }
    
    // Copy second part from other individual
    for (size_t i = crossover_point; i < other.chromosome_.size(); ++i) {
        child_genes.push_back(other.chromosome_[i]);
    }
    
    return Individual(child_genes);
}

void Individual::randomize(size_t length, std::mt19937& rng) {
    chromosome_.clear();
    chromosome_.reserve(length);
    
    // Simple randomization - would be improved with proper gene generation
    std::uniform_real_distribution<double> constant_dist(-10.0, 10.0);
    std::uniform_int_distribution<int> type_dist(0, 2);
    
    for (size_t i = 0; i < length; ++i) {
        int type = type_dist(rng);
        
        if (type == 0) {
            // Constant
            chromosome_.emplace_back(constant_dist(rng));
        } else if (type == 1) {
            // Operation
            chromosome_.emplace_back(OperationType::ADD, 2);
        } else {
            // Terminal (placeholder)
            chromosome_.emplace_back("close");
        }
    }
    
    clear_fitness();
}

std::string Individual::to_string() const {
    std::stringstream ss;
    ss << "Individual[" << chromosome_.size() << " genes, fitness=" 
       << std::fixed << std::setprecision(4) << fitness_ << "]";
    return ss.str();
}

// Population implementation
Population::Population(size_t pop_size, size_t chrom_length, unsigned seed)
    : population_size_(pop_size), chromosome_length_(chrom_length),
      mutation_rate_(0.1), crossover_rate_(0.8), elite_ratio_(0.1),
      rng_(seed), constant_min_(-10.0), constant_max_(10.0) {
    
    individuals_.reserve(population_size_);
    
    // Default operations
    available_operations_ = {
        OperationType::ADD, OperationType::SUBTRACT, OperationType::MULTIPLY, OperationType::DIVIDE,
        OperationType::SIN, OperationType::COS, OperationType::TANH,
        OperationType::MAX, OperationType::MIN
    };
    
    // Default terminals (will be set by feature builder)
    available_terminals_ = {"close", "volume", "high", "low", "open"};
}

void Population::initialize() {
    individuals_.clear();
    
    for (size_t i = 0; i < population_size_; ++i) {
        std::vector<Gene> chromosome;
        chromosome.reserve(chromosome_length_);
        
        for (size_t j = 0; j < chromosome_length_; ++j) {
            chromosome.push_back(generate_random_gene());
        }
        
        individuals_.emplace_back(chromosome);
    }
}

Gene Population::generate_random_gene() {
    std::uniform_int_distribution<int> type_dist(0, 2); // 0=operation, 1=constant, 2=terminal
    std::uniform_real_distribution<double> constant_dist(constant_min_, constant_max_);
    
    int type = type_dist(rng_);
    
    if (type == 0 && !available_operations_.empty()) {
        // Operation
        std::uniform_int_distribution<size_t> op_dist(0, available_operations_.size() - 1);
        OperationType op = available_operations_[op_dist(rng_)];
        
        int arity = 2; // Default arity
        switch (op) {
            case OperationType::SIN:
            case OperationType::COS:
            case OperationType::TANH:
            case OperationType::LOG:
            case OperationType::EXP:
            case OperationType::ABS:
            case OperationType::SQRT:
            case OperationType::NOT_OP:
                arity = 1;
                break;
            case OperationType::IF_GREATER:
            case OperationType::IF_LESS:
                arity = 4;
                break;
            default:
                arity = 2;
                break;
        }
        
        return Gene(op, arity);
    } else if (type == 1) {
        // Constant
        return Gene(constant_dist(rng_));
    } else {
        // Terminal
        if (!available_terminals_.empty()) {
            std::uniform_int_distribution<size_t> term_dist(0, available_terminals_.size() - 1);
            return Gene(available_terminals_[term_dist(rng_)]);
        } else {
            return Gene(0.0); // Fallback to constant
        }
    }
}

void Population::evaluate_fitness(const std::function<double(const Individual&)>& fitness_func) {
    for (auto& individual : individuals_) {
        if (!individual.is_fitness_evaluated()) {
            double fitness = fitness_func(individual);
            individual.set_fitness(fitness);
        }
    }
}

void Population::evolve() {
    sort_by_fitness();
    
    std::vector<Individual> new_population;
    new_population.reserve(population_size_);
    
    // Elitism - keep best individuals
    size_t elite_count = static_cast<size_t>(elite_ratio_ * population_size_);
    for (size_t i = 0; i < elite_count; ++i) {
        new_population.push_back(individuals_[i]);
    }
    
    // Generate new individuals through crossover and mutation
    std::uniform_real_distribution<double> prob_dist(0.0, 1.0);
    
    while (new_population.size() < population_size_) {
        Individual parent1 = tournament_selection();
        Individual parent2 = tournament_selection();
        
        Individual child = parent1;
        
        if (prob_dist(rng_) < crossover_rate_) {
            child = parent1.crossover(parent2, rng_);
        }
        
        child.mutate(mutation_rate_, rng_);
        new_population.push_back(child);
    }
    
    individuals_ = std::move(new_population);
}

void Population::sort_by_fitness() {
    std::sort(individuals_.begin(), individuals_.end(),
              [](const Individual& a, const Individual& b) {
                  return a.get_fitness() > b.get_fitness(); // Higher fitness is better
              });
}

Individual Population::tournament_selection(size_t tournament_size) {
    std::uniform_int_distribution<size_t> ind_dist(0, individuals_.size() - 1);
    
    Individual best = individuals_[ind_dist(rng_)];
    
    for (size_t i = 1; i < tournament_size; ++i) {
        Individual candidate = individuals_[ind_dist(rng_)];
        if (candidate.get_fitness() > best.get_fitness()) {
            best = candidate;
        }
    }
    
    return best;
}

double Population::get_average_fitness() const {
    if (individuals_.empty()) return 0.0;
    
    double sum = 0.0;
    for (const auto& individual : individuals_) {
        sum += individual.get_fitness();
    }
    return sum / individuals_.size();
}

double Population::get_best_fitness() const {
    if (individuals_.empty()) return 0.0;
    
    auto best_it = std::max_element(individuals_.begin(), individuals_.end(),
                                   [](const Individual& a, const Individual& b) {
                                       return a.get_fitness() < b.get_fitness();
                                   });
    return best_it->get_fitness();
}

double Population::get_worst_fitness() const {
    if (individuals_.empty()) return 0.0;
    
    auto worst_it = std::min_element(individuals_.begin(), individuals_.end(),
                                    [](const Individual& a, const Individual& b) {
                                        return a.get_fitness() < b.get_fitness();
                                    });
    return worst_it->get_fitness();
}

std::vector<double> Population::get_fitness_stats() const {
    std::vector<double> stats = {get_best_fitness(), get_worst_fitness(), get_average_fitness()};
    return stats;
}

// FeatureBuilder implementation
FeatureBuilder::FeatureBuilder() {
    // Initialize with basic price features
    add_price_features();
}

void FeatureBuilder::add_sma(int period) {
    indicators_.push_back(std::make_unique<TechnicalIndicators::SMA>(period));
    register_feature("SMA" + std::to_string(period));
}

void FeatureBuilder::add_ema(int period) {
    indicators_.push_back(std::make_unique<TechnicalIndicators::EMA>(period));
    register_feature("EMA" + std::to_string(period));
}

void FeatureBuilder::add_rsi(int period) {
    indicators_.push_back(std::make_unique<TechnicalIndicators::RSI>(period));
    register_feature("RSI" + std::to_string(period));
}

void FeatureBuilder::add_macd(int fast, int slow, int signal) {
    indicators_.push_back(std::make_unique<TechnicalIndicators::MACD>(fast, slow, signal));
    register_feature("MACD_" + std::to_string(fast) + "_" + std::to_string(slow));
}

void FeatureBuilder::add_bollinger_bands(int period, double std_dev) {
    indicators_.push_back(std::make_unique<TechnicalIndicators::BollingerBands>(period, std_dev));
    register_feature("BB_UPPER_" + std::to_string(period));
    register_feature("BB_LOWER_" + std::to_string(period));
    register_feature("BB_WIDTH_" + std::to_string(period));
}

void FeatureBuilder::add_atr(int period) {
    indicators_.push_back(std::make_unique<TechnicalIndicators::ATR>(period));
    register_feature("ATR" + std::to_string(period));
}

void FeatureBuilder::add_stochastic(int k_period, int d_period) {
    indicators_.push_back(std::make_unique<TechnicalIndicators::StochasticOscillator>(k_period, d_period));
    register_feature("STOCH_K_" + std::to_string(k_period));
    register_feature("STOCH_D_" + std::to_string(d_period));
}

void FeatureBuilder::add_obv() {
    indicators_.push_back(std::make_unique<TechnicalIndicators::OBV>());
    register_feature("OBV");
}

void FeatureBuilder::add_cmf(int period) {
    indicators_.push_back(std::make_unique<TechnicalIndicators::CMF>(period));
    register_feature("CMF" + std::to_string(period));
}

void FeatureBuilder::add_price_features() {
    register_feature("open");
    register_feature("high");
    register_feature("low");
    register_feature("close");
    register_feature("typical_price");
    register_feature("median_price");
    register_feature("weighted_close");
    register_feature("body_size");
    register_feature("upper_shadow");
    register_feature("lower_shadow");
    register_feature("is_bullish");
}

void FeatureBuilder::add_volume_features() {
    register_feature("volume");
    register_feature("volume_sma_ratio");
    register_feature("volume_weighted_price");
}

void FeatureBuilder::add_momentum_features() {
    register_feature("price_return");
    register_feature("log_return");
    register_feature("price_change");
    register_feature("percent_change");
    register_feature("price_velocity");
    register_feature("price_acceleration");
}

EvaluationContext FeatureBuilder::build_context(const MarketData::TimeSeries& ts, size_t window_size) const {
    EvaluationContext context;
    
    if (ts.size() < window_size) {
        return context; // Not enough data
    }
    
    // Build basic price features
    auto closes = ts.closes();
    auto opens = ts.opens();
    auto highs = ts.highs();
    auto lows = ts.lows();
    auto volumes = ts.volumes();
    
    context.add_feature_series("close", closes);
    context.add_feature_series("open", opens);
    context.add_feature_series("high", highs);
    context.add_feature_series("low", lows);
    context.add_feature_series("volume", volumes);
    
    // Calculate derived price features
    auto returns = ts.returns();
    auto log_returns = ts.log_returns();
    auto percent_changes = ts.percent_changes();
    auto velocity = ts.price_velocity();
    auto acceleration = ts.price_acceleration();
    
    context.add_feature_series("price_return", returns);
    context.add_feature_series("log_return", log_returns);
    context.add_feature_series("percent_change", percent_changes);
    context.add_feature_series("price_velocity", velocity);
    context.add_feature_series("price_acceleration", acceleration);
    
    // Calculate technical indicators
    for (const auto& indicator : indicators_) {
        auto indicator_values = indicator->calculate_series(ts);
        context.add_feature_series(indicator->name(), indicator_values);
    }
    
    // Add candlestick pattern features
    std::vector<double> typical_prices, median_prices, weighted_closes;
    std::vector<double> body_sizes, upper_shadows, lower_shadows, bullish_flags;
    
    for (size_t i = 0; i < ts.size(); ++i) {
        const auto& candle = ts[i];
        typical_prices.push_back(candle.typical_price());
        median_prices.push_back(candle.median_price());
        weighted_closes.push_back(candle.weighted_close());
        body_sizes.push_back(candle.body_size());
        upper_shadows.push_back(candle.upper_shadow());
        lower_shadows.push_back(candle.lower_shadow());
        bullish_flags.push_back(candle.is_bullish() ? 1.0 : -1.0);
    }
    
    context.add_feature_series("typical_price", typical_prices);
    context.add_feature_series("median_price", median_prices);
    context.add_feature_series("weighted_close", weighted_closes);
    context.add_feature_series("body_size", body_sizes);
    context.add_feature_series("upper_shadow", upper_shadows);
    context.add_feature_series("lower_shadow", lower_shadows);
    context.add_feature_series("is_bullish", bullish_flags);
    
    return context;
}

void FeatureBuilder::register_feature(const std::string& name) {
    feature_names_.push_back(name);
}

// EvolutionEngine implementation
EvolutionEngine::EvolutionEngine(size_t pop_size, size_t chrom_length, unsigned seed)
    : population_(pop_size, chrom_length, seed),
      max_generations_(100), target_fitness_(0.9), early_stopping_(true),
      stagnation_limit_(20), current_generation_(0) {
    
    // Configure feature builder with default features
    feature_builder_.add_sma(10);
    feature_builder_.add_sma(50);
    feature_builder_.add_ema(12);
    feature_builder_.add_ema(26);
    feature_builder_.add_rsi(14);
    feature_builder_.add_macd();
    feature_builder_.add_bollinger_bands();
    feature_builder_.add_atr();
    feature_builder_.add_momentum_features();
    feature_builder_.add_volume_features();
    
    // Set available terminals in population
    auto feature_names = feature_builder_.get_feature_names();
    for (const std::string& name : feature_names) {
        population_.add_terminal(name);
    }
}

void EvolutionEngine::evolve(const MarketData::TimeSeries& training_data) {
    // Initialize population
    population_.initialize();
    
    // Build feature context
    EvaluationContext context = feature_builder_.build_context(training_data);
    
    best_fitness_history_.clear();
    avg_fitness_history_.clear();
    current_generation_ = 0;
    
    for (size_t generation = 0; generation < max_generations_; ++generation) {
        current_generation_ = generation;
        
        // Evaluate fitness for all individuals
        population_.evaluate_fitness([this, &training_data](const Individual& individual) {
            return fitness_function_(individual, training_data);
        });
        
        // Update statistics
        update_statistics();
        
        // Check stopping criteria
        if (should_stop()) {
            break;
        }
        
        // Call progress callback if set
        if (progress_callback) {
            progress_callback(generation, population_.get_best(), population_.get_average_fitness());
        }
        
        // Evolve to next generation
        population_.evolve();
    }
    
    // Final evaluation
    population_.evaluate_fitness([this, &training_data](const Individual& individual) {
        return fitness_function_(individual, training_data);
    });
    
    population_.sort_by_fitness();
    update_statistics();
}

bool EvolutionEngine::should_stop() const {
    if (best_fitness_history_.empty()) return false;
    
    // Check target fitness
    if (early_stopping_ && best_fitness_history_.back() >= target_fitness_) {
        return true;
    }
    
    // Check stagnation
    if (best_fitness_history_.size() >= stagnation_limit_) {
        double recent_best = best_fitness_history_.back();
        double old_best = best_fitness_history_[best_fitness_history_.size() - stagnation_limit_];
        
        if (std::abs(recent_best - old_best) < 1e-6) {
            return true; // Stagnated
        }
    }
    
    return false;
}

void EvolutionEngine::update_statistics() {
    best_fitness_history_.push_back(population_.get_best_fitness());
    avg_fitness_history_.push_back(population_.get_average_fitness());
}

} // namespace VGP
