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

FIRST_AMOUNT_REGEX = re.compile('First Installment[\s\S]+?\$([\d,\.]+)')
SECOND_AMOUNT_REGEX = re.compile('Payment\s+Summary[\s\S]+?First Installment[\s\S]+?\$([\d,\.]+)')

ADDRESS_REGEX = re.compile('Location<\/td>\s+<td width="51%" class="content" >([\s\S]*?)<\/td>')

# California Zone 6
# https://epsg.io/2230
transformer = Transformer.from_crs(2230, 4326)

with open('/home/ian/Downloads/orange/ParcelAttribute.csv.txt') as f_in, \
     open('/home/ian/Downloads/orange/orange.geojson') as f_geojson, \
     open('./parse_output.csv', 'w') as f_out:
    reader = csv.reader(f_in, delimiter='|')
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county', 'zone']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    # Build lookup table for apns to geolocated object id
    print('Build object id <> apn lookup table')
    rows = []
    apn_to_obj_id = {}
    condo_count = 0
    # First pass: Collect non-condo apn -> object_id mapping
    for row in reader:
        rows.append(row)
        object_id, apn, condo_apn = row
        if not apn.strip() or apn == '000' or object_id == '0':
            condo_count += 1
            continue

        apn_to_obj_id[apn] = object_id
    print(len(apn_to_obj_id) + condo_count, 'apns total', len(apn_to_obj_id), 'non condo apns')

    # Second pass: collect all object id from geojson
    print('Collecting objectids from geojson...')
    object_id_to_centroid = {}
    count = 0
    for line in f_geojson:
        count += 1
        if count < 6:
            # Skip geojson garbage
            continue

        try:
            record = json.loads(line[:-2])
        except:
            print('End at line', count)
            break
        objectid = str(record['properties']['OBJECTID'])

        if not record.get('geometry') or not record['geometry'].get('coordinates'):
            print(objectid, '-> no geom')
            continue
        coords = record['geometry']['coordinates'][0]
        try:
            centroid_xy = list(Polygon(coords).centroid.coords)[0]
        except:
            print(objectid, '-> failed centroid')
            continue

        coords = transformer.transform(centroid_xy[0], centroid_xy[1])
        object_id_to_centroid[objectid] = coords

    # Third pass: put it all together
    print('Final pass...')
    print(len(object_id_to_centroid), 'objectids')
    count = 0
    for row in rows:
        count += 1
        object_id, apn, condo_apn = row

        true_object_id = object_id
        true_apn = condo_apn if apn == '000' else apn
        if object_id == '0':
            #  Fill in condo
            true_object_id = apn_to_obj_id[condo_apn]

        if true_object_id not in object_id_to_centroid:
            print('-> could not look up', true_object_id)
            continue
        coords = object_id_to_centroid[true_object_id]

        print(count, true_apn, coords)

        output_path = '/home/ian/code/prop13/scrapers/orange/scrape_output/%s.html' % (true_apn)
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
            amount1_str = FIRST_AMOUNT_REGEX.search(html).group(1).replace(',', '')
            amount1 = float(amount1_str)

            amount2_str = SECOND_AMOUNT_REGEX.search(html).group(1).replace(',', '')
            amount2 = float(amount2_str)

            amount = amount1 if amount1 > amount2 else amount2
        except:
            print('--> Could not parse amount', amount1_str, amount2_str)
            continue

        try:
            address = ADDRESS_REGEX.search(html).group(1).strip()
        except:
            print('--> Could not parse address', address)
            continue

        print('--> Paid', amount, address)

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': coords[1],
            'longitude': coords[0],
            'tax': amount * 2,
            'county': 'OC',
        })
