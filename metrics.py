import pandas as pd
import numpy as np
from portfolio import Portfolio
from utils import get_time_interval
from collections import defaultdict, deque
import scipy.stats as stats


def portfolio_pnl(portfolio, start_date=None, end_date=None) -> tuple[float]:
    """
    Calculate the profit and loss of the portfolio over a specified date range.
    
    Parameters:
        portfolio (Portfolio): The portfolio object
        start_date (str or pd.Timestamp): Start date for calculation (optional).
        end_date (str or pd.Timestamp): End date for calculation (optional).
        
    Returns:
        tuple: (realised_pnl, unrealised_pnl) floats
    """
    prices = portfolio.data
    start,end = get_time_interval(prices, start_date, end_date, verify_date=portfolio.verify_date)
    realised_pnl = 0.0
    unrealised_pnl = 0.0
    inventory = defaultdict(deque) #fifo
    
    log_df = pd.DataFrame(portfolio.log) if isinstance(portfolio.log, list) else portfolio.log
    for log in log_df.itertuples():
        log_date = pd.to_datetime(log.Date)
        if not (start <= log_date <= end):
            continue
        
        ticker = log.Ticker
        quantity = log.Quantity
        price = log.Price
        
        if log.Type == 'Buy':
            inventory[ticker].append((quantity, price))
            
            
        elif log.Type == 'Sell':
            quantity_to_sell = quantity
            while quantity_to_sell > 0 and inventory[ticker]:
                bought_quantity, bought_price =inventory[ticker][0]
                matched_quantity = min(quantity_to_sell, bought_quantity)
                pnl = matched_quantity * (price - bought_price)
                realised_pnl += pnl
                quantity_to_sell -= matched_quantity
                if matched_quantity == bought_quantity:
                    inventory[ticker].popleft()
                else:
                    inventory[ticker][0] = (bought_quantity - matched_quantity, bought_price)
            
        elif log.Type == 'Dividend':
            realised_pnl += log.Total
            
        elif log.Type == 'Interest':
            realised_pnl += log.Total
            
        else: #Fix hvis der tilføjes andre former for cashflows
            raise ValueError(f"Transaction type '{log.Type}' not implemented.")
        
    for ticker, lots in inventory.items():
        current_price = prices.loc[end, (ticker, 'Close')]
    for quantity, cost in lots:
        unrealised_pnl += quantity * (current_price - cost)

    
    return realised_pnl, unrealised_pnl

def simple_historical_var(portfolio, confidence_level=0.95, lookback_days=100) -> float:
        """
        Calculates portfolio Value at Risk (VaR) using historical simulation.
        Assumes that quantity of assets are constant over the lookback_days period.
        Args:
            confidence_level (float): Confidence level for VaR (e.g. 0.95 for 95% VaR).
            lookback_days (int): Number of past trading days to use.

        Returns:
            float: Estimated daily VaR.
        """
        if not portfolio.assets:
            print("No assets in portfolio.")
            return 0.0

        returns = []
        for ticker, quantity in portfolio.assets.items():
            if (ticker, 'Close') not in portfolio.data.columns:
                continue
            price_series = portfolio.data[(ticker, 'Close')].dropna()
            daily_returns = price_series.pct_change().dropna()
            weighted_returns = daily_returns[-lookback_days:] * quantity * price_series.iloc[-1]
            returns.append(weighted_returns)

        if not returns:
            print("No valid return data.")
            return 0.0

        portfolio_returns_series = pd.concat(returns, axis=1).sum(axis=1)
        var = -np.percentile(portfolio_returns_series, (1 - confidence_level) * 100)
        print(f"{int(confidence_level*100)}% 1-day Historical VaR: ${var:.2f}")
        return var

def calculate_var_parametric(returns, confidence_level=0.95)-> float:
    """Calculate VaR using parametric (normal distribution) approach
    example: 0.055 = 5.5% loss at the confidence level.
    """
    mean = returns.mean()
    std_dev = returns.std()
    return -(mean + std_dev * stats.norm.ppf(1-confidence_level))



def portfolio_returns(portfolio, start_date=None, end_date=None):
    """
    Convert multi-index DataFrame to a Series of returns.
    
    Parameters:
        data (pd.DataFrame): MultiIndex (ticker, feature) with 'Close' prices.
        
    Returns:
        pd.Series: Returns of the portfolio.
    """
    data = portfolio.data.copy()

    if start_date:
        data = data.loc[data.index >= pd.to_datetime(start_date)]
    if end_date:
       data = data.loc[data.index <= pd.to_datetime(end_date)]

    close_prices = data.xs('Close', level=1, axis=1)
    daily_returns = close_prices.pct_change().dropna()

    current_prices = {ticker: portfolio.data[(ticker, 'Close')].iloc[-1] 
                     for ticker in portfolio.assets}
    weights = {ticker: portfolio.assets[ticker] * current_prices[ticker] 
              for ticker in portfolio.assets}
    total_value = sum(weights.values())
    
    if total_value == 0:
        return pd.Series(dtype=float)
    
    # Normalisér weights
    weights = {t: w/total_value for t, w in weights.items()}
    
    # Match med deres respektive tickers
    valid_tickers = [t for t in weights.keys() if t in daily_returns.columns]
    if not valid_tickers:
        return pd.Series(dtype=float)
    
    # wieght_series
    weights_series = pd.Series(weights)[valid_tickers]
    
    #tag daglige returns enten positive eller negative for hver ticker, og gang dem med deres respektive vægt i porteføljen. ved at tage prikproduktet
    return daily_returns[valid_tickers].dot(weights_series)
    
def portfolio_return_float(portfolio, start_date=None, end_date=None):
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
    returns = portfolio_returns(portfolio, start_date, end_date)
    if returns.empty:
        return 0.0
 
    cum_return = (1+returns).prod() - 1
    return cum_return


