
from markupsafe import escape
from flask import request
import os

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

    # Placeholder for other function calls
    # e.g., fetch_stock_data(variables['ticker_symbol'])
    # You can add your business logic here, such as fetching data, performing analysis, etc.

    return "Main processing completed successfully."
