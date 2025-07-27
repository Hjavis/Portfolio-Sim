from download_data import load_data, download_and_save_data, fetch_sp500_tickers
tickers, sectors= fetch_sp500_tickers()
download_and_save_data(tickers,sectors)
data = load_data()

from portfolio import Portfolio
pf = Portfolio(name="Hja", data=data, starting_cash=100000)

from backtest import BackTester
from utils import plot_portfolio, plot_portfolio_historic, plot_sector_distribution, plot_portfolio_returns, plot_portfolio_return_volatility
from metrics import simple_historical_var, portfolio_returns, portfolio_return_float
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#Eksempel på brug

pf.buy_asset('AAPL', 10, at_date='2016-01-05')
pf.buy_asset('GOOGL', 155, at_date='2016-05-05')
pf.buy_asset('TSLA', 241, at_date='2018-04-15')
pf.buy_asset('NVDA', 41, at_date='2017-12-20')

pf.sell_asset('GOOGL', 100, at_date='2025-07-13') 
print(simple_historical_var(pf, lookback_days=45))

plot_portfolio(pf)



print(data.columns)

pf.reset_portfolio()

pfbacktest = BackTester(pf)
pfbacktest.moving_average_strategy_full('AAPL', window=30)
pfbacktest.sell_in_may_and_go_away_strategy_full('TSLA')

print(pf.get_portfolio_value())
pf.print_portfolio_log(10)