#!/usr/bin/env python

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
    query_apn = apn.replace('-', '') + '000'
    resp = requests.get('https://common3.mptsweb.com/MBC/sonoma/tax/main/%s/2020/2020' % query_apn)
    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
    else:
        print('-> Failed with code', resp.status_code)

with open('/home/ian/Downloads/Sonoma_Parcels.csv') as f_in:
    count = 0
    reader = csv.DictReader(f_in)

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        for record in reader:
            count += 1

            apn = record['APN'].strip()

            print('Queueing', count, apn)

            output_path = '/home/ian/code/prop13/scrapers/sonoma/scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                continue

            futures.append(executor.submit(process_apn, count, apn, output_path))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)
