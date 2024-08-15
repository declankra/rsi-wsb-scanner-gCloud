from datetime import datetime
from markupsafe import escape
from flask import request
import os
import pandas as pd
from stockScreener import stockScreener  # Import the function
from rsiFilterConcurrent4o import rsi_filter # Import the function
import json
import requests
from fetchStockData import fetch_stock_data
import numpy as np
from volumeSpike import volumeSpike
from sma import sma
from bbandUpperRel import bbandUpperRel
from stoch import stoch
from prettyNum import prettyNum
from strengthRedditSubmissions import strengthRedditSubmissions
from strengthRedditDailyComments import strengthRedditDailyComments
from flask import jsonify


### initialize runtime variables
# FM_API_KEY = os.getenv('FM_API_KEY')
FM_API_KEY = 'Ke0ioOh8J93IRZJc1UDaTHMJSsf0JIMg' # setting it publicly because fuck it, i can get a new one if needed

### entrance function: process user configured variables from google sheets
def getVariables(request):
    request_json = request.get_json(silent=True)
    if request_json and 'user_variables' and 'result_headers' and 'history_headers' in request_json: # check if legit
        user_variables = request_json['user_variables']
        result_headers = request_json['result_headers']
        history_headers = request_json['history_headers']
        print('sheet data received successfully')
        
        # Call the main processing function with the received variables
        gSheetsResultsDF, gSheetsHistoryDF = main_process(user_variables,result_headers,history_headers)
        
        
         # Ensure the DataFrames are in the correct order
        gSheetsResultsDF = gSheetsResultsDF[result_headers]
        gSheetsHistoryDF = gSheetsHistoryDF[history_headers]
        
        
        # Convert DataFrames to lists of dictionaries
        gSheetsResultsDF_json = gSheetsResultsDF.to_dict('records')
        gSheetsHistoryDF_json = gSheetsHistoryDF.to_dict('records')

        # Create a dictionary with both DataFrames
        response_data = {
        'gSheetsResultsDF': gSheetsResultsDF_json,
        'gSheetsHistoryDF': gSheetsHistoryDF_json
        }
        print("gSheetsResultsDF columns:", gSheetsResultsDF.columns.tolist())
        print("gSheetsHistoryDF columns:", gSheetsHistoryDF.columns.tolist())
        
        # Return the data as JSON
        return jsonify(response_data)
    else:
        return 'No variables provided!', 400


