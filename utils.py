import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
def plot_portfolio_value(self, start_date="2021-01-01", end_date=pd.Timestamp.today()):
        """
        Plots total portfolio value over time, accounting for changing holdings.

        Parameters:
        start_date (str or pd.Timestamp): Start date.
        end_date (str or pd.Timestamp): End date.

        Returns:
        None
        """
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        #filter data fra start til slutdato
        if start_date >= end_date:
            raise ValueError("Start date must be before end date.")
        
        date_range = self.data.loc[(self.data.index >= start_date) & (self.data.index <= end_date)].index

        # Ny dataframe til holdings
        holdings = pd.DataFrame(0, index=date_range, columns=self.data.columns.levels[0])

        # Benyt log til at opdatere holdings
        for tx in self.log:
            tx_date = pd.to_datetime(tx['Date'])
            if tx_date > end_date:
                continue
            if tx_date not in holdings.index:
                continue 

            ticker = tx['Ticker']
            qty = tx['Quantity'] if tx['Type'] == 'Buy' else -tx['Quantity']
            holdings.loc[tx_date:, ticker] += qty  #Opdatere holdings fra denne dato og fremad

        #Få Closeprices for alle relevante datoer
        close_prices = self.data.loc[date_range, pd.IndexSlice[:, 'Close']]
        close_prices.columns = close_prices.columns.droplevel(1)

    
        portfolio_value = (holdings * close_prices).sum(axis=1) + self.current_cash

    
        plt.figure(figsize=(10, 6))
        portfolio_value.plot(title=f"Portfolio Value Over Time ({self.name})")
        plt.xlabel("Date")
        plt.ylabel("Total Value")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
def plot_portfolio(portfolio):
    if not portfolio.assets:
        print("No holdings in the portfolio.")
        return

    tickers = list(portfolio.assets.keys())
    latest_prices = portfolio.data.loc[portfolio.data.index[-1]]

    weights = []
    labels = []

    for ticker in tickers:
        quantity = portfolio.assets[ticker]
        price = latest_prices[(ticker, 'Close')]
        value = quantity * price
        if value > 0 and np.isfinite(value):
            weights.append(value)
            labels.append(ticker)

    if not weights:
        print("No valid holdings to plot.")
        return

    plt.figure(figsize=(8, 6))
    plt.pie(weights, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('Portfolio Allocation')
    plt.axis('equal')
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
    
def plot_sector_distribution(portfolio):
    """
    Plots the sector distribution of the portfolio.
 
    Returns:
    None
    """
    tickers = portfolio.columns.levels[0]
    
    sectors = []
    for ticker in tickers:
        if ('Sector' in portfolio[ticker].columns):
            sector_val = portfolio[(ticker, 'Sector')].dropna().iloc[0]
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
    
def plot_sector_distribution_historic(portfolio, plot_date):
    """
    Plots the sector distribution of the portfolio at a specific date.
    
    Parameters:
    plot_date: The date for which to plot the sector distribution.
    
    Returns:
    None
    """
    plot_date = pd.to_datetime(plot_date)

    #nærmeste dato før eller på plot_date
    valid_dates = portfolio.index[portfolio.index <= plot_date]
    if len(valid_dates) == 0:
        print(f"No data available before {plot_date}")
        return
    date = valid_dates[-1]

    #find sektor for hver ticker
    sectors = []
    for ticker in portfolio.columns.levels[0]:
        if (ticker, 'Sector') in portfolio.columns:
            sector_val = portfolio.loc[date, (ticker, 'Sector')]
            sectors.append(sector_val)
    
    sector_counts = pd.Series(sectors).value_counts()
    
    plt.figure(figsize=(10, 6))
    sector_counts.plot(kind='bar')
    plt.title(f'Sector Distribution on {date.date()}')
    plt.xlabel('Sectors')
    plt.ylabel('Number of Assets')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
def verify_date_in_df(df: pd.DataFrame, date) -> pd.Timestamp:
    date = pd.to_datetime(date)
    if date in df.index:
        return date
    next_dates = df.index[df.index > date]
    if len(next_dates) == 0:
        raise ValueError(f"No valid date found after {date}.")
    return next_dates[0]
    
def get_time_interval(
    data: pd.DataFrame,
    start_date=None,
    end_date=None,
    verify_date=verify_date_in_df) -> tuple[pd.Timestamp, pd.Timestamp]:
    index = data.index
    
    if start_date is not None:
        start = verify_date(data, start_date)
    else:
        start = index[0]
        
    if end_date is not None:
        end_date = pd.to_datetime(end_date)
        if end_date in index:
            end = end_date
        else:
            prev_dates = index[index < end_date]
            if len(prev_dates) == 0:
                raise ValueError(f"No dates before {end_date} in data index.")
            end = prev_dates[-1]
    else:
        end = index[-1]
    
    if end < start:
        raise ValueError(f"End date {end} is before start date {start}.")
    
    return start, end
    

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
