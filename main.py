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

#download_and_save_data()
#plot_portfolio(portfolio)
#plot_sector_distribution(data)

#print(portfolio_return_float(data, start_date='2018-01-01', end_date='2024-01-01'))

#print(portfolio_returns(data, start_date='2018-01-01', end_date='2024-01-01').head())
#plot_portfolio_returns(portfolio_returns(data, start_date='2018-01-01', end_date='2024-01-01'))
#plot_portfolio_return_volatility(portfolio_returns(data, start_date='2018-01-01', end_date='2024-01-01'), rolling_window=30)


#print_portfolio(data)
#buy_asset(data, 'AAPL', 10, at_date='2016-01-05')
#buy_asset(data, 'GOOGL', 155, at_date='2016-05-05')
#buy_asset(data, 'MSFT', 100, at_date='2018-01-05')
#plot_portfolio(data)
#plot_sector_distribution(data)

#plot_portfolio_return_volatility(portfolio_returns(data, start_date='2018-01-01', end_date='2024-01-01'), rolling_window=40)

print(data.columns)

pf.buy_asset('AAPL', 10, at_date='2016-01-05')
pf.buy_asset('GOOGL', 155, at_date='2016-05-05')
pf.buy_asset('TSLA', 241, at_date='2018-04-15')
pf.buy_asset('NVDA', 41, at_date='2017-12-20')

pf.sell_asset('GOOGL', 100, at_date='2025-07-13') 
print(simple_historical_var(pf, lookback_days=45))
#pf.reset_portfolio()

#pfbacktest = BackTester(pf)
#pfbacktest.moving_average_strategy_full('AAPL', window=30)
