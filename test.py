from download_data import load_data, download_and_save_data, fetch_sp500_tickers
from portfolio import Portfolio
from cashflow import CashFlow, CashFlowManager, DerivativeCashFlow, DividendCashFlow, InterestCashFlow
from riskmetrics import RiskMetrics
from backtest import BackTester
from utils import plot_portfolio, plot_portfolio_historic, plot_sector_distribution, plot_portfolio_return_volatility, plot_returns
from metrics import portfolio_returns, portfolio_return_float, portfolio_pnl
import pandas as pd

#Eksempel på brug

#Data
tickers, sectors= fetch_sp500_tickers()
download_and_save_data(tickers,sectors)
data = load_data()

#Opret din portefølje
pf = Portfolio(name="Hja", data=data, starting_cash=100000)

#Buy sell
pf.buy_asset('AAPL', 10, at_date='2016-01-05')
pf.buy_asset('GOOGL', 155, at_date='2016-05-05')
pf.buy_asset('TSLA', 241, at_date='2018-04-15')
pf.buy_asset('NVDA', 41, at_date='2017-12-20')
pf.buy_asset('JPM', 115, at_date='2018-04-12')

pf.sell_asset('GOOGL', 100, at_date='2025-07-13') 

# Get all available tickers from the data
tickers = list(pf.data.columns.get_level_values(0).unique())

backtest_on_pf = BackTester(pf)
backtest_on_pf.trading_pairs_strategy_full(tickers)