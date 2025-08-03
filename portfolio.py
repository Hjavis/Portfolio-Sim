import pandas as pd
import numpy as np
from riskmetrics import RiskMetrics


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
        

    def buy_asset(self, ticker, quantity:int, at_date=None, open=False):
        """_summary_

        Args:
            ticker (_type_): Stock ticker symbol to buy
            quantity (_type_): Number of shares to buy
            at_date (str, optional): Date to buy the asset. If None, uses the last date in data.
            open (bool, optional): If True, buys at the open price of the day. Defaults to False, which buys at close price.
        """
        verified_date = self.verify_date(at_date)
        
        if open: #Hvis open er True, bruges åbningskursen
            price = self.data.loc[verified_date, (ticker, 'Open')]
        else: #Hvis open er False, bruges lukkeprisen
            price = self.data.loc[verified_date, (ticker, 'Close')]
        total_cost = price * quantity
        if total_cost > self.current_cash:
            print(f"Not enough cash to buy {quantity} shares of {ticker}.")
            return
        self.current_cash -= total_cost
        self.assets[ticker] = self.assets.get(ticker, 0) + quantity 
        
        # Log handlen
        self.log_transaction('Buy', verified_date, ticker, quantity, price, total_cost)

        
        print(f"Bought {quantity} shares of {ticker}, at {price} per share. Current holdings: {self.assets[ticker]} shares.")
        
    def sell_asset(self, ticker, quantity:int, at_date=None, open=False):
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
        
        verified_date = self.verify_date(at_date)
            
        if open: #Hvis open er True, bruges åbningskursen
            price = self.data.loc[verified_date, (ticker, 'Open')]
        else: #Hvis open er False, bruges lukkeprisen
            price = self.data.loc[verified_date, (ticker, 'Close')]
            
        total_revenue = price * quantity
        self.current_cash += total_revenue
        self.assets[ticker] -= quantity
        
        # Log handlen
        self.log_transaction('Sell', verified_date, ticker, quantity, price, total_revenue)
        
        
        print(f"Sold {quantity} shares of {ticker}, at {price} per share. Remaining holdings: {self.assets.get(ticker, 0)} shares.")
        if self.assets[ticker] == 0:
            del self.assets[ticker]
        
    def log_transaction(self, type_:str, date, ticker, quantity:int, price:float, total):
        if type_ == 'Buy':
            total = -abs(total) #altid negativt
        if type_ =='Sell':
            total = abs(total) #altid positvt

        self.log.append({
            'Type': type_,
            'Date': date,
            'Ticker': ticker,
            'Quantity': quantity,
            'Price': price,
            'Total': total
        })
        
    def get_portfolio_log(self):
        """Returns the transaction log of the portfolio."""
        return pd.DataFrame(self.log)
    
    def print_portfolio_log(self, n=5):
        log = self.get_portfolio_log()
        print(log.tail(n))
        
    def verify_date(self, date) -> pd.Timestamp:
        """Checks if the given date is in the data index, if not, returns the next available date."""
        if date not in self.data.index:
            print(f"Date {date} not found in data.")
            next_dates = self.data.index[self.data.index > date]
            if len(next_dates) == 0:
                print(f"No future dates available in data after {date}.")
                raise ValueError("No valid date found.")
            date = next_dates[0]
            print(f"Using next available date: {date.date()}")
        return date
    
        
    def get_portfolio_value(self) -> float:
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
        
    def portfolio_returns(self, start_date=None, end_date=None):
        """
        Calculate portfolio returns based on current holdings and price data.
        
        Args:
            start_date: Optional start date for the return series
            end_date: Optional end date for the return series
            
        Returns:
            pd.Series: Daily returns of the portfolio
        """
        # Filtrér
        data = self.data.copy()
        if start_date:
            data = data.loc[data.index >= pd.to_datetime(start_date)]
        if end_date:
            data = data.loc[data.index <= pd.to_datetime(end_date)]
        
        close_prices = data.xs('Close', level=1, axis=1)
        daily_returns = close_prices.pct_change().dropna()
        
        
        if daily_returns.empty:
            return pd.Series(dtype=float)
        
        # Beregn nuværende weights baseret på self.assets
        current_prices = {ticker: data[(ticker, 'Close')].iloc[-1] 
                        for ticker in self.assets}
        weights = {ticker: self.assets[ticker] * current_prices[ticker] 
                for ticker in self.assets}
        total_value = sum(weights.values())
        
        # 
        if total_value == 0:
            return pd.Series(0, index=daily_returns.index)
        
        # Normalisér weights
        weights = {t: w/total_value for t, w in weights.items()}
        # Match med deres respektive tickers
        valid_tickers = [t for t in weights.keys() if t in daily_returns.columns]
        
        #tag daglige returns enten positive eller negative for hver ticker, og gang dem med deres respektive vægt i porteføljen. ved at tage prikproduktet
        if valid_tickers:
            weights_series = pd.Series(weights)[valid_tickers]
            return daily_returns[valid_tickers].dot(weights_series)
        else:
            return pd.Series(0, index=daily_returns.index)
    

    def reset_portfolio(self):
        """Resets the portfolio to its initial state."""
        self.current_cash = self.starting_cash
        self.assets = {}
        self.log = []
        print(f"Portfolio {self.name} has been reset.")    
    
    def generate_random_portfolio(self, num_assets=30, max_shares = 200, start_date=None, end_date=None, random_seed=123):
        """Generates a random portfolio with a given number of assets."""
        #Filtrer data og set seed
        if start_date:
            self.data = self.data.loc[self.data.index >= pd.to_datetime(start_date)]
        if end_date:
            self.data = self.data.loc[self.data.index <= pd.to_datetime(end_date)]
        
        np.random.seed(random_seed)
        tickers = list(self.data.columns.levels[0])
        
        
        if num_assets > len(tickers):
            num_assets = len(tickers)
            
        chosen_tickers = np.random.choice(tickers, size=num_assets, replace = False)
        for ticker in chosen_tickers:
            quantity = np.random.randint(1, max_shares + 1)
            buy_date = np.random.choice(self.data.index)
            self.buy_asset(ticker, quantity, at_date=buy_date)
            

        
    
        
    def set_cash(self, amount:float, at_date=None):
        """Sets the current cash to a specific amount."""
        if amount < 0:
            print("Cash amount cannot be negative.")
            return
        difference = amount - self.current_cash
        self.current_cash = amount
        
        #log cash justering
        at_date = pd.to_datetime(at_date) if at_date else pd.Timestamp.now()
        self.log_transaction("Cash Adjustment", at_date, "CASH", 1, difference, difference)
        print(f"Current cash set to {self.current_cash:.2f}.")
    
    def adjust_cash(self, amount:float, at_date=None):
        """__summary__
        Adds or removes(-) a specific amount to the current cash and logs the transaction"""
        if self.current_cash + amount < 0:
            print("Insufficient cash to adjust by this amount.")
            return
        self.current_cash += amount
        
        #log cash justering
        at_date = pd.to_datetime(at_date) if at_date else pd.Timestamp.now()
       
        self.log_transaction("Cash Adjustment", at_date, "CASH", 1, amount, amount)
        
        print(f"Cash adjustet, new balance: {self.current_cash:.2f}.")
    
    def calculate_risk_metrics(self, risk_free_rate=0.0):
        """
        Calculate comprehensive risk metrics for the portfolio
        
        Args:
            benchmark_returns: Optional Series of benchmark returns
            risk_free_rate: Annual risk-free rate (default 0)
            
        Returns:
            Dictionary of risk metrics
        """
        returns = self.portfolio_returns()
        if returns.empty:
            raise ValueError("No returns data available")
            
        risk_calculator = RiskMetrics(returns, risk_free_rate)
        return risk_calculator.risk_report()    
 
    def print_risk_report(self, risk_free_rate=0.0):
            """Print formatted risk report"""
            report = self.calculate_risk_metrics(risk_free_rate)
            
            print("\n=== Portfolio Risk Report ===")
            print(f"Analysis Period: {self.data.index[0].date()} to {self.data.index[-1].date()}")
            print("-" * 50)
            
            for metric, value in report.items():
                if isinstance(value, float):
                    print(f"{metric:<25}: {value:.4f}")
                else:
                    print(f"{metric:<25}: {value}") 