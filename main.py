
from markupsafe import escape
from flask import request
import os
from stockScreener import stockScreener  # Import the function
from rsiFilter import rsiFilter  # Import the function
import json

## initialize runtime variables (private)
# FM_API_KEY = os.getenv('FM_API_KEY')
FM_API_KEY = 'Ke0ioOh8J93IRZJc1UDaTHMJSsf0JIMg' # setting it publicly because fuck it, i can get a new one if needed

def getVariables(request):
    request_json = request.get_json(silent=True)
    if request_json and 'variables' in request_json:
        variables = request_json['variables']
        # Call the main processing function with the received variables
        main_process(variables)
        return 'Variables processed successfully.', 200
    else:
        return 'No variables provided!', 400


def main_process(variables):
    print("variables entered into main_process: ", variables) ## TEST
    # Extract the required variables
        # exchange = variables.get('exchange', None) // cancelling because exchange is defined in stockScreener.py 
    MarketCapMoreThan = variables.get('marketCapMoreThan', None)
    PriceMoreThan = variables.get('priceMoreThan', None)
    VolumeMoreThan = variables.get('volumeMoreThan', None)
        
    # Check if all required variables are provided
    if None in [MarketCapMoreThan, PriceMoreThan, VolumeMoreThan]:
        print("none found in variables list")
        return json.dumps({"error": "Missing one or more required variables."}), 400

    # Call the stockScreener function with the extracted core variables
    all_filtered_stocks = stockScreener(MarketCapMoreThan, PriceMoreThan, VolumeMoreThan, FM_API_KEY) ## returns all filtered stock data
    print(all_filtered_stocks) ## test to get filtered stocks
    
    """ # Call the rsiFilter function with the symbols and rsi variables to further filter out stocks
    rsiPeriod = variables.get('rsiPeriod', None)
    rsiThreshold = variables.get('rsiThreshold', None)
    rsi_filtered_stocks = rsiFilter(all_filtered_stocks, rsiPeriod, rsiThreshold)
    """
    
    ## fetchStockData.py from yfinance
    
    """ # Call the volumeSpike function with the stock data and volume variables
    rsiPeriod = variables.get('rsiPeriod', None)
    rsiThreshold = variables.get('rsiThreshold', None)
    rsi_filtered_stocks = rsiFilter(all_filtered_stocks, rsiPeriod, rsiThreshold)
    
    etc etc
    """



    # Placeholder for other function calls
    # e.g., fetch_stock_data(variables['ticker_symbol'])
    # You can add your business logic here, such as fetching data, performing analysis, etc.

    return print("Main processing completed successfully.")

''' testing within VS code
if __name__ == "__main__":
    # Example variables for testing
    test_variables = {
        "MarketCapMoreThan": 300000000,
        "PriceMoreThan": 5,
        "VolumeMoreThan": 500000
    }
    
    # Call the main_process function with the test variables
    result = main_process(test_variables)
    print(result)
'''