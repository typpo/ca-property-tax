#!/usr/bin/env python

import csv
import gzip
import json
import os
import sys

csv.field_size_limit(sys.maxsize)

def get_val(row, key):
    val = row[key].strip()
    if not val:
        return 0
    return float(val)

with open('/home/ian/Downloads/LA_County_Parcels.csv') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    reader = csv.DictReader(f_in)
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county', 'zone']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    count = 0
    for row in reader:
        count += 1
        if count % 20000 == 0:
            print(count, '...')

        apn = row['APN']
        address = row['SitusAddress']
        try:
            lat = float(row['CENTER_LAT'])
            lng = float(row['CENTER_LON'])

            value = get_val(row, 'Roll_LandValue') + get_val(row, 'Roll_ImpValue') + get_val(row, 'Roll_PersPropValue') + get_val(row, 'Roll_FixtureValue') - get_val(row, 'Roll_HomeOwnersExemp') - get_val(row, 'Roll_RealEstateExemp') - get_val(row, 'Roll_PersPropExemp') - get_val(row, 'Roll_FixtureExemp')
        except ValueError:
            continue

        zone = 'O'
        if row['UseType'] == 'Residential':
            zone = 'R'
        elif row['UseType'] == 'Commercial':
            zone = 'C'

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': lat,
            'longitude': lng,
            'tax': value * 0.016,
            'county': 'LA',
            'zone': zone,
        })
