#!/usr/bin/env python

import csv
import gzip
import os
import sys

import requests

csv.field_size_limit(sys.maxsize)

def process_apn(count, apn, output_path):
    apn_splits = apn.split('-')
    resp = requests.post('https://vcheck.ttc.lacounty.gov/proptax.php?page=main', data={
        'mapbook': apn_splits[0],
        'page': apn_splits[1],
        'parcel': apn_splits[2],
        'year': '',
        'token': 'f00fe327e7d5170ec10561f73a0861d2cd6b359db02cf99c6d4f1e0e6b1dfaac',
    }, cookies={
        'SSID': '8v7vomunofn868besd8naiammq',
    }, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    }, allow_redirects=True)

    if resp.status_code == 200:
        html = resp.text
        if html.find('<b>Assessor ID Number:</b>') > -1 and html.find(apn) < 0:
            # They responded with the wrong number
            print('-> Bad APN response!!! Skipping')
        else:
            with gzip.open(output_path, 'wt') as f_out:
                f_out.write(html)
                f_out.flush()
            return True, apn
    else:
        print('-> Failed')
    return False, apn

with open('/home/ian/Downloads/LA_County_Parcels.csv') as f_in:
    count = 0
    reader = csv.DictReader(f_in)

    for record in reader:
        count += 1
        apn = record['APN']
        if not apn.strip():
            continue

        print(count, apn)

        output_path = '/home/ian/code/prop13/scrapers/los_angeles/scrape_output_corrected/%s.html' % (apn)
        if os.path.exists(output_path):
            print('-> already have')
            continue

        process_apn(count, apn, output_path)
