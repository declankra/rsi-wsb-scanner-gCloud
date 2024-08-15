import aiohttp
import asyncio
import yfinance as yf
import pandas as pd
import numpy as np

# Function to calculate RSI
def calculate_rsi_vectorized(data, period):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# Asynchronous function to fetch data for a single symbol
async def fetch_data(session, symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1mo")
    return symbol, data

# Main function to fetch all data concurrently
async def fetch_all_data(symbols):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, symbol) for symbol in symbols]
        return await asyncio.gather(*tasks)

# Function to filter stocks by RSI
def filter_stocks_by_rsi(symbols, period, threshold):
    loop = asyncio.get_event_loop()
    stock_data = loop.run_until_complete(fetch_all_data(symbols))
    
    results = []
    for symbol, data in stock_data:
        if data is None or data.empty:
            continue
        if 'Close' in data.columns:
            rsi = calculate_rsi_vectorized(data['Close'], period)
            if not rsi.empty and rsi.iloc[-1] > threshold:
                results.append((symbol, rsi.iloc[-1]))
    
    return results

""""
# Example usage:
symbols = ['AAPL', 'MSFT', 'GOOGL']
period = 14
threshold = 70
filtered_stocks = filter_stocks_by_rsi(symbols, period, threshold)
print(filtered_stocks)
"""