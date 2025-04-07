#!/usr/bin/env python3
"""
Robinhood Crypto Trading Bot for Termux (2025 Edition)
Designed for small accounts with optimized scalping strategies.
"""

import os
import json
import time
import logging
import requests
import datetime
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crypto_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("crypto_bot")

class RobinhoodCryptoBot:
    """Robinhood Cryptocurrency Trading Bot"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.token = None
        self.account_id = None

    def _load_config(self) -> Dict:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            logger.error("Configuration file not found!")
            exit(1)

    def authenticate(self) -> bool:
        """Authenticate with Robinhood API"""
        logger.info("Authenticating with Robinhood...")
        auth_url = "https://api.robinhood.com/oauth2/token/"
        payload = {
            "client_id": "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
            "expires_in": 86400,
            "grant_type": "password",
            "password": self.config["credentials"]["password"],
            "scope": "internal",
            "username": self.config["credentials"]["username"],
        }
        
        try:
            response = requests.post(auth_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return False

    def fetch_crypto_quotes(self, symbols: List[str]) -> Dict:
        """Fetch current quotes for cryptocurrencies"""
        logger.info(f"Fetching quotes for: {symbols}")
        quotes = {}
        try:
            for symbol in symbols:
                url = f"https://nummus.robinhood.com/marketdata/forex/quotes/{symbol}USD/"
                headers = {"Authorization": f"Bearer {self.token}"}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    quotes[symbol] = {
                        "price": float(data["mark_price"]),
                        "volume": float(data["volume"]),
                    }
                else:
                    logger.warning(f"Failed to fetch quote for {symbol}: {response.text}")
            return quotes
        except Exception as e:
            logger.error(f"Error fetching quotes: {str(e)}")
            return {}

    def place_order(self, symbol: str, quantity: float, side: str) -> bool:
        """Place a buy or sell order"""
        logger.info(f"Placing {side} order for {quantity} {symbol}...")
        url = f"https://nummus.robinhood.com/orders/"
        payload = {
            "account_id": self.account_id,
            "currency_pair_id": f"{symbol}-USD",
            "quantity": str(quantity),
            "side": side,
            "type": "market",
            "time_in_force": "gtc"
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                logger.info(f"Order placed successfully: {response.json()}")
                return True
            else:
                logger.error(f"Failed to place order: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return False

if __name__ == "__main__":
    bot = RobinhoodCryptoBot()
    if bot.authenticate():
        quotes = bot.fetch_crypto_quotes(["BTC", "ETH", "DOGE"])
        print(quotes)
