import requests
import pandas as pd
import boto3 
import datetime

response = requests.get('https://api.nextlot.com/api/v3/lots?filter=all&page=1&per_page=100&sale=101912&sort=position_asc')

data_details = response.json()

def find_all_info():
    dict_for_csv = []
    for i in data_details['lots']:

        lot_number = i['lot_number']
        name = i['name'].replace(',', '')
        current_bid = i['perf_current_value']
        num_of_bids = i['perf_uniq_bid_count']
        description = i['description_truncated'].replace(',', '')
        lot_status = datetime.datetime.fromisoformat(i['scheduled_ending_at'].replace('Z', '+00:00')).replace(tzinfo=None)
        current_time = datetime.datetime.utcnow()
        if current_time > lot_status:
                lot_status = 'Lot closed'
        else:
                lot_status = 'Lot open'
        
        dict_lots = {
            'Lot_number': lot_number,
            'Product title' : name,
            'Current bid(USD)' : current_bid,
            'Number of bids' : num_of_bids,
            'Lot status' : lot_status,
            'Product description' : description
            }
        
        dict_for_csv.append(dict_lots)
    aution_data_csv = 'aution_data.csv'
    df = pd.DataFrame(dict_for_csv)
    df.to_csv('aution_data.csv', index=False)

    #create client
    s3 = boto3.client('s3')
    S3_BUCKET_NAME = 'scraper-s3-project'
    S3_BUCKET_PATH = 'my_scraper_s3_project/scraper_products_data/'
    with open(aution_data_csv,'rb') as f:
        s3.upload_fileobj(f, S3_BUCKET_NAME, S3_BUCKET_PATH + aution_data_csv)

find_all_info()