def main_process(user_variables,result_headers,history_headers):
    #print("user_variables entered into main_process: ", user_variables) ## TEST
    #print("result_headers entered into main_process: ", result_headers) ## TEST
    #print("history_headers entered into main_process: ", history_headers) ## TEST

    ### Extract the initial required user_variables ---- note: rest of the variables will be extracted later
    MarketCapMoreThan = user_variables.get('marketCapMoreThan', None)
    PriceMoreThan = user_variables.get('priceMoreThan', None)
    VolumeMoreThan = user_variables.get('volumeMoreThan', None)
        # exchange = variables.get('exchange', None) // cancelling because exchange is defined in stockScreener.py 
        
    # Check if all required variables are provided
    if None in [MarketCapMoreThan, PriceMoreThan, VolumeMoreThan]:
        print("none found in user_variables list")
        return json.dumps({"error": "Missing one or more required variables."}), 400


    ### Call the stockScreener function with the extracted core variables -> saves the data to a google cloud file
    all_filtered_stocks = stockScreener(MarketCapMoreThan, PriceMoreThan, VolumeMoreThan, FM_API_KEY) ## returns all filtered stock's info data (and saves to gCloud screened_stocks.json)
   
    ### Extract the symbols from google cloud file # note: idet they need to be saved to google cloud, just extract symbols straight from that list
    screened_stocks_url = "https://storage.googleapis.com/daily_screened_stocks/screened_stocks.json"
    def read_symbols_from_json(screened_stocks_url):
        response = requests.get(screened_stocks_url)
        data = response.json()
        symbols = [item['symbol'] for item in data]
        return symbols
    symbols = read_symbols_from_json(screened_stocks_url)

    
    ### Call the rsiFilter function with the symbols and user configured RSI variables to further filter out stocks
    rsiPeriod = user_variables.get('rsiPeriod', None)
    rsiThreshold = user_variables.get('rsiThreshold', None)
    rsi_filtered_stocks = rsi_filter(symbols, rsiPeriod, rsiThreshold) ####!!!!!! add 14, 90 if testing locally
    print(rsi_filtered_stocks)
    
    
    ### extract the rest of the values from google sheet
    ## remaining user_variables
    # volumeSpike
    volP1 = user_variables.get('volP1', None)
    volP2 = user_variables.get('volP2', None)
    volP3 = user_variables.get('volP3', None)
    # sma
    smaP1 = user_variables.get('smaP1', None)
    smaP2 = user_variables.get('smaP2', None)
    smaP3 = user_variables.get('smaP3', None)
    # bbandUpperDiff
    bbandP1 = user_variables.get('bbandP1', None)
    bbandP2 = user_variables.get('bbandP2', None)
    numStdv = user_variables.get('numStdv', None)
    # stoch
    stochPeriod = user_variables.get('stochPeriod', None)
    stochThreshold = user_variables.get('stochThreshold', None)
    # prettyNum
    inc1 = user_variables.get('inc1', None)
    inc2 = user_variables.get('inc2', None)
    inc3 = user_variables.get('inc3', None)
    inc4 = user_variables.get('inc4', None)
    tol1 = user_variables.get('tol1', None)
    tol2 = user_variables.get('tol2', None)
    tol3 = user_variables.get('tol3', None)
    tol4 = user_variables.get('tol4', None)
    # strengthRedditSubmissions
    recentPeriod = user_variables.get('recentPeriod', None)
    longerPeriod = user_variables.get('longerPeriod', None)
    # strengthRedditDailyComments = none
    ## results_headers = directly imported in dataframe initialization
    ## history_headers = directly imported in dataframe initialization


    ### Setup DataFrames with columns that will ultimately get returned back to google sheets appscript
    gSheetsResultsDF = pd.DataFrame(columns=result_headers)
    gSheetsHistoryDF = pd.DataFrame(columns=history_headers)
       
    ### Setup lists to collect data for DataFrames
    results_data = []
    history_data = []
        
    for symbol in rsi_filtered_stocks.keys(): ### FOR EACH SYMBOL in RSI FILTERED STOCKS
       
        
        # fetchStockData.py: fetch data from yfinance and save as array
        stockData = fetch_stock_data(symbol)
        
        perDiffVolP1, perDiffVolP2, perDiffVolP3 = volumeSpike(stockData, volP1, volP2, volP3)
        perDiffSmaP1, perDiffSmaP2, perDiffSmaP3 = sma(stockData, smaP1, smaP2, smaP3)
        perDiffUpBandP1, perDiffUpBandP2 = bbandUpperRel(stockData, bbandP1, bbandP2, numStdv)
        stochSignal, perDiffStochThresh, stochIndicator = stoch(stockData, stochPeriod, stochThreshold)
        incResult1, incResult2, incResult3, incResult4 = prettyNum(stockData, inc1, inc2, inc3, inc4, tol1, tol2, tol3, tol4)
        # macd --- ignore
        relSubmissionStrength, totalSubmissions, submissionTickerMentions = strengthRedditSubmissions(stockData, recentPeriod, longerPeriod)
        relCommentStrength, totalComments, commentTickerMentions = strengthRedditDailyComments(stockData)
        
        ### Calculate technical score
        
        ### Calculate social score
        
        
        rsi = rsi_filtered_stocks[symbol] # get rsi
        # stock_info = next((item for item in all_filtered_stocks if item['symbol'] == symbol), None) # get all stock info to get exchange
        
        # Extract exchange from all_filtered_stocks
        exchange = None
        for stock in all_filtered_stocks:
            if stock.get("symbol") == symbol:
                 exchange = stock.get("exchangeShortName")
                 break
        if exchange is None:
            print(f"Warning: Exchange not found for symbol {symbol}")
        
        # create filled-in arrays
        result_array = np.array([datetime.today(), symbol, rsi, perDiffVolP1, perDiffVolP2, perDiffVolP3, perDiffSmaP1, perDiffSmaP2, perDiffSmaP3, perDiffUpBandP1, perDiffUpBandP2, stochSignal, perDiffStochThresh, incResult1, incResult2, incResult3, incResult4, relSubmissionStrength, relCommentStrength, None, None])
        history_array = np.array([datetime.today(), exchange, MarketCapMoreThan, PriceMoreThan, VolumeMoreThan, rsiThreshold, rsiPeriod, symbol, rsi, None, None, volP1, volP2, volP3, perDiffVolP1, perDiffVolP2, perDiffVolP3, smaP1, smaP2, smaP3, perDiffSmaP1, perDiffSmaP2, perDiffSmaP3, bbandP1, bbandP2, numStdv, perDiffUpBandP1, perDiffUpBandP2, stochPeriod, stochThreshold, stochIndicator, stochSignal, perDiffStochThresh, inc1, inc2, inc3, inc4, tol1, tol2, tol3, tol4, incResult1, incResult2, incResult3, incResult4, recentPeriod, longerPeriod, totalSubmissions, submissionTickerMentions, relSubmissionStrength, totalComments, commentTickerMentions, relCommentStrength])
        
         # Instead of concatenating, append the data to lists
        results_data.append(result_array)
        history_data.append(history_array)
        print(f'Successfully appended: {symbol} data')
        
    # Create DataFrames after the loop
    gSheetsResultsDF = pd.DataFrame(results_data, columns=result_headers)
    gSheetsHistoryDF = pd.DataFrame(history_data, columns=history_headers)


    """
    ### call a function to write the full data frame to google sheets OR just return the whole dataframe and have the script write it
    # write_to_sheets(gSheetsResultsDF,gSheetsHistoryDF)
    """
    
    print("Main processing completed successfully.")
    return gSheetsResultsDF, gSheetsHistoryDF

