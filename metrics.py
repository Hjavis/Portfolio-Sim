import pandas as pd
import numpy as np
from portfolio import portfolio
from download_data import download_and_save_data, load_data
from Sim.utils import plot_portfolio, plot_sector_distribution

download_and_save_data()  # Will skip if already saved
data = load_data('Sim/tickerdata.csv')

def portfolio_returns(data, start_date=None, end_date=None):
    """
    Convert multi-index DataFrame to a Series of returns.
    
    Parameters:
        data (pd.DataFrame): MultiIndex (ticker, feature) with 'Close' prices.
        
    Returns:
        pd.Series: Returns of the portfolio.
    """
    if start_date:
        data = data.loc[data.index >= pd.to_datetime(start_date)]
    if end_date:
        data = data.loc[data.index <= pd.to_datetime(end_date)]

    close_prices = data.xs('Close', level=1, axis=1)
    daily_returns = close_prices.pct_change().dropna()
    weights = pd.Series(portfolio)

    portfolio_daily_returns = daily_returns.dot(weights)
    return portfolio_daily_returns
    

def portfolio_return_float(data, start_date=None, end_date=None):
    """
    Calculate portfolio cumulative return between start_date and end_date.
    
    Parameters:
        data (pd.DataFrame): MultiIndex (ticker, feature) with 'Close' prices.
        portfolio (dict): {ticker: weight} summing to 1.
        start_date (str or pd.Timestamp): inclusive start date (optional).
        end_date (str or pd.Timestamp): inclusive end date (optional).
        
    Returns:
        float: cumulative portfolio return (example: 0.15 for +15%).
    """
    if start_date:
        data = data.loc[data.index >= pd.to_datetime(start_date)]
    if end_date:
        data = data.loc[data.index <= pd.to_datetime(end_date)]
    
    # Extract Close prices for portfolio tickers
    close_prices = pd.DataFrame({ticker: data[(ticker, 'Close')] for ticker in portfolio})
    
    # Normalize prices to start at 1
    normalized = close_prices / close_prices.iloc[0]
    
    # Calculate weighted returns over time
    weighted_returns = normalized.mul(pd.Series(portfolio), axis=1).sum(axis=1)
    cum_return = weighted_returns.iloc[-1] - 1
    return cum_return


