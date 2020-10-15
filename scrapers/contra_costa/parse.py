#!/usr/bin/env python

import csv
import gzip
import json
import os

from pyproj import Transformer
from shapely.geometry import Polygon

flatten=lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l]

# California Zone 3
# https://epsg.io/2227
transformer = Transformer.from_crs(2227, 4326)

with open('/home/ian/Downloads/contra_costa/contra_costa.geojson') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county', 'zone']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    count = 0
    for line in f_in:
        count += 1
        if count < 6:
            # Skip geojson garbage
            continue

        try:
            record = json.loads(line[:-2])
        except:
            print('-> bad json')
            continue
        apn = record['properties']['APN']

        # There is definitely a more correct way to do this.
        flat_coords = flatten(record['geometry']['coordinates'])
        # Remove every third element - elevation
        del flat_coords[2::3]
        xy_coords = zip(flat_coords[0::2], flat_coords[1::2])

        try:
            xy_centroid = list(Polygon(xy_coords).centroid.coords)[0]
        except:
            print('-> could not find centroid')
            continue

        centroid = transformer.transform(xy_centroid[0],xy_centroid[1])

        print(count, apn, centroid)

        output_path = '/home/ian/code/prop13/scrapers/contra_costa/scrape_output/%s.html' % (apn)
        if not os.path.exists(output_path):
            print('-> no data')
            continue

        with gzip.open(output_path, 'rt') as scrape_file:
            try:
                record = json.loads(scrape_file.read())
            except:
                print('-> could not read')
                continue

        address = record['details']['address']
        try:
            installments = [installment for installment in record['installments'] if installment['type'] == 'SECURED']
            amount = float(installments[-1]['amount'].replace(',', ''))
        except (IndexError, ValueError):
            print('-> bad value')
            continue

        print('-> ', address, amount)

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[0],
            'longitude': centroid[1],
            'tax': amount * 2,
            'county': 'CC',
        })
