import pandas as pd
from portfolio import Portfolio
from download_data import download_and_save_data, load_data
from utils import plot_portfolio, plot_sector_distribution, get_time_interval
from collections import defaultdict, deque



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
    inventory = defaultdict(deque)
    
    for log in portfolio.get_portfolio_log().itertuples():
        if not (start <= log.Date <= end):
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



def portfolio_returns(data, start_date=None, end_date=None):
    #fix
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
    #fix
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


