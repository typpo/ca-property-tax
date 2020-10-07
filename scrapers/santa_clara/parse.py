
#!/usr/bin/env python

import csv
import gzip
import json
import os
import sys

from shapely.geometry import Polygon
from bs4 import BeautifulSoup

csv.field_size_limit(sys.maxsize)

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
        #print('geomstr', geom_str)
        geom_splits = map(lambda lnglatstr: lnglatstr.strip().split(' '), geom_str.replace('(', '').replace(')', '').split(','))
        #print('splits', geom_splits)
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

        soup = BeautifulSoup(html, 'html.parser')
        try:
            address = soup.find(id='situsLine1').get('value')
        except AttributeError:
            print('--> No address')
            continue
        print('--> address', address)

        amount = -1
        amount_elt = soup.find('div', class_='amountduecolumn')
        amount_str = amount_elt.get_text().replace('$', '').replace(',', '')
        try:
            amount = float(amount_str)
        except:
            print('--> Could not parse float', amount_str)

        print('--> Paid', amount)

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[1],
            'longitude': centroid[0],
            'tax': amount * 2,
        })
        #f_out.flush()
