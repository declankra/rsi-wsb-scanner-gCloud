### instead of fetching data for each symbol individually, yfinance allows for downloading of multiple symbols at once so we make "batch" requests
### instead of calculating rsi after each individual download, do vectorized calcs on entire series
### group_by = "ticker" organizes data download by symbol, making it easier to process each symbol's data (?)
### new stocks return errors: not all symbols imported have period > 1mo, which returns rror
### improved batch processing (for single and multiple symbol cases) and parallel processing using threadpoolexecutor
### try excep blocks for error handling

import time
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

def calculate_rsi_vectorized(data, period):
    # now uses pandas vectorized operations
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def fetch_and_calculate_rsi_batch(symbols, period, threshold):
    results = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1mo")
            if not data.empty and len(data) > period:
                rsi = calculate_rsi_vectorized(data['Close'], period)
                rsi_last = rsi.iloc[-1]
                if rsi_last > threshold:
                    results[symbol] = rsi_last
            else:
                print(f"Warning: Insufficient data for {symbol}")
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
    return results

def rsiFilter(symbols, rsiPeriod, rsiThreshold):
    batch_size = 50  # Reduced batch size to minimize potential errors
    results = {}
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            futures.append(executor.submit(fetch_and_calculate_rsi_batch, batch, rsiPeriod, rsiThreshold))
            time.sleep(1)  # Add a delay to avoid rate limiting
        
        for future in as_completed(futures):
            results.update(future.result())
    
    return results

""""
# Example usage
if __name__ == "__main__":
    symbols = ["MORF", "IMMR", "ZNTE", "ARDT", "PLD"]  # Add more symbols as needed
    rsi_period = 14
    rsi_threshold = 70
    
    filtered_symbols = rsiFilter(symbols, rsi_period, rsi_threshold)
    print("Filtered symbols:", filtered_symbols)
    print(f"Processed {len(symbols)} symbols, {len(filtered_symbols)} passed the RSI threshold.")
"""