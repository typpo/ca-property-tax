#!/usr/bin/env python

import csv
import gzip
import os
import re
import sys
import json

from bs4 import BeautifulSoup
from shapely.geometry import Polygon

csv.field_size_limit(sys.maxsize)

AMOUNT_REGEX = re.compile('Total Amount Due:\s+<span class="i16">\$([\d,\.]+)')

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets/parcels.geojson')) as apn_in, \
     open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parse_output.csv'), 'w') as f_out:
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)

    count = 0
    for line in apn_in:
        count += 1
        if count < 6:
            # Skip geojson garbage
            continue

        try:
            record = json.loads(line[:-2])
        except:
            continue

        if 'APN' not in record['properties']:
            print('-> no APN')
            continue
        apn = record['properties']['APN']
        if not apn:
            print('-> blank APN')
            continue

        print('->', count, apn)

        assessment_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scrape_output/%s.assessment.html' % (apn))
        if not os.path.exists(assessment_path):
            continue

        try:
            with gzip.open(assessment_path, 'rt') as f_in:
                html = f_in.read()
        except:
            print('--> bad file')
            continue

        soup = BeautifulSoup(html, 'html.parser')
        address = soup.find(id='Main_lblAddressValue').text
        structure_type = soup.find(id='Main_lblStructureTypeValue').text

        if address == ' ':
            continue

        print('-> Address', address)

        tax_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scrape_output/%s.tax.html' % (apn))
        if not os.path.exists(assessment_path):
            continue

        try:
            with gzip.open(tax_path, 'rt') as f_in:
                html = f_in.read()
        except:
            print('-> bad file')
            continue

        soup = BeautifulSoup(html, 'html.parser')
        amount_str = soup.select("tr[valign='top'] td:nth-child(2)")[0].text.strip().replace(',', '').replace('$', '')

        try:
            amount = float(amount_str)
        except:
            print('-> Could not parse amount', amount_str)
            continue

        print('-> Paid', amount)

        address_search = address.upper()
        address_match = None

        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets/addresses.geojson')) as address_in:
                for line in address_in:
                    if address_search in line:
                        address_match = json.loads(line[:-2])

                if not address_match:
                    print('-> No Address')
                    continue

                coords = address_match['geometry']['coordinates']
        except:
            print('-> bad address')
            continue

        is_commercial = structure_type.find('Commercial') > -1

        if is_commercial:
            address += ' (Commercial)'

        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': coords[1],
            'longitude': coords[0],
            'tax': amount,
            'county': 'SLO',
        })
