import requests
import json
from google.cloud import storage


exchanges = ['nyse', 'nasdaq'] ## not including amex
all_filtered_stocks = []

def stockScreener(MarketCapMoreThan, PriceMoreThan, VolumeMoreThan, FM_API_KEY):
    print("stockScreener function called")
    for exchange in exchanges:
        filtered_stocks = fetch_filtered_stocks_for_exchange(MarketCapMoreThan, PriceMoreThan, VolumeMoreThan, FM_API_KEY, exchange) # add exchange to call
        all_filtered_stocks.extend(filtered_stocks)
        print(f"Found {len(filtered_stocks)} stocks matching criteria on {exchange}.")
    
        # Save the combined list of filtered stocks to Google Cloud Storage
        save_to_cloud_storage(all_filtered_stocks, 'screened_stocks.json', 'daily_screened_stocks')
           
    return all_filtered_stocks, 200

def fetch_filtered_stocks_for_exchange(MarketCapMoreThan, PriceMoreThan, VolumeMoreThan, FM_API_KEY, exchange):
    url = "https://financialmodelingprep.com/api/v3/stock-screener"
    params = {
        'apikey': FM_API_KEY,
        'marketCapMoreThan': MarketCapMoreThan,
        'priceMoreThan': PriceMoreThan,
        'volumeMoreThan': VolumeMoreThan,
        'isEtf': False,
        'isFund': False,
        'isActivelyTrading': 'true',
        'exchange': exchange,
        'limit': None
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {exchange}")
        return []

def save_to_cloud_storage(data, filename, bucket_name):
    """Save data to a file in Google Cloud Storage"""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)

        # Convert the data to a JSON string
        data_string = json.dumps(data, indent=4)
        
        # Upload the data
        blob.upload_from_string(data_string, content_type='application/json')
        print(f"File {filename} uploaded to {bucket_name}.")
    except Exception as e:
        print(f"Failed to upload file {filename} to {bucket_name}: {e}")






