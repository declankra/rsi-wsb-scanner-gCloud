# stochSignal, perDiffStochThresh, stochIndicator = stoch(stockData, stochPeriod, stochThreshold)

def stoch(stockData, stochPeriod, stochThreshold):
    data = stockData
    threshold_value = stochThreshold
    
    # Calculate the Stochastic Oscillator
    low_min = data['Low'].rolling(window=stochPeriod).min()
    high_max = data['High'].rolling(window=stochPeriod).max()

    data['%K'] = (data['Close'] - low_min) * 100 / (high_max - low_min)
    data['%D'] = data['%K'].rolling(window=3).mean()
    data['slow_%D'] = data['%D'].rolling(window=3).mean()

    # Get the last values
    last_k = data['%K'].iloc[-1]
    fast_d = data['%D'].iloc[-1]
    slow_d = data['slow_%D'].iloc[-1]

    # Determine overbought signal based on fast %D and slow %D
    overbought_signal_fast_slow = 1 if fast_d < slow_d else 0

    # Determine the better sell signal based on %K and slow %D threshold analysis
    overbought_indicator = "None"
    percent_over_threshold = 0.0

    if last_k > threshold_value or slow_d > threshold_value:
        if last_k - threshold_value > slow_d - threshold_value:
            overbought_indicator = "%K"
            percent_over_threshold = (last_k - threshold_value) / threshold_value * 100
        else:
            overbought_indicator = "slow %D"
            percent_over_threshold = (slow_d - threshold_value) / threshold_value * 100

    stochSignal = overbought_signal_fast_slow
    stochIndicator = overbought_indicator
    perDiffStochThresh = percent_over_threshold

    return stochSignal, perDiffStochThresh, stochIndicator