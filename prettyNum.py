# incResult1, incResult2, incResult3, incResult4 = prettyNum(stockData, inc1, inc2, inc3, inc4, tol1, tol2, tol3, tol4)

def calc_results(data, inc, tol):
    close_price = data['Close'].iloc[-1]
    closeness = close_price % inc
    is_close = int(closeness < tol or (inc - closeness) < tol)
    return is_close

def prettyNum(stockData, inc1, inc2, inc3, inc4, tol1, tol2, tol3, tol4):
    
    incResult1 = calc_results(stockData, inc1, tol1)
    incResult2 = calc_results(stockData, inc2, tol2)
    incResult3 = calc_results(stockData, inc3, tol3)
    incResult4 = calc_results(stockData, inc4, tol4)

    return incResult1, incResult2, incResult3, incResult4