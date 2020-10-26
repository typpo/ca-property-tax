#!/usr/bin/env python

import concurrent.futures
import gzip
import csv
import os
import pathlib

import requests

CONNECTIONS = 20
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, os.path.join('..', '..', 'outputs', 'solano'))
PARCEL_LOOKUP_URL = 'http://mpay.solanocounty.com/searchResults.asp?ParcelValue=%s'
PARCEL_SOURCE_FILE = os.path.join(DATA_DIR, 'Parcels2020.csv')
OUTPUT_DIR = os.path.join(DATA_DIR, 'scrape_output')

# ensure the data directory is available
pathlib.Path(SCRAPE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def process_apn(count, apn, output_path):
    print(count, 'Processing', apn)
    form_data = {
        'userOpt': '1',
        'action': 'Detail',
        'ParcelValue': apn,
        'OccurValue': '01',
        'BillType': 'SC',
        'billAsmtYear': '',
        'billEvent': '',
        'billAmount': '',
        'bill9972': 'no',
        'DetailButton': 'Detail'
    }
    post_url = PARCEL_LOOKUP_URL % apn
    resp = requests.post(PARCEL_LOOKUP_URL % apn, data=form_data)
    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
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
                apn_index = row.index('APN')
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
