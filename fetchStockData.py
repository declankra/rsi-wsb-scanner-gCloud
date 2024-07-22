import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_data_yfinance(symbol):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)  # Approximation for 52 weeks
    data = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
    return pd.DataFrame(data)

def fetch_stock_data(symbol):
    data = get_data_yfinance(symbol)
    data.insert(0, 'Symbol', symbol)  # Insert the 'Symbol' column at the first position
    return data