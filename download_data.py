import os
import pandas as pd
import yfinance as yf

#web scrape fra wikipedia
link = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
tables = pd.read_html(link)
sp500 = tables[0]
sp500_tickers = sp500['Symbol'].tolist()

tickers = sp500_tickers  # altid brug tickers, ikke sp500 tickers eller c25 ticker osv. for kompatibilitet brug altid 'tickers'"

def download_and_save_data(save_path='Sim/tickerdata.csv'):
    if os.path.exists(save_path):
        print("Data already downloaded.")
        return  # Don’t download

    tickerdata = yf.download(tickers, start="2015-01-01", end="2025-07-23", group_by='ticker')

    sectors = {}
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            sectors[ticker] = info.get('sector', 'Unknown')
        except:
            sectors[ticker] = 'Unknown'

    sector_cols = []
    for ticker in tickers:
        if ticker in tickerdata.columns.levels[0]:
            sector_series = pd.Series([sectors[ticker]] * len(tickerdata.index), index=tickerdata.index)
            sector_df = pd.DataFrame({(ticker, 'Sector'): sector_series})
            sector_cols.append(sector_df)

    if sector_cols:
        sector_data = pd.concat(sector_cols, axis=1)
        tickerdata = pd.concat([tickerdata, sector_data], axis=1)

    new_cols = []
    for ticker in tickers:
        cols = [col for col in tickerdata[ticker].columns if col != 'Sector']
        cols.append('Sector')
        new_cols.extend([(ticker, col) for col in cols])

    tickerdata = tickerdata.reindex(columns=pd.MultiIndex.from_tuples(new_cols))

    os.makedirs('Sim', exist_ok=True)
    tickerdata.to_csv(save_path)
    print(f"Data saved to {save_path}")

def load_data(file_path='Sim/tickerdata.csv'):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    
    data = pd.read_csv(file_path, header=[0, 1], index_col=0, parse_dates=True)
    data.index = pd.to_datetime(data.index)
    return data 

