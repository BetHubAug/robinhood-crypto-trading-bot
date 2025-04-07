import pandas as pd
import backtrader as bt

class ScalpingStrategy(bt.Strategy):
    def __init__(self):
        self.sma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=10)
        self.sma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=50)

    def next(self):
        if self.sma_short > self.sma_long:  # Bullish crossover
            self.buy(size=0.01)  # Example trade size
        elif self.sma_short < self.sma_long:  # Bearish crossover
            self.sell(size=0.01)

# Load historical price data from CSV
data = pd.read_csv("data/crypto_data.csv")
data['datetime'] = pd.to_datetime(data['datetime'])
data.set_index('datetime', inplace=True)

# Set up Backtrader with the data
cerebro = bt.Cerebro()
data_feed = bt.feeds.PandasData(dataname=data)
cerebro.adddata(data_feed)
cerebro.addstrategy(ScalpingStrategy)

# Run the backtest and plot results
cerebro.run()
cerebro.plot()
