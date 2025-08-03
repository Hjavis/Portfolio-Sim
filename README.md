# PortfolioSim - Trading Strategy Backtesting Framework
A Python-based platform for backtesting trading strategies, analyzing portfolio performance, and simulating investment scenarios with multi-asset support.

## ✨ Key Features

- 📈 **Multi-Asset Portfolio Management** - Track stocks, cash positions, and transactions  
- 🤖 **Strategy Backtesting** - Test moving average, seasonal, pairs trading, and custom strategies  
- 📉 **Risk Analysis Tools** - Value-at-Risk (VaR), Sharpe ratio, and other risk metrics  
- 📊 **Performance Visualization** - Interactive charts for returns, allocations, and sector distribution  
- 💰 **Cash Flow Handling** - Comprehensive management of dividends, interest, and derivative flows  
- ⚡ **YFinance Integration** - Automatic S&P 500 data downloading with sector information  
- 🏆 **Summary & Benchmarks** - Compare strategies against buy-and-hold performance  

## 🛠 Core Functionality

| Component                | Description                                        | Status       |
|--------------------------|----------------------------------------------------|--------------|
| **Portfolio Tracking**   | Holdings, cash balance, transactions               | ✅ Stable     |
| **MA Cross Strategy**    | Moving average crossover backtest                  | ✅ Stable     |
| **Seasonal Strategy**    | "Sell in May" pattern implementation               | ✅ Stable     |
| **Pairs Trading**        | Cointegrated pairs trading strategy                | ✅ Stable     |
| **VaR Calculation**      | Historical and parametric Value-at-Risk            | ✅ Stable     |
| **Data Pipeline**        | Yahoo Finance integration with sector data         | ✅ Stable     |
| **Cash Flow Management** | Handle dividends, interest, and derivative flows   | ✅ Stable     |
| **Risk Metrics**         | Sharpe ratio, annualized return, volatility        | ✅ Stable     |
| **Monte Carlo Simulation**| Stochastic simulation for portfolio forecasting    | ❌ Not done yet |

## Example Usage

```python
# Example usage

# Load data
tickers, sectors = fetch_sp500_tickers()
download_and_save_data(tickers, sectors)
data = load_data()

# Create portfolio
pf = Portfolio(name="MyPortfolio", data=data, starting_cash=100000)

# Buy and sell assets
pf.buy_asset('AAPL', 10, at_date='2016-01-05')
pf.buy_asset('GOOGL', 155, at_date='2016-05-05')
pf.buy_asset('TSLA', 241, at_date='2018-04-15')
pf.buy_asset('NVDA', 41, at_date='2017-12-20')
pf.buy_asset('JPM', 115, at_date='2018-04-12')
pf.sell_asset('GOOGL', 100, at_date='2025-07-13')

# Check portfolio value and log
print(pf.get_portfolio_value())
pf.print_portfolio_log(10)

# Portfolio metrics
return_series = portfolio_returns(pf)

# Risk analysis
riskpf = RiskMetrics(return_series)
VaR_Historical = riskpf.value_at_risk(alpha=0.05, method='historical')
VaR_Parametric = riskpf.value_at_risk(alpha=0.05, method='parametric')
print(f'VaR according to historical: {VaR_Historical:.2%}, VaR according to parametric: {VaR_Parametric:.2%}')

# Get risk report
pf.print_risk_report()

# Realised and unrealised profit and loss
realisedpnl, unrealisedpnl = portfolio_pnl(pf)
print(f'Realised PnL: {realisedpnl}, Unrealised PnL: {unrealisedpnl}')

# Visualize portfolio and returns
plot_portfolio(pf)
plot_returns(return_series)

# Backtest strategies
pf.reset_portfolio()
pfbacktest = BackTester(pf)
pfbacktest.moving_average_strategy_full('AAPL', window=30)
pfbacktest.sell_in_may_and_go_away_strategy_full('TSLA')

# Test cash flow system
pf.buy_asset('KO', at_date='2024-01-01', quantity=4)
Divcf = DividendCashFlow(amount=100, ticker='KO', date='2024-03-03', tax_rate=0.27)
Divcf.apply(pf)

# Cash flow is automatically logged
pf.print_portfolio_log()

# Use CashFlowManager
cfm = CashFlowManager()
cfm.add_cash_flow(DividendCashFlow(amount=750, ticker='KO', date='2023-03-03', tax_rate=0.27))
cfm.add_cash_flow(InterestCashFlow('ID:123', 52.5, '2025-01-03'))
cfm.add_cash_flow(DerivativeCashFlow('OPT_AAPL_20231212_C170', strike_price=170, amount=5734, date='2023-12-12'))
cfm.add_cash_flow(DividendCashFlow(amount=1337, ticker='KO', date='2026-03-03', tax_rate=0.27))

# Print CashFlowManager
cfm.print_cash_flow_manager()

# Apply cash flows up to today
cfm.apply_cash_flows(pf, up_to_date=pd.to_datetime('today'))
cfm.print_cash_flow_manager()

# Filter cash flows by type
derivcf = cfm.get_flows_by_type(DerivativeCashFlow)
dividendcf = cfm.get_flows_by_type(DividendCashFlow)
```

## ⚠️ Current Limitations & Upcoming Fixes

- **Data Validation**         
  - 🧩 Enhanced data validation for missing or invalid data  
- **Transaction Costs**          
  - 💸 Basic transaction cost modeling (fees/slippage to be added)  
- **Inflation Adjustment**   
  - 💹 No inflation/currency adjustment yet  
- **Risk-Adjusted Metrics**           
  - 📐 Additional metrics like Sortino ratio planned  
- **Monte Carlo Simulation**  
  - 🎲 Stochastic simulation for portfolio forecasting in progress




noter til mig selv
utils
def plot_portfolio_return_volatility(returns, rolling_window=30):
    #skal bruge et fix

randomwalk(skal laves ordenligt, dårlig autocomplete er ikke engang integreret endnu)

cashflow discount, 

def first_portfolio_activity og set som default på mange utils og metrics

