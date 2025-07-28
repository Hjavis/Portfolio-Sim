import numpy as np
import pandas as pd
import scipy.stats as stats
from typing import Tuple, Optional


class RiskMetrics:
    """Risk Metrics calculator for portfolio analysis
    All calculations are designed to work with daily returns by default
    """

    def __init__(self, returns: pd.Series, risk_free_rate: float = 0.025):
        """
        Initialize with return series and optional risk-free rate
        
        Args:
            returns: Pandas Series of portfolio returns
            risk_free_rate: Annualized risk-free rate (default Danish Goverment Bond)
        """
            

        self.returns = returns.dropna()
        self.risk_free_rate = risk_free_rate
        self._annual_factor = np.sqrt(251)

    def annualized_return(self) -> float:
        """Calculate annualized return from daily returns"""
        return (1 + self.returns).prod() ** (251/len(self.returns)) - 1
    
    def annualized_volatility(self) -> float:
        """Calculate annualized volatility from daily returns"""
        #volatilitet er sigma * sqrt(t), hvor t = tid i markedsdage 
        return self.returns.std() * self._annual_factor
    
    def sharpe_ratio(self) -> float:
        """Calculate annualized Sharpe ratio
        Sharpe_ratio = (expected[returns]-risk_free_rate) / sigma[returns]"""

        delta = self.annualized_return() - self.risk_free_rate 
        return delta / self.annualized_volatility()
    
    def value_at_risk(self, alpha: float = 0.05, method: str = 'historical') -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            alpha: Confidence level (e.g., 0.05 for 95% VaR)
            method: 'historical' or 'parametric' (normal distribution)
            
        Returns:
            VaR as positive number (loss amount)
        """
        if not 0 < alpha < 1:
            raise ValueError('alpha must be between 0 and 1, example: 0.05 = 5%')
        if method == 'historical':
            return -np.percentile(self.returns, alpha * 100)
        elif method == 'parametric':
            return -(self.returns.mean() + self.returns.std() * stats.norm.ppf(alpha))
        else:
            raise ValueError("Method must be 'historical' or 'parametric'")
        

        
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
    
