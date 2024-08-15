from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
import pandas as pd
import numpy as np
import logging

# Optimized function to calculate RSI using vectorized operations
def calculate_rsi_vectorized(data, period):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Function to fetch data and calculate RSI
def fetch_and_calculate_rsi(symbol, data, period, threshold):
    try:
        if data.empty:
            logging.warning(f"No data available for {symbol}")
            return None
        
        if 'Close' not in data.columns:
            logging.warning(f"'Close' column not found in data for {symbol}")
            return None
        
        close_data = data['Close']
        rsi = calculate_rsi_vectorized(close_data, period)
        rsi_last = rsi.iloc[-1]
        
        if rsi_last > threshold:
            return symbol, rsi_last
    except Exception as e:
        logging.error(f"Error processing {symbol}: {e}")
        return None

# Optimized function to fetch stock data in batches
def fetch_stock_data_batch(symbols):
    try:
        data = yf.download(symbols, period="1mo", group_by="ticker")
        return data
    except Exception as e:
        logging.error(f"Error fetching batch data: {e}")
        return None

# Main function to execute the filtering process
def rsi_filter(symbols, period, threshold):
    results = []
    
    # Fetch stock data for all symbols in a single batch
    stock_data = fetch_stock_data_batch(symbols)
    
    if stock_data is None:
        return results
    
    # Use ThreadPoolExecutor to process each symbol concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_symbol = {
            executor.submit(fetch_and_calculate_rsi, symbol, stock_data[symbol], period, threshold): symbol 
            for symbol in symbols
        }
        
        for future in as_completed(future_to_symbol):
            result = future.result()
            if result:
                results.append(result)
    
    return results
