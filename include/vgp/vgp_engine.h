#ifndef VGP_ENGINE_H
#define VGP_ENGINE_H

#include <vector>
#include <memory>
#include <random>
#include <functional>
#include <string>
#include <unordered_map>
#include "market_data/market_data.h"
#include "technical_indicators/technical_indicators.h"

namespace VGP {

// Forward declarations
class Individual;
class Population;

/**
 * Represents a gene in the VGP chromosome
 * Can be an operation, constant, or terminal (market feature)
 */
enum class GeneType {
    OPERATION,
    CONSTANT,
    TERMINAL
};

enum class OperationType {
    ADD,
    SUBTRACT,
    MULTIPLY,
    DIVIDE,
    SIN,
    COS,
    TANH,
    LOG,
    EXP,
    ABS,
    SQRT,
    POWER,
    MAX,
    MIN,
    IF_GREATER,
    IF_LESS,
    AND_OP,
    OR_OP,
    NOT_OP
};

/**
 * A gene represents a single instruction in the VGP program
 */
struct Gene {
    GeneType type;
    OperationType operation;
    double constant_value;
    std::string terminal_name;
    int arity; // Number of arguments for operations
    
    Gene() : type(GeneType::CONSTANT), operation(OperationType::ADD), 
             constant_value(0.0), arity(0) {}
    
    Gene(OperationType op, int ar) : type(GeneType::OPERATION), operation(op), 
                                     constant_value(0.0), arity(ar) {}
    
    Gene(double val) : type(GeneType::CONSTANT), operation(OperationType::ADD), 
                       constant_value(val), arity(0) {}
    
    Gene(const std::string& terminal) : type(GeneType::TERMINAL), operation(OperationType::ADD), 
                                        constant_value(0.0), terminal_name(terminal), arity(0) {}
};

/**
 * Context for evaluating VGP expressions
 * Contains current market state and feature values
 */
class EvaluationContext {
public:
    std::unordered_map<std::string, double> features;
    std::unordered_map<std::string, std::vector<double>> feature_series;
    
    void add_feature(const std::string& name, double value) {
        features[name] = value;
    }
    
    void add_feature_series(const std::string& name, const std::vector<double>& series) {
        feature_series[name] = series;
    }
    
    double get_feature(const std::string& name) const {
        auto it = features.find(name);
        return (it != features.end()) ? it->second : 0.0;
    }
    
    const std::vector<double>& get_feature_series(const std::string& name) const {
        static std::vector<double> empty;
        auto it = feature_series.find(name);
        return (it != feature_series.end()) ? it->second : empty;
    }
};

/**
 * Represents an individual in the VGP population
 * Contains a vector of genes that form a trading strategy
 */
class Individual {
private:
    std::vector<Gene> chromosome_;
    double fitness_;
    bool fitness_evaluated_;
    mutable std::vector<double> execution_stack_;
    
public:
    Individual() : fitness_(0.0), fitness_evaluated_(false) {}
    explicit Individual(const std::vector<Gene>& genes) 
        : chromosome_(genes), fitness_(0.0), fitness_evaluated_(false) {}
    
    // Accessors
    const std::vector<Gene>& get_chromosome() const { return chromosome_; }
    std::vector<Gene>& get_chromosome() { return chromosome_; }
    double get_fitness() const { return fitness_; }
    void set_fitness(double fitness) { fitness_ = fitness; fitness_evaluated_ = true; }
    bool is_fitness_evaluated() const { return fitness_evaluated_; }
    void clear_fitness() { fitness_evaluated_ = false; }
    
    size_t size() const { return chromosome_.size(); }
    Gene& operator[](size_t index) { return chromosome_[index]; }
    const Gene& operator[](size_t index) const { return chromosome_[index]; }
    
    // VGP execution
    double evaluate(const EvaluationContext& context) const;
    std::vector<double> evaluate_series(const EvaluationContext& context, size_t series_length) const;
    
    // Generate trading signals
    double generate_signal(const EvaluationContext& context) const;
    std::vector<int> generate_signals(const EvaluationContext& context, size_t length) const; // -1, 0, 1 for sell, hold, buy
    
    // Genetic operations
    void mutate(double mutation_rate, std::mt19937& rng);
    Individual crossover(const Individual& other, std::mt19937& rng) const;
    
    // Utility
    void randomize(size_t length, std::mt19937& rng);
    std::string to_string() const;
    
private:
    double execute_operation(OperationType op, const std::vector<double>& args) const;
    bool is_valid() const;
};

/**
 * Manages the VGP population and evolution process
 */
class Population {
private:
    std::vector<Individual> individuals_;
    size_t population_size_;
    size_t chromosome_length_;
    double mutation_rate_;
    double crossover_rate_;
    double elite_ratio_;
    std::mt19937 rng_;
    
