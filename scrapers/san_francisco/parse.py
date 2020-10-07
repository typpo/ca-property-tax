
#!/usr/bin/env python

import csv
import gzip
import json
import os

from shapely.geometry import Polygon
from bs4 import BeautifulSoup

with open('/home/ian/Downloads/san_mateo_apn/san_mateo.geojson') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    count = 0
    for line in f_in:
        count += 1
        if count < 6:
            continue
        record = json.loads(line[:-2])
        apn = record['properties']['APN']

        coords = record['geometry']['coordinates'][0]
        try:
            centroid = list(Polygon(coords).centroid.coords)[0]
        except:
            continue

        print(count, apn, centroid)

        output_path = '/home/ian/code/prop13/scrapers/san_mateo/scrape_output/%s.html' % (apn)
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
            address = 'UNKNOWN'
        else:
            address = ownersplit[1].strip()
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
        })
        f_out.flush()
