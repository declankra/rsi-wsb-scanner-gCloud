# perDiffUpBandP1, perDiffUpBandP2 = bbandUpperRel(stockData, bbandP1, bbandP2, numStdv)

def calc_upperRel(data, bband, numStdv):
    sma = data['Close'].rolling(window=bband).mean()
    std = data['Close'].rolling(window=bband).std()
        
    upper_band = sma + (std * numStdv)
    # lower_band = sma - (std * numStdv) # not needed  
    percent_above_upper = (data['Close'] - upper_band) / upper_band * 100
    return percent_above_upper.iloc[-1] # Return only the last value

def bbandUpperRel(stockData, bbandP1, bbandP2, numStdv):
    
    perDiffUpBandP1 = calc_upperRel(stockData, bbandP1, numStdv)
    perDiffUpBandP2 = calc_upperRel(stockData, bbandP2, numStdv)

    return perDiffUpBandP1, perDiffUpBandP2

