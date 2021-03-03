#!/usr/bin/env python

import csv
import gzip
import json
import os
import re
import sys

from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)

AMOUNT_REGEX = re.compile('<td class="center">Installment #1</td>\s+<td style="text-align:right">\$([,\.\d]+)</td>')

def get_val(row, key):
    val = row[key].strip()
    if not val:
        return 0
    return float(val)

with open('/home/ian/Downloads/riverside/riverside.geojson') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    count = 0
    for line in f_in:
        count += 1
        if count < 6:
            # Skip geojson garbage
            continue
        if count % 20000 == 0:
            print(count, '...')

        try:
            record = json.loads(line[:-2])
        except:
            print('End of json')
            break

        apn = record['properties']['APN']
        if apn == 'RW' or not apn:
            print('No APN')
            continue
        address = '%s %s' % (record['properties']['HOUSE_NO'], record['properties']['STREET'])
        if not address:
            print('No address')
            continue
        print(count, apn, address)

        coords = record['geometry']['coordinates'][0]
        try:
            centroid = list(Polygon(coords).centroid.coords)[0]
        except:
            print('-> bad latlng')
            continue

        output_path = '/home/ian/code/prop13/scrapers/riverside/scrape_output/%s.html' % (apn)
        if not os.path.exists(output_path):
            print('-> no scraped file')
            continue

        try:
            with gzip.open(output_path, 'rt') as f_in:
                html = f_in.read()
        except:
            print('--> bad file')
            continue

        amount = -1
        try:
            amount_strs = AMOUNT_REGEX.findall(html)
            amounts = [float(s.replace(',', '')) for s in amount_strs]
            if len(amounts) < 1:
                print('Could not find amount')
                continue
            amount = max(amounts)
        except:
            print('--> Could not parse float', amount_str)
            continue

        print('--> Paid', amount)

        realuse = record['properties']['REALUSE']
        if realuse and len(realuse) > 0:
            if realuse[0] == 'R':
                zone = 'R'
            if realuse[0] == 'C':
                zone = 'C'

            if zone == 'C':
                address += ' (Commercial)'

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[1],
            'longitude': centroid[0],
            'tax': amount * 2,
            'county': 'RS',
        })
