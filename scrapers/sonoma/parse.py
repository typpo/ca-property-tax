#!/usr/bin/env python

import csv
import gzip
import os
import re
import sys

csv.field_size_limit(sys.maxsize)

AMOUNT_REGEX = re.compile('Total Due</dt>\s+<dd>\$([\d\.,]+)')

with open('/home/ian/Downloads/Sonoma_Parcels.csv') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county', 'zone']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    count = 0
    reader = csv.DictReader(f_in)
    for record in reader:
        count += 1

        apn = record['APN'].strip()
        address = record['SitusFmt1']
        lat = float(record['Lat'])
        lng = float(record['Long'])

        if record['UseCType'] == 'Commercial':
            address += ' (Commercial)'

        print(count, apn, address, lat, lng)

        output_path = '/home/ian/code/prop13/scrapers/sonoma/scrape_output/%s.html' % (apn)
        if os.path.exists(output_path):
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
            'latitude': lat,
            'longitude': lng,
            'tax': amount * 2,
            'county': 'SN',
        })
