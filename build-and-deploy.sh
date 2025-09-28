#!/bin/bash
# Quick build and deploy script for hackathon

echo "🚀 VTHacks26 Quick Deploy Script"
echo "================================"

# Build React frontend
echo "📦 Building React frontend..."
cd stock-dashboard
npm run build
cd ..

echo "✅ React build complete!"

# Deploy to fly.io
echo "🌐 Deploying to fly.io..."
flyctl deploy --dockerfile Dockerfile.financial-api

echo "🎉 Deployment complete!"
echo "🔗 Your app: https://vthacks26-financial-api.fly.dev"
echo "💻 Frontend: https://vthacks26-financial-api.fly.dev"
echo "📊 API: https://vthacks26-financial-api.fly.dev/docs"
