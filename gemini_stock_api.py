import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

@app.route('/api/stock/summary', methods=['POST'])
def generate_stock_summary():
    """Generate AI summary for stock data using Gemini"""
    try:
        data = request.get_json()

        # Extract stock data from request
        symbol = data.get('symbol', 'Unknown')
        price = data.get('price', 0)
        change_percent = data.get('changePercent', 0)
        market_cap = data.get('marketCap', 0)
        pe_ratio = data.get('peRatio', 0)
        beta = data.get('beta', 0)
        risk_score = data.get('riskScore', None)
        risk_grade = data.get('riskGrade', 'Unknown')

        # Create prompt for Gemini
        prompt = f"""
        Analyze the following stock data and provide a concise, investor-friendly summary in 2-3 sentences:

        Stock: {symbol}
        Current Price: ${price}
        Change: {change_percent}%
        Market Cap: ${market_cap:,.0f}
        P/E Ratio: {pe_ratio}
        Beta: {beta}
        Risk Score: {risk_score}/100 ({risk_grade} risk)

        Focus on:
        1. Current performance and valuation
        2. Risk assessment
        3. What this means for everyday investors

        Keep it simple and actionable, avoiding jargon.
        """

        # Generate summary using Gemini
        response = model.generate_content(prompt)
        summary = response.text.strip()

        return jsonify({
            'success': True,
            'summary': summary,
            'symbol': symbol
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock', methods=['GET'])
def get_stock_data():
    """Mock stock data endpoint - replace with real data source"""
    symbol = request.args.get('symbol', 'AAPL')

    # Mock data - replace with real Yahoo Finance scraping or API
    mock_data = {
        'AAPL': {
            'symbol': 'AAPL',
            'shortName': 'Apple Inc.',
            'price': 192.34,
            'changePercent': -0.84,
            'marketCap': 3000000000000,
            'peRatio': 28.4,
            'beta': 1.12,
            'week52Low': 120.23,
            'week52High': 203.45,
            'volume': 52000000,
            'avgVolume': 60000000,
            'dividendYield': 0.005,
            'historical': [
                {'t': '2025-09-01', 'p': 180},
                {'t': '2025-09-02', 'p': 185},
                {'t': '2025-09-03', 'p': 190},
                {'t': '2025-09-04', 'p': 192}
            ],
            'risk': {'score': 72, 'grade': 'Medium'}
        },
        'AMZN': {
            'symbol': 'AMZN',
            'shortName': 'Amazon.com Inc.',
            'price': 3456.78,
            'changePercent': 1.23,
            'marketCap': 1800000000000,
            'peRatio': 45.2,
            'beta': 1.45,
            'week52Low': 2800.00,
            'week52High': 3600.00,
            'volume': 25000000,
            'avgVolume': 30000000,
            'dividendYield': 0.0,
            'historical': [
                {'t': '2025-09-01', 'p': 3400},
                {'t': '2025-09-02', 'p': 3420},
                {'t': '2025-09-03', 'p': 3440},
                {'t': '2025-09-04', 'p': 3457}
            ],
            'risk': {'score': 65, 'grade': 'Medium'}
        }
    }

    # Add default data for other symbols
    if symbol not in mock_data:
        mock_data[symbol] = {
            'symbol': symbol,
            'shortName': f'{symbol} Corporation',
            'price': 100.00,
            'changePercent': 0.0,
            'marketCap': 1000000000,
            'peRatio': 20.0,
            'beta': 1.0,
            'week52Low': 80.0,
            'week52High': 120.0,
            'volume': 10000000,
            'avgVolume': 12000000,
            'dividendYield': 0.02,
            'historical': [
                {'t': '2025-09-01', 'p': 95},
                {'t': '2025-09-02', 'p': 98},
                {'t': '2025-09-03', 'p': 99},
                {'t': '2025-09-04', 'p': 100}
            ],
            'risk': {'score': 50, 'grade': 'Medium'}
        }

    return jsonify(mock_data[symbol])

if __name__ == '__main__':
    app.run(debug=True, port=5000)