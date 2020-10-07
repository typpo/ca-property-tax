
#!/usr/bin/env python

import csv
import gzip
import json
import os
import re
import sys

from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)

ADDRESS_REGEX = re.compile('name="situsLine1" type="hidden" value="(.*)"')
AMOUNT_REGEX = re.compile('amountduecolumn.*\n\s+\$([\d,\.]+)')

with open('/home/ian/Downloads/Santa_Clara_Parcels.csv') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    reader = csv.DictReader(f_in)

    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'zone']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    count = 0
    for record in reader:
        count += 1
        apn = record['APN']
        if not apn.strip():
            continue

        lnglats = []
        geom_str = record['the_geom'].replace('MULTIPOLYGON (((', '').replace(')))', '')
        geom_splits = map(lambda lnglatstr: lnglatstr.strip().split(' '), geom_str.replace('(', '').replace(')', '').split(','))
        coords = [(float(x[0]), float(x[1])) for x in geom_splits]

        try:
            centroid = list(Polygon(coords).centroid.coords)[0]
        except:
            continue

        print(count, apn, centroid)

        output_path = '/home/ian/code/prop13/scrapers/santa_clara/scrape_output/%s.html' % (apn)
        if not os.path.exists(output_path):
            print('-->', apn, 'record does not exist')
            continue

        with gzip.open(output_path, 'rt') as f_in:
            html = f_in.read()

        try:
            address = ADDRESS_REGEX.search(html).group(1) + ''
        except:
            print('--> No address')
            continue
        print('--> address', address)

        amount = -1
        try:
            amount = float(AMOUNT_REGEX.search(html).group(1).replace(',', ''))
        except:
            print('--> Could not parse float', amount_str)
            continue

        print('--> Paid', amount)

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[1],
            'longitude': centroid[0],
            'tax': amount * 2,
        })
