### instead of fetching data for each symbol individually, yfinance allows for downloading of multiple symbols at once so we make "batch" requests
### instead of calculating rsi after each individual download, do vectorized calcs on entire series
### group_by = "ticker" organizes data download by symbol, making it easier to process each symbol's data (?)
### new stocks return errors: not all symbols imported have period > 1mo, which returns rror

import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

def calculate_rsi(data, period):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def fetch_and_calculate_rsi_batch(symbols, period, threshold):
    data = yf.download(symbols, period="1mo", group_by="ticker", progress=False)
    results = {}
    for symbol in symbols:
        if symbol in data.columns:
            symbol_data = data[symbol]['Close']
            if not symbol_data.empty:
                rsi = calculate_rsi(symbol_data, period)
                rsi_last = rsi.iloc[-1]
                if rsi_last > threshold:
                    results[symbol] = rsi_last
        else:
            print(f"Warning: No data available for {symbol}")
    return results

def rsiFilter(symbols, rsiPeriod, rsiThreshold):
    batch_size = 200  # Adjust this value based on your needs and API limitations
    results = {}
    
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        batch_results = fetch_and_calculate_rsi_batch(batch, rsiPeriod, rsiThreshold)
        results.update(batch_results)
    return results

