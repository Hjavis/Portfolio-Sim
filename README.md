# PortfolioSim - Trading Strategy Backtesting Framework
A Python-based platform for backtesting trading strategies, analyzing portfolio performance, and simulating investment scenarios with multi-asset support.

## ✨ Key Features

- 📈 **Multi-Asset Portfolio Management** - Track stocks, cash positions, and transactions  
- 🤖 **Strategy Backtesting** - Test moving average, seasonal, and custom strategies  
- 📉 **Risk Analysis** - Value-at-Risk (VaR) and basic risk metrics  
- 📊 **Performance Visualization** - Interactive charts for returns and allocations 
- 💰 **Cash Flow Handling** - Cash flow managing system 
- ⚡ **YFinance Integration** - Automatic S&P 500 data downloading  
- 🏆 **Summary & Benchmarks** - Compare strategies against buy-hold performance  

## 🛠 Core Functionality

| Component            | Description                              | Status       |
|----------------------|------------------------------------------|--------------|
| **Portfolio Tracking** | Holdings, cash balance, transactions   | ✅ Stable     |
| **MA Cross Strategy** | Moving average crossover backtest       | ✅ Stable     |
| **Seasonal Strategy** | "Sell in May" pattern implementation    | ✅ Stable     |
| **VaR Calculation**   | Historical Value-at-Risk                | ✅ Stable     |
| **Data Pipeline**     | Yahoo Finance integration               | ✅ Stable     |
| **Montecarlo&stochastic**     | Soon to be implemented   |  ❌ Not done yet   |


## Example usage
 ```python
#Eksempel på brug

#Data
tickers, sectors= fetch_sp500_tickers()
download_and_save_data(tickers,sectors)
data = load_data()

#Opret din portefølje
pf = Portfolio(name="Hja", data=data, starting_cash=100000)

#Buy sell
pf.buy_asset('AAPL', 10, at_date='2016-01-05')
pf.buy_asset('GOOGL', 155, at_date='2016-05-05')
pf.buy_asset('TSLA', 241, at_date='2018-04-15')
pf.buy_asset('NVDA', 41, at_date='2017-12-20')
pf.buy_asset('JPM', 115, at_date='2018-04-12')

pf.sell_asset('GOOGL', 100, at_date='2025-07-13') 

#Tjek log og portefølje værdi
print(pf.get_portfolio_value())
pf.print_portfolio_log(10)

#portefølje metrics
return_series_daily = portfolio_returns(pf)

#Brug metrics til at enkelte risiko vurderinger.
return_series = portfolio_returns(pf)
riskpf = RiskMetrics(return_series)

VaR_Historical = riskpf.value_at_risk(alpha = 0.05, method='historical')
VaR_Parametric = riskpf.value_at_risk(alpha = 0.05, method='parametric')

#Tjek efter forskel på var med normalfordeling og den historiske
print(f'VaR according to historical_var {VaR_Historical:.2%}, VaR according to parametric approach {VaR_Parametric:.2%}')

#få en risiko rapport 
pf.print_risk_report()

#realised og unrealised profit and loss
realisedpnl, unrealisedpnl = portfolio_pnl(pf)
print(f'Realised PnL : {realisedpnl}, Unrealised PnL: {unrealisedpnl}')

return_float = portfolio_return_float(pf, start_date='2020-01-01', end_date='2025-01-01')
print(return_float)


#Visualiser portefølje, returns og mere med utils
plot_portfolio(pf)
plot_returns(return_series)

#Backtest indbygget strategier
pf.reset_portfolio()

pfbacktest = BackTester(pf)
pfbacktest.moving_average_strategy_full('AAPL', window=30)
pfbacktest.sell_in_may_and_go_away_strategy_full('TSLA')

print(pf.get_portfolio_value())
pf.print_portfolio_log(25)

#Test CashFlow systemet
pf.buy_asset('KO', at_date='2024-01-01', quantity=4)
Divcf = DividendCashFlow(amount=100, ticker='KO', date='2024-03-03', tax_rate=0.27)
Divcf.apply(pf)

#CashFlow bliver automatisk logget
pf.print_portfolio_log()

#Brug CashFlow Manager
cf1 = DividendCashFlow(amount=750, ticker='KO', date='2023-03-03', tax_rate=0.27)
cf2 = InterestCashFlow('ID:123', 52.5, '2025-01-03')
cf3 = DerivativeCashFlow('OPT_AAPL_20231212_C170', strike_price= 170, amount=5734, date='2023-12-12')
cf4 = DividendCashFlow(amount=1337, ticker='KO', date='2026-03-03', tax_rate=0.27)

#lav en CFM som kan holde styr på cashflows til vores portefølje "pf", eller hvilken som helst anden.
pf_cfm = CashFlowManager()
pf_cfm.add_cash_flow(cf1)
pf_cfm.add_cash_flow(cf2)
pf_cfm.add_cash_flow(cf3)
pf_cfm.add_cash_flow(cf4)

#Print CashFlowManager
pf_cfm.print_cash_flow_manager()


#Apply alle, pånær cf4 som først er i 2026
pf_cfm.apply_cash_flows(pf, up_to_date=pd.to_datetime('today'))
pf_cfm.print_cash_flow_manager()

#filtrér cashflows udfra type
derivcf = pf_cfm.get_flows_by_type(DerivativeCashFlow)
dividendcf = pf_cfm.get_flows_by_type(DividendCashFlow)
``` 

## ⚠️ Current Limitations & Upcomming fixes
**Data Validation**         
🧩 Basic data validation needs improvement

**Transaction Costs**          
💸 Simplified transaction costs (no fees/slippage modeling)

**Inflation Adjustment**   
💹 No inflation/currency adjustment

**Risk adjusted performance metric**           
📐 Missing risk-adjusted metrics







noter til mig selv
utils
def plot_portfolio_return_volatility(returns, rolling_window=30):
    #skal bruge et fix

randomwalk(skal laves ordenligt, dårlig autocomplete er ikke engang integreret endnu)

cashflow discount, 

def first_portfolio_activity og set som default på mange utils og metrics

