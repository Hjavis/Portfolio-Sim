import numpy as np
import pandas as pd
import matplotlib.pyplot as plt     
from portfolio import Portfolio


class BackTester:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.initial_cash = portfolio.starting_cash
        
    def moving_average_strat(self, ticker, window: int = 30, start_date=None, end_date = None):
        """Backtests a MA-strategy on a given ticker in your portfolio"""
        if ticker not in self.portfolio.data.columns.get_level_values(0):
            raise ValueError(f'Ticker {ticker} was not found in portfolio data')
        
        data_series = self.portfolio.data[ticker]['Close'].loc[start_date:end_date]        
        ma = data_series.rolling(window).mean()
        
        tradesignal = pd.DataFrame(index=data_series.index)
        tradesignal['price'] = data_series
        tradesignal['ma'] = ma
        tradesignal['signal'] = 0 #0 = hold, 1=buy_asset, -1=sell_asset
        tradesignal['returns'] = tradesignal['price'].pct_change()

        #hvornår skal der gennemføres handler
        tradesignal['signal'][window:] = np.where(tradesignal['price'][window:] > tradesignal['ma'][window:], 1, -1)
        tradesignal['positions_change'] = tradesignal['signal'].diff() #Kigger efter hvornår der sker en ændring
        
       

        #simulere trades
        for idx, row in tradesignal.iterrows():
            if row['positions_change'] == 2: #skift fra -1 til 1 (køb)
                self.buy_max(ticker,row['price'],idx)
            elif row['positions_change'] == -2: #skift fra 1 til -1 (salg)
                self.sell_all(ticker,idx)
        return tradesignal
                    
    def sell_in_may_and_go_away_strategy(self, ticker, start_date = None, end_date=None):
        """Backtests the questionable strategy of selling in may, and then going away. A strategy my grandfather swears by"""
        if ticker not in self.portfolio.data.columns.get_level_values(0):
            raise ValueError(f'Ticker {ticker} was not found in portfolio data')
        
        data_series = self.portfolio.data[ticker]['Close'].loc[start_date:end_date]
        

        tradesignal = pd.DataFrame(index=data_series.index)
        tradesignal['price'] = data_series
        tradesignal['returns'] = tradesignal['price'].pct_change() #returns for hver dag

        #Sell in may and go away, køb igen 1. november
        ismay_to_oct = (tradesignal.index.month >= 5) & (tradesignal.index.month <= 10)

        #filtrer ved at typecast booleanmask som int
        tradesignal['signal'] = ismay_to_oct.astype(int)
        
        for idx, row in tradesignal.iterrows():
            if row['signal'] == 0: #Køb
                self.buy_max(ticker, row['price'], idx)
            if row['signal'] == 1: #Sælg
                self.sell_all(ticker, idx)
        return tradesignal
    

    def strategy_summary(self, ticker: str, initial_cash: float = None) -> None:
        """
        Prints a clean profitability summary of the strategy using the portfolio's transaction log.
        Compares against buy-and-hold"""
        if initial_cash is None:
            initial_cash = self.portfolio.starting_cash
        
        log_df = self.portfolio.get_portfolio_log()
        ticker_log = log_df[log_df['Ticker'] == ticker]
        
        # beregn strategy performance
        final_value = self.portfolio.get_portfolio_value()
        total_return = (final_value - initial_cash) / initial_cash * 100
        
        # Buy-and-hold sammenligning
        start_price = self.portfolio.data[ticker]['Close'].iloc[0]
        end_price = self.portfolio.data[ticker]['Close'].iloc[-1]
        bh_return = (end_price - start_price) / start_price * 100
        
        # Trading metrics
        n_trades = len(ticker_log)
        winning_trades = len(ticker_log[
        ((ticker_log['Type'] == 'Buy') & (ticker_log['Total'] < 0)) |  # Losses
        ((ticker_log['Type'] == 'Sell') & (ticker_log['Total'] > 0))   # Gains
            ])
        
        win_rate = winning_trades / n_trades * 100 if n_trades > 0 else 0
        
        print(f"\n{' MA Strategy Summary ':=^50}")
        print(f"Ticker: {ticker}")
        print(f"Period: {self.portfolio.data.index[0].date()} to {self.portfolio.data.index[-1].date()}")
        print("\nStrategy Performance:")
        print(f"- Initial Cash: ${initial_cash:,.2f}")
        print(f"- Final Value: ${final_value:,.2f}")
        print(f"- Total Return: {total_return:.2f}%")
        print(f"- Trades Executed: {n_trades}")
        print(f"- Win Rate: {win_rate:.1f}%")
        
        print("\nBenchmark (Buy-and-Hold):")
        print(f"- Buy Price: ${start_price:.2f}")
        print(f"- Sell Price: ${end_price:.2f}")
        print(f"- Total Return: {bh_return:.2f}%")
        
        print("\nComparison:")
        print(f"- Outperformance: {total_return - bh_return:.2f} percentage points")
        print("="*50) 
            
    def generate_performance_report(self, signals: pd.DataFrame, ticker: str):
        """
        Compares against buy-hold strategy"""
        strategy_returns = signals['returns'] * signals['signal'].shift(1)
        cumulative_strategy = (1 + strategy_returns).cumprod()  #kumuleret afkast fra strategien
        
        
        bh_prices = self.portfolio.data[ticker]['Close'].loc[signals.index]
        bh_returns = bh_prices.pct_change()
        cumulative_bh = (1 + bh_returns).cumprod()  # Kumuleret buy-and-hold
        
        
        plt.figure(figsize=(10,6))
        plt.plot(cumulative_strategy, label='MA-strategi', linewidth=2)
        plt.plot(cumulative_bh, label='Buy-and-Hold', linewidth=2, linestyle='--')
        plt.title(f'Performance: MA vs Buy-and-Hold ({ticker})')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Returns (1 = 100%)')
        plt.legend()
        plt.grid(True)
        plt.show()
        
    def moving_average_strategy_full(self, ticker, window:int):
        """one-click analysis wrapper function"""
        signals = self.moving_average_strat(ticker, window)
        self.strategy_summary(ticker, self.portfolio.starting_cash)
        self.generate_performance_report(signals, ticker)
        return signals
    
    def sell_in_may_and_go_away_strategy_full(self, ticker):
        signals = self.sell_in_may_and_go_away_strategy(ticker)
        self.strategy_summary(ticker, self.portfolio.starting_cash)
        self.generate_performance_report(signals, ticker)
        return signals
    
    def buy_max(self,ticker, price, date):
        max_shares = int(self.portfolio.current_cash / price)
        if max_shares > 0:
            self.portfolio.buy_asset(ticker, max_shares, at_date=date)

    def sell_all(self, ticker, date):
        shares = self.portfolio.get_asset_quantity(ticker)
        if shares > 0:
            self.portfolio.sell_asset(ticker,quantity=shares, at_date=date)