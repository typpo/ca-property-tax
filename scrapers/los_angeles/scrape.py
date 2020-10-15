#!/usr/bin/env python

import concurrent.futures
import csv
import gzip
import os
import sys

import requests

csv.field_size_limit(sys.maxsize)

CONNECTIONS = 10

def process_apn(count, apn, output_path):
    print(count, 'Processing', apn)
    apn_splits = apn.split('-')
    resp = requests.post('https://vcheck.ttc.lacounty.gov/proptax.php?page=main', data={
        'mapbook': apn_splits[0],
        'page': apn_splits[1],
        'parcel': apn_splits[2],
        'year': '',
        'token': 'b43a4be6021c5f6c66992952a64847690bc7b589f80a13d9ee569a69d03242b8',
    }, cookies={
        'SSID': 'orv3ljjoc3tib7erdbg3c5mhio',
    }, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    }, allow_redirects=True)

    if resp.status_code == 200:
        html = resp.text
        if html.find('Installment 1') < 0:
            print('-> Invalid response')
        else:
            with gzip.open(output_path, 'wt') as f_out:
                f_out.write(html)
            return True, apn
    else:
        print('-> Failed')
    return False, apn

with open('/home/ian/Downloads/LA_County_Parcels.csv') as f_in:
    count = 0
    reader = csv.DictReader(f_in)

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        for record in reader:
            count += 1
            if count <= 2e6:
                continue
            apn = record['APN']
            if not apn.strip():
                continue

            print(count, apn)

            output_path = '/home/ian/code/prop13/scrapers/los_angeles/scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                continue

            futures.append(executor.submit(process_apn, count, apn, output_path))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)
