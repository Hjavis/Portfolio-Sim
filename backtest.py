import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from pairs_trading import find_cointegrated_pairs, compute_spread, generate_pairs_trading_signals
from portfolio import Portfolio


class BackTester:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.initial_cash = portfolio.starting_cash
        
    def pairs_trading_strategy(self, tickers, start_date=None, end_date=None, significance = 0.05, z_entry=2.0, z_exit=0.5):
        """backtests pairs trading strategy, where ticker pairs can get traded independently from each other"""
        # Data validering og filtrering
        for ticker in tickers:
            if ticker not in self.portfolio.data.columns.get_level_values(0):
                raise ValueError(f'Ticker {ticker} was not found in portfolio data')
        data_filtered = self.portfolio.data.loc[start_date:end_date, pd.IndexSlice[tickers, 'Close']]
       
        pairs = find_cointegrated_pairs(data_filtered, tickers, significance = significance)
        results = {}  # dict til tradesignal og afkast for hvert par
        
        for t1, t2, pvalue in pairs:
            s1 = data_filtered[t1]
            s2 = data_filtered[t2]
          
            # spread og beta
            spread_series, beta = compute_spread(s1, s2)
            zscore_series = (spread_series - spread_series.mean()) / spread_series.std() 
            
            tradesignal = generate_pairs_trading_signals(s1, s2, beta, zscore_series, z_entry, z_exit)
            
            # Gem resultatet for dette par
            results[(t1, t2)] = tradesignal
        return results  # Dictionary: (t1, t2) -> tradesignal DataFrame
        
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
    
    def pairs_trading_strategy_summary(self, results: dict, initial_cash: float = None) -> None:
        """
        Prints a clean profitability summary of the pairs trading strategy.
        Compares against buy-and-hold for each pair.
        """
        if initial_cash is None:
            initial_cash = self.portfolio.starting_cash
        
        print(f"\n{' Pairs Trading Strategy Summary ':=^50}")
        print(f"Number of pairs found: {len(results)}")
        print(f"Period: {self.portfolio.data.index[0].date()} to {self.portfolio.data.index[-1].date()}")
        
        if len(results) == 0:
            print("No cointegrated pairs found in the given ticker list.")
            return
        
        total_return = 0
        for (t1, t2), tradesignal in results.items():
            # Calculate strategy performance for this pair
            pair_returns = tradesignal['returns']
            cumulative_return = (1 + pair_returns).prod() - 1
            
            # Buy-and-hold comparison for this pair
            s1 = self.portfolio.data[(t1, 'Close')].loc[tradesignal.index]
            s2 = self.portfolio.data[(t2, 'Close')].loc[tradesignal.index]
            bh_return_1 = (s1.iloc[-1] / s1.iloc[0]) - 1
            bh_return_2 = (s2.iloc[-1] / s2.iloc[0]) - 1
            bh_return_avg = (bh_return_1 + bh_return_2) / 2
            
            # Trading metrics
            n_trades = len(tradesignal[tradesignal['signal'] != 0])
            
            print(f"\nPair: {t1}-{t2}")
            print(f"- Strategy Return: {cumulative_return:.2%}")
            print(f"- Buy-and-Hold Return: {bh_return_avg:.2%}")
            print(f"- Outperformance: {cumulative_return - bh_return_avg:.2%} percentage points")
            print(f"- Number of trades: {n_trades}")
            
            total_return += cumulative_return
        
        print(f"\n{' Overall Performance ':-^30}")
        print(f"- Average pair return: {total_return/len(results):.2%}")
        print("="*50)

    def pairs_trading_strategy_full(self, tickers: list):
        """One-click analysis wrapper function for pairs trading"""
        results = self.pairs_trading_strategy(tickers)
        self.pairs_trading_strategy_summary(results, self.portfolio.starting_cash)
        return results
    
    def buy_max(self,ticker, price, date):
        max_shares = int(self.portfolio.current_cash / price)
        if max_shares > 0:
            self.portfolio.buy_asset(ticker, max_shares, at_date=date)

    def sell_all(self, ticker, date):
        shares = self.portfolio.get_asset_quantity(ticker)
        if shares > 0:
            self.portfolio.sell_asset(ticker,quantity=shares, at_date=date)