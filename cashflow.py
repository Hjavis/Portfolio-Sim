class CashFlow:
    def __init__(self, initial_cash=0.0):
        self.current_cash = initial_cash
        self.cash_flow_history = []

    def __repr__(self):
        return f"CashFlow(current_cash={self.current_cash:.2f})"

    def add_cash(self, amount: float, at_date=None):
        """Adds cash to the current cash balance."""
        if amount < 0 and abs(amount) > self.current_cash:
            raise ValueError("Insufficient cash to remove this amount.")
        
        self.current_cash += amount
        self.cash_flow_history.append((at_date, amount))
        
class dividend(CashFlow):
    def __init__(self, ticker, amount, at_date=None):
        super().__init__(amount)
        self.ticker = ticker
        self.at_date = pd.to_datetime(at_date) if at_date else pd.Timestamp.now()
    
    def __repr__(self):
        return f"Dividend(ticker={self.ticker}, amount={self.current_cash:.2f}, date={self.at_date})"
    
    def apply(self, portfolio):
        """Applies the dividend to the portfolio's cash."""
        portfolio.adjust_cash(self.current_cash, at_date=self.at_date)
        print(f"Dividend of {self.current_cash:.2f} applied for {self.ticker} on {self.at_date}."
              

)