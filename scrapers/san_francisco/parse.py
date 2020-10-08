
#!/usr/bin/env python

import csv
import gzip
import json
import os
import sys

from shapely.geometry import Polygon
from bs4 import BeautifulSoup

csv.field_size_limit(sys.maxsize)

with open('/home/ian/Downloads/Parcels___Active_and_Retired.csv') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    reader = csv.DictReader(f_in)
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    count = 0
    for record in reader:
        count += 1

        apn = record['blklot']

        geom_str = record['shape'].replace('MULTIPOLYGON (((', '').replace(')))', '')
        geom_splits = map(lambda lnglatstr: lnglatstr.strip().split(' '), geom_str.replace('(', '').replace(')', '').split(','))
        try:
            coords = [(float(x[0]), float(x[1])) for x in geom_splits]
        except ValueError:
            print('--> bad coords', geom_splits)
            continue

        try:
            centroid = list(Polygon(coords).centroid.coords)[0]
        except:
            continue

        print(count, apn, centroid)

        output_path = '/home/ian/code/prop13/scrapers/san_francisco/scrape_output/%s.html' % (apn)
        if not os.path.exists(output_path):
            print(apn, 'record does not exist')
            break

        try:
            with gzip.open(output_path, 'rt') as f_in:
                html = f_in.read()
        except:
            print('--> bad file')
            continue

        soup = BeautifulSoup(html, 'html.parser')
        owner = soup.find('span', class_='gsgx-account-owner')
        if owner is None:
            continue
        ownersplit = owner.get_text().split(' at ')
        if len(ownersplit) < 2:
            continue
        else:
            address = ownersplit[1].strip().replace('\n', ' ')
            print('address:', address)

        amount = -1
        for payment in soup.find_all('div', class_='data-payment'):
            if payment.get_text().find('12/10/2020') > -1 or payment.get_text().find('12/10/2019') > -1:
                # Last payment
                amount_elt = payment.find('div', class_='gsgx-installment-amount')
                amount_str = amount_elt.get_text().replace('$', '').replace(',', '')
                try:
                    amount = float(amount_str)
                    break
                except:
                    print('--> Could not parse float', amount_str)
        if amount < 0:
            continue
        print('--> Paid', amount)

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[1],
            'longitude': centroid[0],
            'tax': amount * 2,
            'county': 'SF',
        })
