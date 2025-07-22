import pandas as pd
import matplotlib.pyplot as plt

class Portfolio:
    def __init__(self, name, data, starting_cash=100000):
        self.name = name
        self.starting_cash = starting_cash
        self.current_cash = starting_cash
        self.data = data
        self.assets = {}
        self.log = []
        
    def __str__(self):
        """
        Returns a string representation of the current portfolio.
        """
        output = [f"\nPortfolio: {self.name}"]
        tickers = self.data.columns.levels[0]

        for ticker in self.assets:
            try:
                sector = self.data[(ticker, 'Sector')].dropna().iloc[0] if 'Sector' in self.data[ticker] else 'Unknown'
            except:
                sector = 'Unknown'
            shares = self.assets[ticker]
            output.append(f"{ticker} - Sector: {sector}, Shares: {shares}")

        output.append(f"Current Cash: {self.current_cash:.2f}")
        output.append(f"Total Portfolio Value: {self.get_portfolio_value():.2f}")
        return "\n".join(output)
    
    def __repr__(self):
        return f"Portfolio(name='{self.name}', cash={self.current_cash:.2f}, holdings={len(self.assets)})"

    def buy_asset(self, ticker, quantity, at_date=None, open=False):
        """_summary_

        Args:
            ticker (_type_): Stock ticker symbol to buy
            quantity (_type_): Number of shares to buy
            at_date (str, optional): Date to buy the asset. If None, uses the last date in data.
            open (bool, optional): If True, buys at the open price of the day. Defaults to False, which buys at close price.
        """
        if at_date: #Hvis bestemt dato skal bruges
            buy_date = pd.to_datetime(at_date)
            if buy_date not in self.data.index:
                print(f"Date {at_date} not found in data.")
                next_dates = self.data.index[self.data.index > buy_date]
                if len(next_dates) == 0:
                    print(f"No future dates available in data after {at_date}.")
                    return
                buy_date = next_dates[0]
                print(f"Using next available date: {buy_date.date()}")
        else: #Hvis ingen dato er bestemt, bruges den sidste dato i data
            buy_date = self.data.index[-1]
        
        if open: #Hvis open er True, bruges åbningskursen
            price = self.data.loc[buy_date, (ticker, 'Open')]
        else: #Hvis open er False, bruges lukkeprisen
            price = self.data.loc[buy_date, (ticker, 'Close')]
        total_cost = price * quantity
        if total_cost > self.current_cash:
            print(f"Not enough cash to buy {quantity} shares of {ticker}.")
            return
        self.current_cash -= total_cost
        self.assets[ticker] = self.assets.get(ticker, 0) + quantity 
        
        # Log handlen
        self.log_transaction('Buy', buy_date, ticker, quantity, price, total_cost)

        
        print(f"Bought {quantity} shares of {ticker}, at {price} per share. Current holdings: {self.assets[ticker]} shares.")
        
    def sell_asset(self, ticker, quantity, at_date=None, open=False):
        """_summary_

        Args:
            ticker (_type_): Stock ticker symbol to sell
            quantity (_type_): Number of shares to sell
            at_date (str, optional): Date to sell the asset. If None, uses the last date in data.
            open (bool, optional): If True, sells at the open price of the day. Defaults to False, which sells at close price.
        """
        if ticker not in self.assets or self.assets[ticker] < quantity:
            print(f"Not enough shares of {ticker} to sell.")
            return
        
        if at_date: #Hvis bestemt dato skal bruges
            sell_date = pd.to_datetime(at_date)
            if sell_date not in self.data.index:
                print(f"Date {at_date} not found in data.")
                next_dates = self.data.index[self.data.index > sell_date]
                if len(next_dates) == 0:
                    print(f"No future dates available in data after {at_date}.")
                    return
                sell_date = next_dates[0]
                print(f"Using next available date: {sell_date.date()}")
        
        else: #Hvis ingen dato er bestemt, bruges den sidste dato i data
            sell_date = self.data.index[-1]
            
        if open: #Hvis open er True, bruges åbningskursen
            price = self.data.loc[sell_date, (ticker, 'Open')]
        else: #Hvis open er False, bruges lukkeprisen
            price = self.data.loc[sell_date, (ticker, 'Close')]
            
        total_revenue = price * quantity
        self.current_cash += total_revenue
        self.assets[ticker] -= quantity
        
        # Log handlen
        self.log_transaction('Sell', sell_date, ticker, quantity, price, total_revenue)
        
        
        print(f"Sold {quantity} shares of {ticker}, at {price} per share. Remaining holdings: {self.assets.get(ticker, 0)} shares.")
        if self.assets[ticker] == 0:
            del self.assets[ticker]
        
    def log_transaction(self, type_, date, ticker, quantity, price, total):
        self.log.append({
            'Type': type_,
            'Date': date,
            'Ticker': ticker,
            'Quantity': quantity,
            'Price': price,
            'Total': total
        })
        
    def get_portfolio_value(self):
        """Calculates the total value of the portfolio based on current prices."""
        total_value = self.current_cash
        for ticker, quantity in self.assets.items():
            if ticker in self.data.columns.levels[0]:
                price = self.data[(ticker, 'Close')].iloc[-1]
                total_value += price * quantity
        return total_value 
        
    def get_asset_quantity(self, ticker):
        """Returns the quantity of a specific asset in the portfolio."""
        return self.assets.get(ticker, 0)
    
    def get_current_cash(self):
        """Returns the current cash available in the portfolio."""
        return self.current_cash
    
    def get_asset_value(self, ticker):
        """Returns the value of a specific asset in the portfolio."""
        if ticker in self.assets:
            quantity = self.assets[ticker]
            price = self.data[(ticker, 'Close')].iloc[-1]
            return quantity * price

    def get_portfolio_log(self):
        """Returns the transaction log of the portfolio."""
        return pd.DataFrame(self.log)
    

    def reset_portfolio(self):
        """Resets the portfolio to its initial state."""
        self.current_cash = self.starting_cash
        self.assets = {}
        self.log = []
        print(f"Portfolio {self.name} has been reset.")    
    
    
 