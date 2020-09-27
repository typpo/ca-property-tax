#!/usr/bin/env python

import csv
import time
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

# sort san_mateo.csv | uniq > san_mateo_uniq.csv
# zcat us_ca_san_mateo-addresses-county.geojson.gz | jq -r '[.properties.number,.properties.street,.geometry.coordinates[0],.geometry.coordinates[1]] | @csv' > san_mateo.csv

# https://sanmateo-ca.county-taxes.com/public/search?search_query=118+RIO+VERDE+ST&category=all

with open('../../addresses/san_mateo_uniq.csv') as f_in, \
     open('./output.csv', 'w') as f_out:
    fieldnames = ['number', 'street', 'longitude', 'latitude']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames + ['tax_2019'])
    reader = csv.DictReader(f_in, fieldnames=fieldnames)
    count = 0
    for row in reader:
        #if count % 100 == 0:
        #    #print(count, '...')

        query = '%s %s' % (row['number'], row['street'])
        print('%d: %s' % (count, query))
        url = 'https://sanmateo-ca.county-taxes.com/public/search?search_query=%s&category=all' % quote(query)
        print('-->', url)

        resp = requests.get(url)
        if resp.status_code != 200:
            print('--> Bad response code', resp.status_code)

        soup = BeautifulSoup(resp.text, 'html.parser')
        amount = -1
        for payment in soup.find_all('div', class_='data-payment'):
            if payment.get_text().find('12/10/2019') > -1:
                # Last payment
                amount_elt = payment.find('div', class_='gsgx-installment-amount')
                amount_str = amount_elt.get_text().replace('$', '').replace(',', '')
                try:
                    amount = float(amount_str)
                    break
                except:
                    print('--> Could not parse float')

        print('--> Paid', amount)
        writer.writerow({
            'number': row['number'],
            'street': row['street'],
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'tax_2019': amount * 2,
        })
        f_out.flush()

        count += 1
        time.sleep(0.5)
