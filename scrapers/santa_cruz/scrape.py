#!/usr/bin/env python

import csv
import gzip
import json
import os
import sys

import requests

csv.field_size_limit(sys.maxsize)

with open('/home/ian/Downloads/Santa_Cruz_Assessor_Parcels.csv') as f_in:
    count = 0
    reader = csv.DictReader(f_in)
    for record in reader:
        count += 1
        #if count < 50000:
        #    continue
        apn = record['APN']
        if not apn.strip():
            continue

        print(count, apn)

        output_path = '/home/ian/code/prop13/scrapers/santa_cruz/scrape_output/%s.html' % (apn)
        if os.path.exists(output_path):
            continue

        resp = requests.post('http://ttc.co.santa-cruz.ca.us/Taxbills/', params={
            'Parcel': apn,
        }, cookies={
            'ASP.NET_SessionId': 'oqblcrejntdrhgxrsn33ubj1',
        }, allow_redirects=True)

        if resp.status_code == 200:
            html = resp.text
            if html.find('Installment') < 0:
                print('-> Invalid response')
            else:
                with gzip.open(output_path, 'wt') as f_out:
                    f_out.write(html)
        else:
            print('-> Failed')
