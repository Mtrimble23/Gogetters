#!/usr/bin/env python3
"""
Setup Alpaca API keys as environment variables
"""

import os

def setup_alpaca_keys():
    """Setup Alpaca API credentials"""

    print("🔑 Setting up Alpaca API credentials...")

    # Your API key
    api_key = "PK1E7AWHGHV85SI81FS7"

    # You'll need to get your secret key from Alpaca dashboard
    secret_key = input("Enter your Alpaca SECRET key: ").strip()

    # Paper trading URL (safe for testing)
    base_url = "https://paper-api.alpaca.markets"

    # Set environment variables for current session
    os.environ['APCA_API_KEY_ID'] = api_key
    os.environ['APCA_API_SECRET_KEY'] = secret_key
    os.environ['APCA_API_BASE_URL'] = base_url

    print("✅ Alpaca credentials configured for this session!")
    print(f"   API Key: {api_key}")
    print(f"   Base URL: {base_url}")
    print("   Secret Key: [HIDDEN]")

    # Test connection
    try:
        from alpaca_trade_api import REST
        alpaca = REST(api_key, secret_key, base_url)
        account = alpaca.get_account()
        print(f"🏦 Connection successful! Account value: ${float(account.portfolio_value):,.2f}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    setup_alpaca_keys()