""""
# testing within VS code
if __name__ == "__main__":
    # Example variables for testing
    test_user_variables = {
    "exchange": "'nyse', 'nasdaq'",
    "marketCapMoreThan": 300000000,
    "priceMoreThan": 5,
    "volumeMoreThan": 500000,
    "rsiThreshold": 94.6,
    "rsiPeriod": 14,
    "volP1": 60,
    "volP2": 21,
    "volP3": 5,
    "smaP1": 20,
    "smaP2": 10,
    "smaP3": 5,
    "bbandP1": 20,
    "bbandP2": 10,
    "numStdv": 2,
    "stochPeriod": 14,
    "stochThreshold": 80,
    "inc1": 100,
    "inc2": 50,
    "inc3": 25,
    "inc4": 10,
    "tol1": 10,
    "tol2": 5,
    "tol3": 3,
    "tol4": 1.5,
    "recentPeriod": 2,
    "longerPeriod": 30
    }

    test_result_headers = [
    'Date',
    'Symbol',
    'RSI',
    'perDiffVolP1',
    'perDiffVolP2',
    'perDiffVolP3',
    'perDiffSmaP1',
    'perDiffSmaP2',
    'perDiffSmaP3',
    'perDiffUpBandP1',
    'perDiffUpBandP2',
    'stochSignal',
    'perDiffStochThresh',
    'incResult1',
    'incResult2',
    'incResult3',
    'incResult4',
    'relSubmissionStrength',
    'relCommentStrength',
    'technical score',
    'social score'
    ]
    
    test_history_headers = [
    'Date',
    'exchange',
    'marketCapMoreThan',
    'priceMoreThan',
    'volumeMoreThan',
    'rsiThreshold',
    'rsiPeriod',
    'Symbol',
    'RSI',
    'technical score',
    'social score',
    'volP1',
    'volP2',
    'volP3',
    'perDiffVolP1',
    'perDiffVolP2',
    'perDiffVolP3',
    'smaP1',
    'smaP2',
    'smaP3',
    'perDiffSmaP1',
    'perDiffSmaP2',
    'perDiffSmaP3',
    'bbandP1',
    'bbandP2',
    'numStdv',
    'perDiffUpBandP1',
    'perDiffUpBandP2',
    'stochPeriod',
    'stochThreshold',
    'stochIndicator',
    'stochSignal',
    'perDiffStochThresh',
    'inc1',
    'inc2',
    'inc3',
    'inc4',
    'tol1',
    'tol2',
    'tol3',
    'tol4',
    'incResult1',
    'incResult2',
    'incResult3',
    'incResult4',
    'recentPeriod',
    'longerPeriod',
    'totalSubmissions',
    'submissionTickerMentions',
    'relSubmissionStrength',
    'totalComments',
    'commentTickerMentions',
    'relCommentStrength'
]

    # Call the main_process function with the test variables
    result = main_process(test_user_variables, test_result_headers, test_history_headers)    
    
    
    ""
     # manual column headers
    gSheetResultColumns = ['Date', 'Symbol', 'RSI', 'perDiffVolP1', 'perDiffVolP2', 'perDiffVolP3', 'perDiffSmaP1', 'perDiffSmaP2', 'perDiffSmaP3', 'perDiffUpBandP1', 'perDiffUpBandP2', 'stochSignal', 'perDiffStochThresh', 'incResult1', 'incResult2', 'incResult3', 'incResult4', 'relSubmissionStrength', 'relCommentStrength']
    gSheetHistoryColumns = [ "Date", "exchange", "marketCapMoreThan", "priceMoreThan", "volumeMoreThan", "rsiThreshold", 
    "rsiPeriod", "Symbol", "RSI", "technical score", "social score", "volP1", "volP2", "volP3", 
    "perDiffVolP1", "perDiffVolP2", "perDiffVolP3", "smaP1", "smaP2", "smaP3", "perDiffSmaP1", 
    "perDiffSmaP2", "perDiffSmaP3", "bbandP1", "bbandP2", "numStdv", "perDiffUpBandP1", 
    "perDiffUpBandP2", "stochPeriod", "stochThreshold", "stochIndicator", "stochSignal", 
    "perDiffStochThresh", "inc1", "inc2", "inc3", "inc4", "tol1", "tol2", "tol3", "tol4", 
    "incResult1", "incResult2", "incResult3", "incResult4", "recentPeriod", "longerPeriod", 
    "totalSubmissions", "submissionTickerMentions", "relSubmissionStrength", "totalComments", 
    "commentTickerMentions", "relCommentStrength" ]
   
    SPREADSHEET_ID = ("")
    RESULTS_SHEET_NAME = ("") #
    HISTORY_SHEET_NAME = ("")
    
    """        
    
    # symbol_gSheetResult, symbol_gSheetHistory = paramCalcs(symbol) ## call a single function to calculate each parameter for google sheets



""