import json
import yfinance as yf
import pandas as pd

def calculate_rsi(data, period=14): # 14 day rsi value
    delta = data['Close'].diff(1)
    avg_gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    avg_loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def rsiFilter(all_filtered_stocks, rsiPeriod, rsiThreshold):
    return