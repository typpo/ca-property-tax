#!/usr/bin/env python

import csv
import gzip
import os
import sys

import requests

csv.field_size_limit(sys.maxsize)

def process_apn(count, apn, output_path):
    apn_splits = apn.split('-')

    retries = 0
    while True:
        try:
            resp = requests.post('https://vcheck.ttc.lacounty.gov/proptax.php?page=main', data={
                'mapbook': apn_splits[0],
                'page': apn_splits[1],
                'parcel': apn_splits[2],
                'year': '',
                'token': 'dd1f2e78e528dfe54cdf5b6fb037f4757460173e6e8bda171f112b8e002282ef',
            }, cookies={
                'SSID': 'enprmofm7vbq8hueu7823pragj',
            }, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
            }, allow_redirects=True)
            break
        except:
            retries += 1
            if retries > 3:
                print('-> Complete failure')
                sys.exit(1)

    if resp.status_code == 200:
        html = resp.text
        if html.find('<b>Assessor ID Number:</b>') > -1 and html.find(apn) < 0:
            # They responded with the wrong number
            print('-> Bad APN response!!! Skipping')
        if html.find('captcha') > -1:
            print('-> captcha :O')
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
