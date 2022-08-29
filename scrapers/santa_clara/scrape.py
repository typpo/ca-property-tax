#!/usr/bin/env python

import csv
import gzip
import json
import os
import sys

import cloudscraper
from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)
scraper = cloudscraper.create_scraper()

with open('/home/ian/Downloads/Santa_Clara_Parcels.csv') as f_in:
    count = 0
    reader = csv.DictReader(f_in)
    for record in reader:
        count += 1
        #if count < 200000:
        #    continue
        apn = record['APN']
        if not apn.strip():
            continue

        #coords = record['geometry']['coordinates'][0]
        #centroid = list(Polygon(coords).centroid.coords)[0]
        centroid = ()

        print(count, apn, centroid)

        output_path = '/home/ian/code/prop13/scrapers/santa_clara/scrape_output/%s.html' % (apn)
        if os.path.exists(output_path):
            continue

        retries = 0
        while True:
            try:
                resp = scraper.post('https://payments.sccgov.org/propertytax/Secured', params={
                    'ParcelNumber': apn,
                })
                break
            except:
                retries += 1
                if retries > 3:
                    print('--> Complete failure')
                    sys.exit(1)

        if resp.status_code == 200:
            html = resp.text
            with gzip.open(output_path, 'wt') as f_out:
                f_out.write(html)
        else:
            print('-> Failed')
