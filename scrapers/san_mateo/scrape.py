#!/usr/bin/env python

import gzip
import json
import os

import requests
from shapely.geometry import Polygon

with open('../../addresses/san_mateo.geojson') as f_in:
    count = 0
    for line in f_in:
        count += 1
        if count < 6:
            continue
        record = json.loads(line[:-2])
        apn = record['properties']['APN']

        #coords = record['geometry']['coordinates'][0]
        #centroid = list(Polygon(coords).centroid.coords)[0]
        centroid = ()

        print(count, apn, centroid)

        output_path = '/home/ian/code/prop13/scrapers/san_mateo/scrape_output/%s.html' % (apn)
        if os.path.exists(output_path):
            continue

        #apn_str = '%s-%s-%s' % (apn[0:3], apn[3:6], apn[6:9])
        #resp = requests.get('https://sanmateo-ca.county-taxes.com/public/property_tax/accounts/%s' % apn_str)
        resp = requests.get('https://sanmateo-ca.county-taxes.com/public/search?search_query=%s&category=all' % apn)
        if resp.status_code == 200:
            html = resp.text
            with gzip.open(output_path, 'wt') as f_out:
                f_out.write(html)
        else:
            print('-> Failed')
