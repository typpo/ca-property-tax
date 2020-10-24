#!/usr/bin/env python

import csv
import gzip
import os
import re
import sys

from pyproj import Transformer

csv.field_size_limit(sys.maxsize)

AMOUNT_REGEX = re.compile('Both Installment[\s\S]+\$([\d,\.]+)')

# California Zone 3
# https://epsg.io/2227
transformer = Transformer.from_crs(2227, 4326)

def get_val(row, key):
    val = row[key].strip()
    if not val:
        return 0
    return float(val)

with open('/home/ian/Downloads/Santa_Cruz_Assessor_Parcels.csv') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    reader = csv.DictReader(f_in)
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    count = 0
    for row in reader:
        count += 1
        if count % 1000 == 0:
            print(count, '...')

        apn = row['APN']
        address = row['SITEADD']

        try:
            x_coord = float(row['XCOORD'])
            y_coord = float(row['YCOORD'])
        except:
            print('-> bad coords')
            continue

        centroid = transformer.transform(x_coord, y_coord)

        print(count, apn, address, centroid)

        output_path = '/home/ian/code/prop13/scrapers/santa_cruz/scrape_output/%s.html' % (apn)
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
            amount_str = AMOUNT_REGEX.search(html).group(1).replace(',', '')
            amount = float(amount_str)
        except:
            print('--> Could not parse float', amount_str)
            continue

        print('--> Paid', amount)

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[0],
            'longitude': centroid[1],
            'tax': amount,
            'county': 'SCZ',
        })
