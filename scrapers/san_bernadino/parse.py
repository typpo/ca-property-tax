#!/usr/bin/env python

import csv
import gzip
import os
import re
import sys
import json

from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)

AMOUNT_REGEX = re.compile('([\d\.]+)\|Secured\|2020-12-10')

with open('/home/ian/Downloads/san_bernadino/sbdo.geojson') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county', 'zone']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    count = 0
    for line in f_in:
        count += 1
        if count < 6:
            # Skip geojson garbage
            continue

        record = json.loads(line[:-2])
        apn = record['properties']['ParcelNumb']

        if not record.get('geometry') or not record['geometry'].get('coordinates'):
            print('-> no geom')
            continue
        coords = record['geometry']['coordinates'][0]
        try:
            centroid = list(Polygon(coords).centroid.coords)[0]
        except:
            print('-> failed centroid')
            continue

        address = ''
        zone = record['properties']['AssessClas']
        if zone and zone.find('Commercial') > -1:
            address += ' (Commercial)'

        print(count, apn, address, centroid)

        output_path = '/home/ian/code/prop13/scrapers/san_bernadino/scrape_output/%s.html' % (apn)
        if not os.path.exists(output_path):
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
            print('--> Could not parse amount', amount_str)
            continue

        print('--> Paid', amount)

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[1],
            'longitude': centroid[0],
            'tax': amount * 2,
            'county': 'SB',
        })
