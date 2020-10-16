#!/usr/bin/env python

import csv
import gzip
import os
import re
import sys
import json

from pyproj import Transformer
from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)

AMOUNT_REGEX = re.compile('Total Amount Due:\s+<span class="i16">\$([\d,\.]+)')

# California Zone 3
# https://epsg.io/2227
transformer = Transformer.from_crs(2227, 4326)

with open('/home/ian/Downloads/marin/marin.geojson') as f_in, \
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
        apn = record['properties']['Prop_ID']

        coords = record['geometry']['coordinates'][0]
        try:
            centroid_xy = list(Polygon(coords).centroid.coords)[0]
            centroid = transformer.transform(centroid_xy[0],centroid_xy[1])
        except:
            continue

        address = record['properties']['AssessorSi']
        if 'UseCdDesc' in record and record['UseCdDesc'].find('Commercial') > -1:
            address += ' (Commercial)'

        print(count, apn, address, centroid)

        output_path = '/home/ian/code/prop13/scrapers/marin/scrape_output/%s.html' % (apn)
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
            'latitude': centroid[0],
            'longitude': centroid[1],
            'tax': amount,
            'county': 'MN',
        })
