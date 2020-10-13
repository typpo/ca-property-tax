#!/usr/bin/env python

import csv
import gzip
import json
import os
import re
import sys

from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)

AMOUNT_REGEX = re.compile('width="15%">\$([\d\.,]+)')

flatten=lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l]

with open('/home/ian/Downloads/alameda_parcels/alameda.geojson') as f_in, \
     open('./parse_output.csv', 'w') as f_out:

    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    count = 0
    for line in f_in:
        count += 1
        if count < 6:
            # Skip geojson cruft left by conversion
            continue

        record = json.loads(line[:-2])
        apn = record['properties']['APN']
        address = record['properties']['SitusAddress']
        if not apn:
            continue
        if record['properties']['UseCode'] and record['properties']['UseCode'][0] == '3':
            address += ' (Commercial)'

        if not record['geometry'] or not record['geometry']['coordinates']:
            print('-> skip')
            continue
        # There is definitely a more correct way to do this.
        flat_coords = flatten(record['geometry']['coordinates'])
        coords = zip(flat_coords[0::2], flat_coords[1::2])

        try:
            centroid = list(Polygon(coords).centroid.coords)[0]
        except:
            print('-> could not find centroid')
            continue

        print(count, apn, centroid)

        output_path = '/home/ian/code/prop13/scrapers/alameda/scrape_output/%s.html' % (apn)
        if not os.path.exists(output_path):
            print('-->', apn, 'record does not exist')
            continue

        try:
            with gzip.open(output_path, 'rt') as f_in:
                html = f_in.read()
        except:
            print('--> bad file')
            continue

        amount = -1
        try:
            amount_str = AMOUNT_REGEX.search(html).group(1).replace(',', '')
            amount = float(amount_str)
        except:
            print('--> Could not parse float', amount_str)
            continue

        print('--> Paid', amount)

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[1],
            'longitude': centroid[0],
            'tax': amount,
            'county': 'AL',
        })
