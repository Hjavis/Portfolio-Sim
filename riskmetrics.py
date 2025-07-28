import numpy as np
import pandas as pd
import scipy.stats as stats



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
    
    def value_at_risk(self, alpha: float = 0.05, method: str = 'parametric') -> float:
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
        
    def expected_shortfall(self, alpha: float = 0.05) -> float:
        """
        Calculate Expected Shortfall (CVaR)
        Average of losses beyond VaR
        """
        var = self.value_at_risk(alpha)
        return -self.returns[self.returns <= -var].mean()
        
    def risk_report(self) -> dict:
        """
        Generate comprehensive risk report
        """
        report = {
            'Annualized Return': self.annualized_return(),
            'Annualized Volatility': self.annualized_volatility(),
            'Sharpe Ratio': self.sharpe_ratio(),
            '95% VaR (Parametric)': self.value_at_risk(0.05, 'parametric'),
            '95% Expected Shortfall': self.expected_shortfall(0.05)}
        
        return report
