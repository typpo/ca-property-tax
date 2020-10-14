#!/usr/bin/env python

import concurrent.futures
import gzip
import json
import os

import requests

CONNECTIONS = 20

def process_apn(count, apn, output_path):
    print(count, 'Processing', apn)
    resp = requests.get('https://taxcolp.cccounty.us/taxpaymentrev3/api/lookup/apn?apn=%s' % apn)
    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
    else:
        print('-> Failed with code', resp.status_code)

with open('/home/ian/Downloads/contra_costa/contra_costa.geojson') as f_in:
    count = 0
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        for line in f_in:
            count += 1
            if count < 6:
                # Skip geojson garbage
                continue

            record = json.loads(line[:-2])
            apn = record['properties']['APN']

            print('Queueing', count, apn)

            output_path = '/home/ian/code/prop13/scrapers/contra_costa/scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                continue

            futures.append(executor.submit(process_apn, count, apn, output_path))
            break

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)
