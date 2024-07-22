import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_data_yfinance(symbol):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)  # Approximation for 52 weeks
    data = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
    return pd.DataFrame(data)

# Initialize an empty list to store DataFrames
df_list = []

# fetch data and append to list
def fetch_and_append(symbol):
    data = get_data_yfinance(symbol)
    data.insert(0, 'Symbol', symbol)  # Insert the 'Symbol' column at the first position
    df_list.append(data)

# iterate through each symbol in array
def fetch_stock_data(rsi_filtered_stocks):
    for symbol in rsi_filtered_stocks.keys():
        fetch_and_append(symbol)
    stock_data_df = pd.concat(df_list, ignore_index=True) # Concatenate all DataFrames in the list into a single DataFrame
    #stock_data_df.to_csv('combined_stock_data.csv', index=False) # for testing
    return(stock_data_df)




