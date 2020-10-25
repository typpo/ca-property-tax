#!/usr/bin/env python

import concurrent.futures
import gzip
import csv
import os
import time

import requests

CONNECTIONS = 20
PARCEL_LOOKUP_URL = 'https://common2.mptsweb.com/MBC/napa/tax/main/%s/2020/0000'
PARCEL_SOURCE_FILE = '/home/alin/Downloads/napa/parcels_public.csv'
OUTPUT_DIR = '/home/alin/code/prop13/scrapers/napa/scrape_output'
SLEEP_TIME = 0.5

def process_apn(count, apn, output_path):
    print(count, 'Processing', apn)
    proxyDict = {
        'https': 'https://104.149.139.206:3128'
    }
    get_url = PARCEL_LOOKUP_URL % apn
    resp = requests.get(PARCEL_LOOKUP_URL % apn, proxies=proxyDict)
    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
        time.sleep(SLEEP_TIME)
    else:
        print('-> Failed with code', resp.status_code)

with open(PARCEL_SOURCE_FILE) as f_in:
    count = 0
    futures = []
    f_in_csv = csv.reader(f_in)
    apn_index = -1
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        for row in f_in_csv:
            count += 1

            if count == 1:
                apn_index = row.index('ASMT')
                continue

            if apn_index < 0:
                print('Unable to locate APN index from header row')
                raise

            apn = row[apn_index]

            print('Queueing', count, apn)

            output_path = (OUTPUT_DIR + '/%s.html') % (apn)
            if os.path.exists(output_path):
                continue

            futures.append(executor.submit(process_apn, count, apn, output_path))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)
