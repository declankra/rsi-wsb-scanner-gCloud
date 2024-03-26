
from markupsafe import escape
from flask import request
import os
from stockScreener import stockScreener  # Import the function
import json

## initialize runtime variables (private)
FM_API_KEY = os.getenv('FM_API_KEY')

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
    
    
    # Extract the required variables
        # exchange = variables.get('exchange', None) cancelling
    MarketCapMoreThan = variables.get('MarketCapMoreThan', None)
    PriceMoreThan = variables.get('PriceMoreThan', None)
    VolumeMoreThan = variables.get('VolumeMoreThan', None)
    
    # Check if all required variables are provided
    if None in [MarketCapMoreThan, PriceMoreThan, VolumeMoreThan]:
        return json.dumps({"error": "Missing one or more required variables."}), 400

    # Call the stockScreener function with the extracted variables
    result = stockScreener(MarketCapMoreThan, PriceMoreThan, VolumeMoreThan, FM_API_KEY)

    # Placeholder for other function calls
    # e.g., fetch_stock_data(variables['ticker_symbol'])
    # You can add your business logic here, such as fetching data, performing analysis, etc.

    return "Main processing completed successfully."
