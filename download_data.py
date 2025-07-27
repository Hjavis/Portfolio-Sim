import os
import pandas as pd
import yfinance as yf

local_save_path = 'data/yfinancedata.parquet'

#web scrape fra wikipedia
def fetch_sp500_tickers():
    "Returns tickers and sectors. List and dictornary mapping sectors to the tickers."

    sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp500['Symbol'] = sp500['Symbol'].str.replace(".", "-")
    tickers = sp500['Symbol'].tolist()
    sectors = dict(zip(sp500['Symbol'], sp500['GICS Sector']))
    return tickers, sectors

def download_and_save_data(tickers, sectors, save_path=local_save_path):
    if os.path.exists(save_path):
        print("Data already exists. Delete it to re-download.")
        return

    print("Downloading historical data...")
    data = yf.download(
        tickers, 
        start="2015-01-01", 
        end=pd.to_datetime('today').strftime("%Y-%m-%d"), 
        group_by='ticker',
        progress=False
    )

    sector_data = pd.DataFrame(
        { (ticker, 'Sector'): sectors.get(ticker, 'Unknown') for ticker in tickers },
        index=data.index
    )
    data = pd.concat([data, sector_data], axis=1)


    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    data.to_parquet(save_path)
    print(f"Data saved to {save_path}")

def load_data(file_path=local_save_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    return pd.read_parquet(file_path)
    
if __name__ == "__main__":
    tickers, sectors = fetch_sp500_tickers()
    data = load_data()
    print("Data downloaded successfully")
    print(data.head())
