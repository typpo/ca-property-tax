#!/usr/bin/env python

import csv
import gzip
import json
import os
import re
import sys
import pathlib

from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, os.path.join('..', '..', 'outputs', 'solano'))
ADDRESS_REGEX = re.compile('Property\sType.*\n.*\n.*\n[^.*\>]+\>([^\<]+)\<')
AMOUNTS_REGEX = re.compile('\>Total\<.*\n.*.*\n[^\>]+\>([^\<]+).*\n[^\>]+\>([^\<]+).*\n')
GEOJSON_FILE = os.path.join(DATA_DIR, 'solano.geojson')
OUTPUT_FILE = os.path.join(DATA_DIR, 'parse_output.csv')
SCRAPE_OUTPUT_DIR = os.path.join(DATA_DIR, 'scrape_output')

# ensure the data directory is available
pathlib.Path(SCRAPE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

flatten=lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l]

with open(GEOJSON_FILE) as f_in, \
     open(OUTPUT_FILE, 'w') as f_out:

    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    count = 0
    for line in f_in:
        count += 1
        if count < 6:
            # Skip geojson cruft left by conversion
            continue

        try:
            json_to_parse = line[:-1] if line.decode('utf-8').endswith('}\n') else line[:-2]
            record = json.loads(json_to_parse)
        except:
            print('-> could not parse JSON on line %d' % (count,))
            continue

        apn = record['properties']['APN']
        if not apn:
            continue
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

        output_path = (SCRAPE_OUTPUT_DIR + '/%s.html') % (apn)
        if not os.path.exists(output_path):
            print('-->', apn, 'record does not exist')
            continue

        try:
            with gzip.open(output_path, 'rt') as f_in:
                html = f_in.read()
        except:
            print('--> bad file')
            continue

        amount = 0

        try:
            amounts_grps = AMOUNTS_REGEX.search(html)
            for x in range(1, 3):
                amount_str = amounts_grps.group(x).replace(',', '').replace('$', '')
                amount += float(amount_str)
        except:
            print('--> Could not parse float %s' % apn)
            amount = -1
            continue

        address = None

        try:
            address = ADDRESS_REGEX.search(html).group(1).replace('&nbsp;', ' ').strip()
        except:
            print('--> Could not find address for %s' % apn)
            continue

        print('--> Paid', amount)

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[1],
            'longitude': centroid[0],
            'tax': amount,
            'county': 'SOL',
        })
