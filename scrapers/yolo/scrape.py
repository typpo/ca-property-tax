# Scrapes Yolo County property tax info onto local device
# Code by @typpo and @highleyman

# Notes:
# Assessor data scraped from here https://common2.mptsweb.com/MBC/yolo/tax/main/030310003000/2020/0000, for example
# Parcel numbers loaded from csv downloaded here: https://yodata-yolo.opendata.arcgis.com/datasets/f950580d0dbd4cc0a203c04fa7f3d987_0
# The field for the parcel number in the Yolo database is "MEGA_APN" for some reason

import concurrent.futures
import csv
import gzip
import os
import sys

import requests

csv.field_size_limit(sys.maxsize)

CONNECTIONS = 5

def process_apn(count, apn, output_path):
    print(count, 'Processing', apn)
    query_apn = apn.replace('-', '') 
    resp = requests.get('https://common2.mptsweb.com/MBC/yolo/tax/main/%s/2020/0000' % query_apn)
    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
    else:
        print('-> Failed with code', resp.status_code)

with open('/Users/jake/Documents/Projects/yolo_data/Yolo_County_Tax_Parcels_Open_Data.csv') as f_in:
    count = 0
    reader = csv.DictReader(f_in)
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:

        for record in reader:
            count += 1

            apn = record['MEGA_APN'].strip()

            print('Queueing', count, apn)

            output_path = '/Users/jake/Documents/Projects/yolo_data/scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                continue

            futures.append(executor.submit(process_apn, count, apn, output_path))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)