    // Available operations and terminals
    std::vector<OperationType> available_operations_;
    std::vector<std::string> available_terminals_;
    double constant_min_, constant_max_;
    
public:
    Population(size_t pop_size, size_t chrom_length, unsigned seed = 0);
    
    // Configuration
    void set_mutation_rate(double rate) { mutation_rate_ = rate; }
    void set_crossover_rate(double rate) { crossover_rate_ = rate; }
    void set_elite_ratio(double ratio) { elite_ratio_ = ratio; }
    void set_constant_range(double min_val, double max_val) { 
        constant_min_ = min_val; constant_max_ = max_val; 
    }
    
    void add_operation(OperationType op) { available_operations_.push_back(op); }
    void add_terminal(const std::string& terminal) { available_terminals_.push_back(terminal); }
    
    // Population management
    void initialize();
    void evaluate_fitness(const std::function<double(const Individual&)>& fitness_func);
    void evolve();
    void sort_by_fitness();
    
    // Accessors
    const Individual& get_best() const { return individuals_[0]; }
    Individual& get_individual(size_t index) { return individuals_[index]; }
    const Individual& get_individual(size_t index) const { return individuals_[index]; }
    size_t size() const { return individuals_.size(); }
    
    // Statistics
    double get_average_fitness() const;
    double get_best_fitness() const;
    double get_worst_fitness() const;
    std::vector<double> get_fitness_stats() const;
    
private:
    Gene generate_random_gene();
    Individual tournament_selection(size_t tournament_size = 3);
    void replace_population(std::vector<Individual>& new_pop);
};

/**
 * Feature builder for VGP terminals
 * Converts market data into features that VGP can use
 */
class FeatureBuilder {
private:
    std::vector<std::unique_ptr<TechnicalIndicators::Indicator>> indicators_;
    std::vector<std::string> feature_names_;
    
public:
    FeatureBuilder();
    ~FeatureBuilder() = default;
    
    // Add indicators and features
    void add_sma(int period);
    void add_ema(int period);
    void add_rsi(int period = 14);
    void add_macd(int fast = 12, int slow = 26, int signal = 9);
    void add_bollinger_bands(int period = 20, double std_dev = 2.0);
    void add_atr(int period = 14);
    void add_stochastic(int k_period = 14, int d_period = 3);
    void add_obv();
    void add_cmf(int period = 20);
    
    // Add price-based features
    void add_price_features();
    void add_volume_features();
    void add_momentum_features();
    
    // Build features for VGP evaluation
    EvaluationContext build_context(const MarketData::TimeSeries& ts, size_t window_size = 50) const;
    std::vector<std::string> get_feature_names() const { return feature_names_; }
    
private:
    void register_feature(const std::string& name);
};

/**
 * VGP Evolution Engine
 * Main class that coordinates the entire VGP evolution process
 */
class EvolutionEngine {
private:
    Population population_;
    FeatureBuilder feature_builder_;
    std::function<double(const Individual&, const MarketData::TimeSeries&)> fitness_function_;
    
    // Evolution parameters
    size_t max_generations_;
    double target_fitness_;
    bool early_stopping_;
    size_t stagnation_limit_;
    
    // Statistics tracking
    std::vector<double> best_fitness_history_;
    std::vector<double> avg_fitness_history_;
    size_t current_generation_;
    
public:
    EvolutionEngine(size_t pop_size, size_t chrom_length, unsigned seed = 0);
    
    // Configuration
    void set_max_generations(size_t gens) { max_generations_ = gens; }
    void set_target_fitness(double target) { target_fitness_ = target; }
    void set_early_stopping(bool enable) { early_stopping_ = enable; }
    void set_stagnation_limit(size_t limit) { stagnation_limit_ = limit; }
    void set_fitness_function(std::function<double(const Individual&, const MarketData::TimeSeries&)> func) {
        fitness_function_ = func;
    }
    
    // Feature configuration
    FeatureBuilder& get_feature_builder() { return feature_builder_; }
    Population& get_population() { return population_; }
    
    // Evolution process
    void evolve(const MarketData::TimeSeries& training_data);
    Individual get_best_individual() const { return population_.get_best(); }
    
    // Statistics and monitoring
    size_t get_current_generation() const { return current_generation_; }
    const std::vector<double>& get_best_fitness_history() const { return best_fitness_history_; }
    const std::vector<double>& get_avg_fitness_history() const { return avg_fitness_history_; }
    
    // Callback for monitoring progress
    std::function<void(size_t generation, const Individual& best, double avg_fitness)> progress_callback;
    
private:
    bool should_stop() const;
    void update_statistics();
};

} // namespace VGP

#endif // VGP_ENGINE_H