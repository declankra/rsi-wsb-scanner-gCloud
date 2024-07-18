import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed


def calculate_rsi(data, period): # rsi value from google sheet OR 14 day period by default
    delta = data['Close'].diff(1)
    avg_gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    avg_loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def fetch_and_calculate_rsi(symbols, period, threshold):
    rsi_values = {}
    print("Fetching stock data and calculating RSI to create list")
    for symbol in symbols:
        try:
            data = yf.download(symbol, period="1mo", progress = False)
            if not data.empty:
                rsi = calculate_rsi(data, period)
                rsi_last = rsi.iloc[-1]
                if rsi_last > threshold:  # Check if RSI is above the threshold
                    rsi_values[symbol] = rsi_last
            else:
                rsi_values[symbol] = None
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            rsi_values[symbol] = None
    return rsi_values


def rsiFilter(symbols, rsiPeriod, rsiThreshold):
    rsi_values = fetch_and_calculate_rsi(symbols, rsiPeriod, rsiThreshold)
    return rsi_values


""""
def fetch_and_calculate_rsi_single(symbol, period, threshold):
    try:
        data = yf.download(symbol, period="1mo", progress=False)
        if data.empty:
            print(f"Warning: No data available for {symbol}")
            return symbol, None
        rsi = calculate_rsi(data, period)
        rsi_last = rsi.iloc[-1]
        if rsi_last > threshold:
            return symbol, rsi_last
    except Exception as e:
        print(f"Error processing {symbol}: {str(e)}")
    return symbol, None

def fetch_and_calculate_rsi(symbols, period, threshold):
    rsi_values = {}
    print("Fetching stock data and calculating RSI to create list")
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_and_calculate_rsi_single, symbol, period, threshold) for symbol in symbols]
        for future in as_completed(futures):
            symbol, rsi_value = future.result()
            if rsi_value is not None:
                rsi_values[symbol] = rsi_value
    return rsi_values

"""