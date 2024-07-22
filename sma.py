# perDiffSmaP1, perDiffSmaP2, perDiffSmaP3 = sma(stockData, smaP1, smaP2, smaP3)

def calc_sma(data, sma):
    
    # Calculate the SMA values
    data[f'SMA_{sma}'] = data['Close'].rolling(window=sma).mean()
   
    # Extract the most recent row of data
    latest_data = data.iloc[-1]
    close_price = latest_data['Close']
    
    # Calculate the percentages
    perDiffSma = ((close_price - latest_data[f'SMA_{sma}']) / latest_data[f'SMA_{sma}']) * 100
    
    return perDiffSma

def sma(stockData, smaP1, smaP2, smaP3):
    
    perDiffSmaP1 = calc_sma(stockData, smaP1)
    perDiffSmaP2 = calc_sma(stockData, smaP2)
    perDiffSmaP3 = calc_sma(stockData, smaP3)

    return perDiffSmaP1, perDiffSmaP2, perDiffSmaP3