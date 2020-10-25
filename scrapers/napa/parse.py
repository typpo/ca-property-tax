#!/usr/bin/env python

import csv
import gzip
import json
import os
import re
import sys

from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)

ADDRESS_REGEX = re.compile('Address.*\n[^.*\>]+\>([^\<]+).*\n.*\n[^.*\>]+\>([^\<]+)')
AMOUNTS_REGEX = re.compile('\>Total Due\<.*\n[^\>]+\>([^\<]+)')
GEOJSON_FILE = '/home/alin/Downloads/napa/napa.geojson'
OUTPUT_FILE = '/home/alin/code/prop13/scrapers/napa/parse_output.csv'
SCRAPE_OUTPUT_DIR = '/home/alin/code/prop13/scrapers/napa/scrape_output'

flatten=lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l]

2784885.618484084,2784885.4214996574
38.317145, -122.294374
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
            json_to_parse = line.strip()
            if json_to_parse.endswith(','):
                json_to_parse = json_to_parse[:-1]
            record = json.loads(json_to_parse)
        except:
            print('-> could not parse JSON on line %d' % (count,))
            continue

        apn = record['properties']['ASMT']
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
            amount_str = amounts_grps.group(1).replace(',', '').replace('$', '')
            amount += float(amount_str)
        except:
            print('--> Could not parse float %s' % apn)
            amount = -1
            continue

        address = None

        try:
            address_grps = ADDRESS_REGEX.search(html)
            address_parts = []
            for x in range(1, 3):
                address_parts.append(' '.join(map(lambda wd: wd if wd == 'CA' else wd.lower().capitalize(), address_grps.group(x).strip().split())))
            address = ', '.join(address_parts)
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
            'county': 'NAPA',
        })
