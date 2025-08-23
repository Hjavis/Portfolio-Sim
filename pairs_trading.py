from ftplib import all_errors
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
from statsmodels.tsa.stattools import coint
import pandas as pd
import numpy as np


def find_cointegrated_pairs(data, tickers, significance=0.05):
    """Find cointegrated pairs in a list of time series data.
    Args:
        data (list): List of time series data
        tickers (list): List of tickers O(n^2) tidskompleksitet
        significance (float, optional): Significance level for cointegration. Defaults to 0.05.
    """
    
    if len(tickers) > 80:
        raise ValueError("Dont. 80 tickers is reasonable maximum due to time complexity")
        
    n = len(tickers) 
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            t1, t2 = tickers[i], tickers[j]
            s1 = data[(t1, 'Close')]
            s2 = data[(t2, 'Close')]
            
            all_common_idx = s1.index.intersection(s2.index)
            s1_common = s1.loc[all_common_idx]
            s2_common = s2.loc[all_common_idx]
            
            # Fjerner de SAMME datoer fra begge serier. forhåbentlig sikrer at det ikke er misaligned
            mask = (~s1_common.isna()) & (~s2_common.isna()) & (~np.isinf(s1_common)) & (~np.isinf(s2_common))
            s1_clean = s1_common[mask]  
            s2_clean = s2_common[mask]
            
            if len(s1_clean) < 100:  # skip hvis ikke nok overlap
                continue
            if s1_clean.iloc[0] == 0 or s2_clean.iloc[0] == 0:
                continue  # Skip hvis prisen er 0
            
            s1_norm = s1_clean / s1_clean.iloc[0]
            s2_norm = s2_clean / s2_clean.iloc[0]
            
            pvalue = test_cointegration(s1_norm, s2_norm)
            if pvalue < significance:
                pairs.append((t1, t2, pvalue))
    return sorted(pairs, key=lambda x: x[2]) #sortere efter p-værdi (key = p-værdi) eksempel: ('AAPL', 'MSFT', 0.01) laveste p-værdi først


def test_cointegration(series1, series2) -> float:
    """ Tests cointegration and returns pvalue as a float"""
    score, pvalue, crit_value = coint(series1, series2)
    return pvalue

def compute_spread(series1, series2):
    if isinstance(series1, pd.DataFrame):
        series1 = series1.squeeze()
    if isinstance(series2, pd.DataFrame):
        series2 = series2.squeeze()
        
    #samme index please
    common_idx = series1.index.intersection(series2.index)
    series1 = series1.loc[common_idx]
    series2 = series2.loc[common_idx]
    
    mask = (~series1.isna()) & (~series2.isna()) & (~np.isinf(series1)) & (~np.isinf(series2))
    if mask.sum() == 0:
        raise ValueError("No valid data after cleaning")
    
    series1_clean = series1.loc[mask]
    series2_clean = series2.loc[mask]
    
    if series1_clean.iloc[0] == 0 or series2_clean.iloc[0] == 0:
        raise ValueError("Zero price at start")
    series1_norm = series1_clean / series1_clean.iloc[0]
    series2_norm = series2_clean / series2_clean.iloc[0]
   
    
    X = add_constant(series2_norm) # så modellen ikke tvinges gennem origo
    
    # Lineær regression af series1 på series2+constant for at få hedge ratio (beta) og skæring med y aksen(alpha)
    model = OLS(series1_norm, X).fit() 
    
    
    alpha = model.params.iloc[0] #skæringspunkt med y-aksen
    beta = model.params.iloc[1] #hældningskoefficienten, hvor meget series1 ændrer sig når series2 ændrer sig med 1

    spread_series = series1_norm - (beta * series2_norm + alpha) #spredning/residualerne
    return spread_series, beta

def generate_pairs_trading_signals(series1, series2, beta, zscore, z_entry=2.0, z_exit=0.5) -> pd.DataFrame:
    """
    Generates trading signals and positions for a pair based on zscore.
    Returns and DataFrame with signal, positions and returns.
    
    zscore (series) = Standardized spread values between series1 and series2
    """
    
    # FØRST sikre at alle serier har samme index
    common_idx = zscore.index.intersection(series1.index).intersection(series2.index)
    
    if len(common_idx) == 0:
        raise ValueError("No common index between zscore, series1 and series2")
    
    zscore = zscore.loc[common_idx]
    series1 = series1.loc[common_idx]
    series2 = series2.loc[common_idx]
    
    tradesignal = pd.DataFrame(index=zscore.index)
    tradesignal['zscore'] = zscore.astype(float)
    tradesignal['signal'] = 0
    tradesignal['pos1'] = 0.0
    tradesignal['pos2'] = 0.0
    tradesignal['returns'] = 0.0
    tradesignal['daily_returns'] = 0.0
    in_long = False
    in_short = False
    
    for i in range(len(tradesignal)):
        current_zscore = zscore.iloc[i]
        if not in_long and not in_short:
            if current_zscore < -z_entry:
                in_long = True
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = 1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = 1.0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = -float(beta)
            elif current_zscore > z_entry:
                in_short = True
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = -1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = -1.0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = float(beta)
        elif in_long:
            if abs(current_zscore) < z_exit:
                in_long = False
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = 0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = 0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = 0
            else:
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = 1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = 1.0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = -float(beta)
        elif in_short:
            if abs(current_zscore) < z_exit:
                in_short = False
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = 0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = 0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = 0
            else:
                tradesignal.iloc[i, tradesignal.columns.get_loc('signal')] = -1
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos1')] = -1.0
                tradesignal.iloc[i, tradesignal.columns.get_loc('pos2')] = float(beta)

    # Beregn afkast brug close-to-close returns
    ret1 = series1.pct_change().fillna(0)
    ret2 = series2.pct_change().fillna(0)
    
    # Positionsvægte fra dagen før (vi handler på close, så positionen etableres ved næste dags åbning)
    pos1_shifted = tradesignal['pos1'].shift(1).fillna(0)
    pos2_shifted = tradesignal['pos2'].shift(1).fillna(0)
    
    daily_returns = (pos1_shifted * ret1 + pos2_shifted * ret2)
    tradesignal['returns'] = daily_returns.astype(float)
    tradesignal['comulative_returns'] = (1 + daily_returns).cumprod() - 1
    
    return tradesignal

