#!/usr/bin/env python3
"""
Robinhood Crypto Trading Bot for Termux (2025 Edition)
Interactive and User-Friendly Version
"""

import os
import json
import time
import logging
import requests
import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

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

    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.token = None
        self.account_id = None
        self.model = RandomForestClassifier()

    def load_config(self, path: str) -> Dict:
        with open(path, "r") as file:
            return json.load(file)

    def setup(self):
        """Interactive setup for user configuration"""
        print("\nWelcome to Robinhood Crypto Trading Bot!")
        print("Please provide your Robinhood credentials.")

        username = input("Username: ")
        password = input("Password: ")

        self.config["credentials"]["username"] = username
        self.config["credentials"]["password"] = password

        print("\nSetup complete! Proceeding to authentication...\n")

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

    def fetch_historical_data(self, symbol: str, interval: str = "1d", limit: int = 100) -> pd.DataFrame:
        """Fetch historical crypto data from Binance"""
        logger.info(f"Fetching historical data for {symbol} with interval {interval}")
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])

            # Convert timestamps to readable dates
            df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
            df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")

            # Keep only relevant columns
            df = df[["open_time", "open", "high", "low", "close", "volume"]]
            return df
        else:
            logger.error(f"Failed to fetch historical data: {response.status_code}")
            return pd.DataFrame()

    def analyze_data(self, data: pd.DataFrame):
        """Analyze data and train model"""
        logger.info("Analyzing data and training model...")
        if data.empty:
            logger.error("No data to analyze")
            return

        data['target'] = (data['close'].shift(-1) > data['close']).astype(int)  # Example target
        X = data.drop(['target', 'open_time'], axis=1)
        y = data['target']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        logger.info(f"Model training completed with accuracy: {accuracy_score(y_test, self.model.predict(X_test))}")

    def make_decision(self, quotes: Dict[str, Dict[str, float]]) -> str:
        """Make buy/sell decision based on AI model"""
        logger.info("Making buy/sell decision...")
        if not quotes:
            logger.error("No quotes available for decision making")
            return "hold"

        features = np.array([quotes[symbol]['price'] for symbol in quotes]).reshape(1, -1)
        prediction = self.model.predict(features)
        return "buy" if prediction == 1 else "sell"

def main():
    bot = RobinhoodCryptoBot()
    bot.setup()

    if bot.authenticate():
        while True:
            print("\nMain Menu:")
            print("1. Fetch Crypto Quotes")
            print("2. Place Order")
            print("3. Fetch Historical Data")
            print("4. Analyze Data")
            print("5. Make Decision")
            print("6. Exit")

            choice = input("Select an option (1/2/3/4/5/6): ")

            if choice == '1':
                symbols = input("Enter cryptocurrency symbols (comma-separated): ").split(',')
                quotes = bot.fetch_crypto_quotes([s.strip().upper() for s in symbols])
                print("\nCurrent Quotes:")
                for symbol, data in quotes.items():
                    print(f"{symbol}: Price - ${data['price']}, Volume - {data['volume']}")

            elif choice == '2':
                symbol = input("Enter cryptocurrency symbol: ").strip().upper()
                quantity = float(input("Enter quantity to trade: "))
                side = input("Enter 'buy' or 'sell': ").strip().lower()

                if bot.place_order(symbol, quantity, side):
                    print("\nOrder placed successfully!")
                else:
                    print("\nFailed to place order.")

            elif choice == '3':
                symbol = input("Enter cryptocurrency symbol (e.g., BTCUSDT): ").strip().upper()
                interval = input("Enter time interval (e.g., 1d, 1h): ").strip()
                limit = int(input("Enter limit (number of data points to fetch): ").strip())

                data = bot.fetch_historical_data(symbol, interval, limit)
                if not data.empty:
                    print(data.head())
                    data.to_csv("data/crypto_data.csv", index=False)
                    print("\nHistorical data fetched and saved to data/crypto_data.csv")
                else:
                    print("\nFailed to fetch historical data.")

            elif choice == '4':
                file_path = input("Enter path to historical data CSV file: ").strip()
                if os.path.exists(file_path):
                    data = pd.read_csv(file_path)
                    bot.analyze_data(data)
                else:
                    print("\nFile not found.")

            elif choice == '5':
                symbols = input("Enter cryptocurrency symbols (comma-separated): ").split(',')
                quotes = bot.fetch_crypto_quotes([s.strip().upper() for s in symbols])
                decision = bot.make_decision(quotes)
                print(f"\nDecision: {decision}")

            elif choice == '6':
                print("\nExiting... Goodbye!")
                break

            else:
                print("\nInvalid option. Please try again.")

if __name__ == "__main__":
    main()
