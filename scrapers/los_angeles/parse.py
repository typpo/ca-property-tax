#!/usr/bin/env python

import csv
import gzip
import os
import re
import sys

csv.field_size_limit(sys.maxsize)

AMOUNT_REGEX = re.compile('<td>Tax Amount</td>\s+<td class=\'installmentmoney fakeform\'>\$([,\.\d]+)</td>')

def get_val(row, key):
    val = row[key].strip()
    if not val:
        return 0
    return float(val)

with open('/home/ian/Downloads/LA_County_Parcels.csv') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    reader = csv.DictReader(f_in)
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    count = 0
    for row in reader:
        count += 1
        if count % 20000 == 0:
            print(count, '...')

        apn = row['APN']
        address = row['SitusAddress']
        print(count, apn, address)

        try:
            lat = float(row['CENTER_LAT'])
            lng = float(row['CENTER_LON'])
        except:
            print('-> bad latlng')
            continue

        output_path = '/home/ian/code/prop13/scrapers/los_angeles/scrape_output_corrected/%s.html' % (apn)
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
            amount_strs = AMOUNT_REGEX.findall(html)
            amount = sum([float(s.replace(',', '')) for s in amount_strs])
        except:
            print('--> Could not parse float', amount_str)
            continue

        print('--> Paid', amount)

        zone = 'O'
        if row['UseType'] == 'Residential':
            zone = 'R'
        elif row['UseType'] == 'Commercial':
            zone = 'C'

        if zone == 'C':
            address += ' (Commercial)'

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': lat,
            'longitude': lng,
            'tax': amount,
            'county': 'LA',
        })
