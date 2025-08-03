from ftplib import all_errors
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
from statsmodels.tsa.stattools import coint
import pandas as pd
#Prototype

def find_cointegrated_pairs(data, tickers, significance=0.05):
    """Find cointegrated pairs in a list of time series data.
    Args:
        data (list): List of time series data
        tickers (list): List of tickers O(n^2) tidskompleksitet
        significance (float, optional): Significance level for cointegration. Defaults to 0.05.
    """
    n = len(tickers) 
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            t1, t2 = tickers[i], tickers[j]
            s1 = data[(t1, 'Close')].dropna()
            s2 = data[(t2, 'Close')].dropna()
            all_common_idx = s1.index.intersection(s2.index)
            if len(all_common_idx) < 100:  # skip hvis ikke nok overlap
                continue
            pvalue = test_cointegration(s1.loc[all_common_idx], s2.loc[all_common_idx])
            if pvalue < significance:
                pairs.append((t1, t2, pvalue))
    return sorted(pairs, key=lambda x: x[2]) #sortere efter p-værdi (key = p-værdi) eksempel: ('AAPL', 'MSFT', 0.01) laveste p-værdi først


def test_cointegration(series1, series2):
    score, pvalue, crit_value = coint(series1, series2)
    return pvalue  # p < 0.05 betyder cointegration


def compute_spread(series1, series2):
    # Lineær regression af series1 på series2 for at få hedge ratio (beta)
    X = add_constant(series2) # så modellen ikke tvinges gennem origo
    model = OLS(series1, X).fit() 
    
    
    alpha = model.params.iloc[0] #skæringspunkt med y-aksen
    beta = model.params.iloc[1] #hældningskoefficienten, hvor meget series1 ændrer sig når series2 ændrer sig med 1

    spread = series1 - (beta * series2 + alpha) #spredning/residualerne
    return spread, beta

def generate_pairs_trading_signals(series1, series2, beta, zscore, z_entry=2.0, z_exit=0.5) -> pd.DataFrame:
    """
    Generates trading signals and positions for a pair based on zscore.
    Returns and DataFrame with signal, positions and returns.
    """
    
    tradesignal = pd.DataFrame(index=zscore.index)
    tradesignal['zscore'] = zscore
    tradesignal['signal'] = 0
    tradesignal['pos1'] = 0
    tradesignal['pos2'] = 0
    tradesignal['pos2'] = tradesignal['pos2'].astype(float)    
    tradesignal['returns'] = 0.0

    in_long = False
    in_short = False
    for i in range(1, len(tradesignal)):
        current_zscore = zscore.iloc[i].item()  # Convert to scalar
        if not in_long and not in_short:
            if current_zscore < -z_entry:
                in_long = True
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = 1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = 1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = -beta
            elif current_zscore > z_entry:
                in_short = True
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = -1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = -1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = beta
        elif in_long:
            if abs(current_zscore) < z_exit:
                in_long = False
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = 0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = 0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = 0
            else:
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = 1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = 1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = -beta
        elif in_short:
            if abs(current_zscore) < z_exit:
                in_short = False
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = 0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = 0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = 0
            else:
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = -1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = -1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = beta

    # Beregn daglige afkast for strategien
    ret1 = series1.pct_change().fillna(0)
    ret2 = series2.pct_change().fillna(0)
    
    # Sikre at de har samme index.
    common_index = tradesignal.index.intersection(ret1.index).intersection(ret2.index)
    tradesignal = tradesignal.loc[common_index]
    ret1 = ret1.loc[common_index]
    ret2 = ret2.loc[common_index]
    
    
    pos1_shifted = tradesignal['pos1'].shift().fillna(0).astype(float)
    pos2_shifted = tradesignal['pos2'].shift().fillna(0).astype(float)
    ret1 = series1.pct_change().fillna(0).astype(float).squeeze()
    ret2 = series2.pct_change().fillna(0).astype(float).squeeze()

    
    #Afkast beregning
    returns_calc = pos1_shifted * ret1 + pos2_shifted * ret2
    tradesignal['returns'] = returns_calc

    return tradesignal

