import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from backtest import BackTester
from portfolio import Portfolio
from download_data import download_and_save_data, load_data, fetch_sp500_tickers
from utils import plot_portfolio, plot_returns

#Data
tickers, sectors= fetch_sp500_tickers()
download_and_save_data(tickers,sectors)
data = load_data()

pairspf = Portfolio('PairsTrading', data, starting_cash = 5000000)
pairspf.generate_random_portfolio()
pairspf.print_portfolio_log()
plot_portfolio(pairspf)

PairsBT = BackTester(pairspf)
pairstickers = np.random.choice(tickers, size=100, replace=False)
results = PairsBT.pairs_trading_strategy_full(tickers=pairstickers)






