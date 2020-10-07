#!/usr/bin/env python

import csv
import gzip
import json
import os
import sys

import requests
from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)

with open('/home/ian/Downloads/Parcels___Active_and_Retired.csv') as f_in:
    count = 0
    reader = csv.DictReader(f_in)
    for record in reader:
        count += 1

        apn = record['blklot']

        #coords = record['geometry']['coordinates'][0]
        #centroid = list(Polygon(coords).centroid.coords)[0]
        centroid = ()

        print(count, apn, centroid)

        output_path = '/home/ian/code/prop13/scrapers/san_francisco/scrape_output/%s.html' % (apn)
        if os.path.exists(output_path):
            continue

        resp = requests.get('https://sanfrancisco-ca.county-taxes.com/public/search?search_query=%s&category=gsgx_property_tax' % apn)
        if resp.status_code == 200:
            html = resp.text
            with gzip.open(output_path, 'wt') as f_out:
                f_out.write(html)
        else:
            print('-> Failed')
