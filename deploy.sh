#!/bin/bash
# Deployment script for VTHacks26 Financial API on fly.io

echo "========================================"
echo "VTHacks26 Financial API Deployment"
echo "========================================"

# Check if fly CLI is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is not installed. Please install it first:"
    echo "   curl -L https://fly.io/install.sh | sh"
    exit 1
fi

echo "🔐 Logging into fly.io..."
flyctl auth login

echo "🚀 Deploying to fly.io..."
flyctl deploy

echo "✅ Deployment complete!"
echo "🌐 Your API should be available at: https://vthacks26-financial-api.fly.dev"
echo "📊 Health check: https://vthacks26-financial-api.fly.dev/health"
echo "📖 API docs: https://vthacks26-financial-api.fly.dev/docs"