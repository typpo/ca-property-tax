# Scrapes Sacramento County property tax info onto local device
# Code by @typpo and @highleyman

# Notes:
# Assessor data scraped from here https://eproptax.saccounty.net/#secured/BillDetail/20391972, for example
# Parcel numbers loaded from csv called Parcel_Centroids.csv downloaded here: https://yodata-yolo.opendata.arcgis.com/datasets/f950580d0dbd4cc0a203c04fa7f3d987_0
# For this code to work, please add an 11th column called 'CLEAN_APN' to Parcel_Centroids.csv which consists of the full 14 digit APN in string format." ))

# This scrape takes at least a day to run, maybe more (~482,000 files) You can stop and restart and it will save your progress.

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
    query_apn = apn
    resp = requests.get('https://eproptax.saccounty.net/servicev2/eproptax.svc/rest/BillSummary?parcel=%s' % query_apn, timeout=30)
    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
    else:
        print('-> Failed with code', resp.status_code)



with open('./Parcel_Centroids.csv') as f_in:
    count = 0
    reader = csv.DictReader(f_in)
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:

        for record in reader:
            count += 1

            try:
                apn = record['CLEAN_APN'].strip()
            except:
                print("Please add a column called 'CLEAN_APN' to Parcel_Centroids.csv which consists of the full 14 digit APN in string format." )

            print('Queueing', count, apn)

            output_path = './scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                continue

            futures.append(executor.submit(process_apn, count, apn, output_path))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)
