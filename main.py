import datetime
from markupsafe import escape
from flask import request
import os
import pandas as pd
from stockScreener import stockScreener  # Import the function
from rsiFilterBatch import rsiFilter # Import the function
import json
import requests
from fetchStockData import fetch_stock_data


### initialize runtime variables
# FM_API_KEY = os.getenv('FM_API_KEY')
FM_API_KEY = 'Ke0ioOh8J93IRZJc1UDaTHMJSsf0JIMg' # setting it publicly because fuck it, i can get a new one if needed

### entrance function: process user configured variables from google sheets
def getVariables(request):
    request_json = request.get_json(silent=True)
    if request_json and 'variables' in request_json: # check if legit
        variables = request_json['variables']
        print('Variables processed successfully')
        # Call the main processing function with the received variables
        main_process(variables)
        return 'Data has been successfully appended to sheet', 200
    else:
        return 'No variables provided!', 400


def main_process(variables):
    print("variables entered into main_process: ", variables) ## TEST
    ### Extract the initial required variables ---- note: rest of the variables will be extracted later
    MarketCapMoreThan = variables.get('marketCapMoreThan', None)
    PriceMoreThan = variables.get('priceMoreThan', None)
    VolumeMoreThan = variables.get('volumeMoreThan', None)
        # exchange = variables.get('exchange', None) // cancelling because exchange is defined in stockScreener.py 
        
    # Check if all required variables are provided
    if None in [MarketCapMoreThan, PriceMoreThan, VolumeMoreThan]:
        print("none found in variables list")
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
    rsiPeriod = variables.get('rsiPeriod', None)
    rsiThreshold = variables.get('rsiThreshold', None)
    rsi_filtered_stocks = rsiFilter(symbols, 14, 90) ####!!!!!! add 14, 90 if testing locally
    print(rsi_filtered_stocks)
    
    
    ### Google sheet auth
    
     
    ### Setup dataframes that will ultimately get exported to sheets at the end with calcs
    # create columns based off google sheet column headers
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
     # init DataFrames with columns
    gSheetsResultsDF = pd.DataFrame(columns=gSheetResultColumns)
    gSheetsHistoryDF = pd.DataFrame(columns=gSheetHistoryColumns)
    # 
    

   
    
    ### FOR EACH SYMBOL in RSI FILTERED STOCKS
        ## call a single function to calculate each parameter for google sheets
        ##symbol_gSheetResult[], symbol_gSheetHistory[] = masterCalcFunction(symbol)
            ## create the array
            # fetchStockData.py: fetch data from yfinance and save as array
            # volumeSpike.py: volume spike calc
            # sma.py: sma calc
            # bbandUpperRel.py: bband calc
            # stoch.py: stoch calc
            # prettyNum.py: pretty num calc
            # macd --- ignore
            # strengthRedditSubmissions.py: submissions calc
            # strengthRedditDailyComments.py: comments calc

    
    ### call a function to write the full data frame to google sheets
    ## write_to_sheets(gSheetsResultsDF,gSheetsHistoryDF)
        
        
    # fetchStockData.py from yfinance (1 years worth) -> save to google cloud
    fetch_stock_data(rsi_filtered_stocks)
        
    
    """
    ## Create the master array for each filtered symbol that will contain the calcs/results to append to google sheet
    # List of variables for each array
    gSheetResultVars = ['Date', 'Symbol', 'RSI', 'perDiffVolP1', 'perDiffVolP2', 'perDiffVolP3', 'perDiffSmaP1', 'perDiffSmaP2', 'perDiffSmaP3', 'perDiffUpBandP1', 'perDiffUpBandP2', 'stochSignal', 'perDiffStochThresh', 'incResult1', 'incResult2', 'incResult3', 'incResult4', 'relSubmissionStrength', 'relCommentStrength']
    # Get current date
    current_date = datetime.datetime.now().strftime('%m-%d-%y')
    # Create a dictionary to store the arrays
    symbol_arrays = {symbol: [current_date, symbol, rsi_filtered_stocks[symbol]] + [None] * (len(variables) - 3) for symbol in rsi_filtered_stocks.keys()}
    # Print the result to verify
    for symbol, array in symbol_arrays.items():
        print(f"{symbol}: {array}")
    """
    
    
    

    return print("Main processing completed successfully.")



# testing within VS code
if __name__ == "__main__":
    # Example variables for testing
    test_variables = {
        "marketCapMoreThan": 300000000,
        "priceMoreThan": 5,
        "volumeMoreThan": 500000
    }
    
    # Call the main_process function with the test variables
    result = main_process(test_variables)
    print(result)
