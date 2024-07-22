        ## perDiffVolP1, perDiffVolP2, perDiffVolP3 = volumeSpike(stockData, volP1, volP2, volP3)



def avg_volumes(data, days):
    volumes = data['Volume'].tail(days)
    average_volume = volumes.mean()
    return average_volume

def calc_volume(data, days):
    data = data
    recent_volume = data['Volume'].iloc[-1]
    avg_volume = avg_volumes(data, days)
    percent_diff = ((recent_volume - avg_volume) / avg_volume) * 100
    return percent_diff

def volumeSpike(stockData, volP1, volP2, volP3):
    perDiffVolP1 = calc_volume(stockData, volP1)
    perDiffVolP2 = calc_volume(stockData, volP2)
    perDiffVolP3 = calc_volume(stockData, volP3)
    
    return perDiffVolP1, perDiffVolP2, perDiffVolP3