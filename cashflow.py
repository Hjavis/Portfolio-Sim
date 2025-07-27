from typing import Optional
from abc import ABC, abstractmethod
import pandas as pd

class CashFlow(ABC):
    """ abstract base class for all cash flows """
    def __init__(self, amount: float, date: Optional[str] = None, metadata: Optional[dict[str, any]] = None):
        self._amount = amount
        self.date = pd.to_datetime(date) if date else pd.Timestamp.now()
        self.metadata = metadata if metadata else {}
        self.applied = False
        
    @property
    def amount(self) -> float:
        """Type-safe getter for amount"""
        return self._amount
        
    @property
    def tax_rate(self) -> Optional[float]:
        """Type-safe getter for tax rate from metadata."""
        rate = self.metadata.get('tax_rate', None)
        if rate is not None and not 0 <= rate <= 1:
            raise ValueError("Tax rate must be between 0 and 1")
        return rate
    
    def amount_after_tax(self) -> tuple[float, Optional[float]]:
        """Calculates the amount after tax if a tax rate is provided in metadata."""
        if self.tax_rate is None:
            return self.amount, None
        
        tax = self.amount * self.tax_rate
        return self.amount - tax, tax    
      
    @abstractmethod
    def apply(self, portfolio) -> None:
         """ Applies the cash flow to the portfolio. Must be implemented by subclasses. """
         pass
        
    def _process_payment(self, 
                       portfolio, 
                       flow_type: str,
                       asset_id: str) -> None:
        """
        Protected helper method handling universal payment processing
        """
        if self.applied:
            raise ValueError("Cash flow has already been applied.")
        
        net_amount, tax = self.amount_after_tax()
        portfolio.adjust_cash(net_amount, at_date=self.date)
        self.applied = True
        
        log_msg = f"{flow_type} of {net_amount:.2f} applied to {asset_id}"
        if tax:
            log_msg += f" (tax: {tax:.2f})"
        print(log_msg)
                
    def __repr__(self):
        return f"{self.__class__.__name__}(amount={self.amount:.2f}, date={self.date}, metadata={self.metadata})"
    
    
                
class DividendCashFlow(CashFlow):
    """" Cashh flows from dividends"""
    def __init__(self, ticker, amount: float, date: Optional[str] =None, tax_rate: Optional[float] = None, payment_type: str = "ordinary"):
        super().__init__(amount, date, {
            'ticker': ticker,
            'tax_rate': tax_rate,
            'payment_type': payment_type
            })
        self.ticker = ticker
        
    def apply(self, portfolio):
        """Applies the dividend to the portfolio's cash."""
        if self.ticker not in portfolio.assets:
            raise ValueError(f"Ticker {self.ticker} not found in portfolio")

        
        self._process_payment(portfolio, "Dividend", self.ticker)

        
class DerivativeCashFlow(CashFlow):
    """
    Cash flow from derivative contracts (options, futures, etc.)
    """
    def __init__(self, contract_id: str, amount: float, date: Optional[str] = None, 
                 contract_type: str = "option", strike_price: Optional[float] = None, tax_rate: Optional[float] = None):
        super().__init__(amount, date, {
            'contract_id': contract_id,
            'contract_type': contract_type,
            'strike_price': strike_price,
            'tax_rate': tax_rate
        })
        self.contract_id = contract_id
        
    def apply(self, portfolio) -> None:
        """Apply derivative cash flow to portfolio"""
        self._process_payment(portfolio, f"{self.metadata['contract_type']} Derivative", self.contract_id)

class InterestCashFlow(CashFlow):
    """
    Cash flow from interest payments (bonds, savings, etc.)
    """
    def __init__(self, instrument_id: str, amount: float, date: Optional[str] = None,
                 rate: float = 0.0, accrual_period: str = "daily", tax_rate: Optional[float] = None):
        super().__init__(amount, date, {
            'instrument_id': instrument_id,
            'rate': rate,
            'accrual_period': accrual_period
        })
        self.instrument_id = instrument_id
        
    def apply(self, portfolio) -> None:
        """Apply interest payment to portfolio"""
        
        self._process_payment(
            portfolio=portfolio,
            flow_type="Interest",
            asset_id=self.instrument_id,
        )
            

class CashFlowManager:
    """
    Manages collection and application of cash flows
    """
    def __init__(self):
        self.cash_flows = []
        
    def add_cash_flow(self, cash_flow: CashFlow) -> None:
        """Add a cash flow to be processed"""
        self.cash_flows.append(cash_flow)
        
    def apply_cash_flows(self, portfolio, up_to_date: Optional[str] = None) -> None:
        """Apply all cash flows up to a certain date"""
        up_to_date = pd.to_datetime(up_to_date) if up_to_date else pd.Timestamp.now()
        
        for cf in sorted(self.cash_flows, key=lambda x: x.date):
            if cf.date <= up_to_date and not cf.applied:
                cf.apply(portfolio)
                
    def get_total_pending(self) -> float:
        """Get sum of all cash flows not yet applied"""
        return sum(cf.amount for cf in self.cash_flows if not cf.applied)
    
    def get_flows_by_type(self, flow_type: type) -> list:
        """Get all cash flows of a specific type"""
        return [cf for cf in self.cash_flows if isinstance(cf, flow_type)]