#!/bin/bash
# Aerospike Backend Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}$1${NC}"
    echo "=========================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Help function
show_help() {
    echo "Aerospike Backend Management Script"
    echo ""
    echo "Usage: ./manage.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup           - Install dependencies and setup backend"
    echo "  start           - Start the backend server"
    echo "  test-aerospike  - Test direct Aerospike connection"
    echo "  test-backend    - Run backend integration tests"
    echo "  test-full       - Run comprehensive test suite"
    echo "  install         - Install Python dependencies"
    echo "  check-aerospike - Check if Aerospike is running"
    echo "  help            - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./manage.sh setup"
    echo "  ./manage.sh start"
    echo "  ./manage.sh test-full"
}

# Check if Aerospike is running
check_aerospike() {
    print_header "Checking Aerospike Status"
    
    if docker ps | grep -q aerospike; then
        print_success "Aerospike container is running"
        
        # Check if port 3000 is accessible
        if nc -z localhost 3000 2>/dev/null; then
            print_success "Aerospike is accessible on port 3000"
            return 0
        else
            print_warning "Aerospike container running but port 3000 not accessible"
            return 1
        fi
    else
        print_error "Aerospike container not found"
        echo "Start Aerospike with: docker-compose up -d"
        return 1
    fi
}

# Install dependencies
install_deps() {
    print_header "Installing Dependencies"
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        return 1
    fi
}

# Setup everything
setup() {
    print_header "Setting Up Aerospike Backend"
    
    install_deps
    check_aerospike
    
    print_header "Running Setup Script"
    python setup_aerospike_backend.py
}

# Start backend
start_backend() {
    print_header "Starting Backend Server"
    
    if [ -f "run_backend.py" ]; then
        echo "Starting backend on http://localhost:8000"
        echo "API Documentation: http://localhost:8000/docs"
        echo "Press Ctrl+C to stop"
        echo ""
        python run_backend.py
    else
        print_error "run_backend.py not found"
        return 1
    fi
}

# Test Aerospike directly
test_aerospike() {
    print_header "Testing Aerospike Connection"
    
    check_aerospike
    
    if [ -f "test_aerospike_direct.py" ]; then
        python test_aerospike_direct.py
    else
        print_error "test_aerospike_direct.py not found"
        return 1
    fi
}

# Test backend
test_backend() {
    print_header "Testing Backend"
    
    if [ -f "test_backend.py" ]; then
        python test_backend.py
    else
        print_error "test_backend.py not found"
        return 1
    fi
}

# Run full test suite
test_full() {
    print_header "Running Full Test Suite"
    
    check_aerospike
    
    if [ -f "test_aerospike_integration.py" ]; then
        python test_aerospike_integration.py
    else
        print_error "test_aerospike_integration.py not found"
        return 1
    fi
}

# Main script logic
case "${1:-help}" in
    "setup")
        setup
        ;;
    "start")
        start_backend
        ;;
    "test-aerospike")
        test_aerospike
        ;;
    "test-backend")
        test_backend
        ;;
    "test-full")
        test_full
        ;;
    "install")
        install_deps
        ;;
    "check-aerospike")
        check_aerospike
        ;;
    "help"|*)
        show_help
        ;;
esac