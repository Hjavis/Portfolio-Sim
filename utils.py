import matplotlib.pyplot as plt
import pandas as pd


def plot_portfolio(Portfolio):
    tickers = Portfolio.data.columns.levels[0]
    weights = [Portfolio[(ticker, 'Close')].iloc[-1] for ticker in tickers]
    
    plt.figure(figsize=(10, 6))
    plt.pie(weights, labels=tickers, autopct='%1.1f%%', startangle=140)
    plt.title('Portfolio Allocation')
    plt.axis('equal')  # Equal aspect ratio ensures that pie chart is circular.
    plt.show()

def plot_portfolio_historic(portfolio, plot_date):
    plot_date = pd.to_datetime(plot_date)

    # Find nærmeste dato før eller på plot_date
    valid_dates = portfolio.data.index[portfolio.data.index <= plot_date]
    if len(valid_dates) == 0:
        print(f"No data available before {plot_date}")
        return
    date = valid_dates[-1]

    # Udregn portofølje på plot_date
    holdings = {}
    for tx in portfolio.log:
        if tx['Date'] <= date:
            qty = holdings.get(tx['Ticker'], 0)
            if tx['Type'] == 'Buy':
                holdings[tx['Ticker']] = qty + tx['Quantity']
            elif tx['Type'] == 'Sell':
                holdings[tx['Ticker']] = qty - tx['Quantity']

    # Udregn værdien af hver beholdning på plot_date
    values = []
    tickers = []
    for ticker, qty in holdings.items():
        if ticker in portfolio.data.columns.levels[0]:
            price = portfolio.data.loc[date, (ticker, 'Close')]
            values.append(qty * price)
            tickers.append(ticker)

    if not values:
        print(f"No holdings on {date}")
        return

    # Plot
    plt.figure(figsize=(10, 6))
    plt.pie(values, labels=tickers, autopct='%1.1f%%', startangle=140)
    plt.title(f'Portfolio Allocation on {date.date()}')
    plt.axis('equal')
    plt.show()
    
def plot_sector_distribution(data):
    """
    Plots the sector distribution of the portfolio.
    
    Parameters:
    data (DataFrame): A DataFrame containing the portfolio data with sectors.
    
    Returns:
    None
    """
    tickers = data.columns.levels[0]
    
    sectors = []
    for ticker in tickers:
        if ('Sector' in data[ticker].columns):
            sector_val = data[(ticker, 'Sector')].dropna().iloc[0]
            sectors.append(sector_val)
        else:
            sectors.append('Unknown')
            
    sector_counts = pd.Series(sectors).value_counts()
    
    
    plt.figure(figsize=(10, 6))
    sector_counts.plot(kind='bar')
    plt.title('Sector Distribution in Portfolio')
    plt.xlabel('Sectors')
    plt.ylabel('Number of Assets')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
def plot_portfolio_returns(returns):
    #fix
    """
    Plots the cumulative returns of the portfolio.
    
    Parameters:
    returns (Series): A pandas Series containing cumulative returns.
    
    Returns:
    None
    """
    cumulative_returns = (1 + returns).cumprod() - 1
     
    plt.figure(figsize=(10, 6))
    cumulative_returns.plot(title='Cumulative Portfolio Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.grid(True)
    plt.show()
    
def plot_portfolio_return_volatility(returns, rolling_window=30):
    #fix
    """
    Plots the rolling volatility of the portfolio returns.
    
    Parameters:
    returns (Series): A pandas Series containing daily returns.
    rolling_window (int): The window size for calculating rolling volatility.
    
    Returns:
    None
    """
    
    rolling_volatility = returns.rolling(window=rolling_window).std()
    
    plt.figure(figsize=(10, 6))
    rolling_volatility.plot(title='Rolling Volatility of Portfolio Returns')
    plt.xlabel('Date')
    plt.ylabel('Volatility')
    plt.grid(True)
    plt.show()

def plot_portfolio_value(data, portfolio, start_date=None, end_date=None):
    """         
    Plots the value of the portfolio over time.
    
    Parameters:
    data (DataFrame): A DataFrame containing the portfolio data with 'Close' prices.
    portfolio (dict): A dictionary with tickers as keys and weights as values.
    start_date (str or pd.Timestamp): Start date for the plot (optional).
    end_date (str or pd.Timestamp): End date for the plot (optional).
    
    Returns:
    None
    """
    if start_date:
        data = data.loc[data.index >= pd.to_datetime(start_date)]
    if end_date:
        data = data.loc[data.index <= pd.to_datetime(end_date)]
    
    close_prices = pd.DataFrame({ticker: data[(ticker, 'Close')] for ticker in portfolio})
    
    # Calculate portfolio value over time
    portfolio_value = close_prices.mul(pd.Series(portfolio), axis=1).sum(axis=1)
    
    plt.figure(figsize=(10, 6))
    portfolio_value.plot(title='Portfolio Value Over Time')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value')
    plt.grid(True)
    plt.show()