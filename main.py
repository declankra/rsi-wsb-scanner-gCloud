
from markupsafe import escape
from flask import request
import os
from stockScreener import stockScreener  # Import the function
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
        print("variables from request_json: ", variables)  ## TEST
        return 'Variables processed successfully.', 200
    else:
        return 'No variables provided!', 400


def main_process(variables):
    print("main_process accessed") ## TEST
    print("variables from main_process: ",variables) ## TEST
    # Extract the required variables
        # exchange = variables.get('exchange', None) // cancelling because exchange is defined in stockScreener.py 
    MarketCapMoreThan = variables.get('MarketCapMoreThan', None)
    PriceMoreThan = variables.get('PriceMoreThan', None)
    VolumeMoreThan = variables.get('VolumeMoreThan', None)
    
    print("three get variables: ", MarketCapMoreThan, PriceMoreThan, VolumeMoreThan) ## TEST
    
    # Check if all required variables are provided
    if None in [MarketCapMoreThan, PriceMoreThan, VolumeMoreThan]:
        print("none found in variables list")
        return json.dumps({"error": "Missing one or more required variables."}), 400

    # Call the stockScreener function with the extracted variables
    stockScreener(MarketCapMoreThan, PriceMoreThan, VolumeMoreThan, FM_API_KEY)

    # Placeholder for other function calls
    # e.g., fetch_stock_data(variables['ticker_symbol'])
    # You can add your business logic here, such as fetching data, performing analysis, etc.

    return "Main processing completed successfully."

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