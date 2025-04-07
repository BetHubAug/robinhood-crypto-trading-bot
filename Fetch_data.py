import requests
import pandas as pd
from datetime import datetime

def fetch_binance_historical_data(symbol="BTCUSDT", interval="1d", limit=100):
    """
    Fetch historical crypto data from Binance.
    
    Args:
        symbol (str): Trading pair (e.g., BTCUSDT for Bitcoin/USDT).
        interval (str): Time interval (e.g., 1m, 5m, 1h, 1d).
        limit (int): Number of data points to fetch (max: 1000).
    
    Returns:
        pd.DataFrame: DataFrame containing historical OHLCV data.
    """
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
        print(f"Failed to fetch data: {response.status_code}")
        return None

# Example usage
if __name__ == "__main__":
    symbol = "BTCUSDT"  # Bitcoin/USDT trading pair
    interval = "1d"     # Daily interval
    limit = 100         # Fetch last 100 days of data

    df = fetch_binance_historical_data(symbol, interval, limit)
    if df is not None:
        print(df.head())
        # Save to CSV for backtesting
        df.to_csv("data/crypto_data.csv", index=False)
          
