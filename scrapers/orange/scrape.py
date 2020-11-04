#!/usr/bin/env python

import concurrent.futures
import csv
import gzip
import os
import sys

import requests

CONNECTIONS = 20

csv.field_size_limit(sys.maxsize)

def process_apn(count, apn, output_path):
    print('Process', count, apn)
    apn_clean = apn.replace('-', '')
    url = f'http://tax.ocgov.com/tcweb/detail_sec.asp?ReqParcel={apn}&StreetNo=&Direction=&StreetName=&APN={apn_clean}&Suffix=00&CmpRevDte=79799276&RollTypCde=Secured&Code=A&StSuffix=&City=&Unit=&s=1&p=1&t=&TaxYr=2020&CurYr=2020'
    resp = requests.get(url)

    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
            f_out.flush()
    else:
        print('-> Failed')

with open('/home/ian/Downloads/orange/ParcelAttribute.csv.txt') as f_in:
    reader = csv.reader(f_in, delimiter='|')

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        count = 0
        for row in reader:
            count += 1
            #rows.append(row)
            _, apn, _ = row
            if not apn.strip() or apn == '000':
                continue

            print(count, apn)

            output_path = '/home/ian/code/prop13/scrapers/orange/scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                print('-> already have')
                continue

            futures.append(executor.submit(process_apn, count, apn.strip(), output_path))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)
