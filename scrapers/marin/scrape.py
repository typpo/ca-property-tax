#!/usr/bin/env python

import gzip
import json
import os
import re

import requests

BILL_NUMBER_REGEX = re.compile('BillNumber=([\d-]+)')

def process_apn(count, apn, output_path):
    print(count, 'Processing', apn)
    resp = requests.get('https://apps.marincounty.org/TaxBillOnline/?PropertyId=%s' % apn, cookies={
        'ASP.NET_SessionId': 'cb43i2fteofouruu13vrqlpt',
        'BNES_ASP.NET_SessionId': 'tpYQIn2c1x9dtg4Pr0oMa6CvBOr9/zv0WbXWALNFjdQeKlUtZ3K/c1T64zQJlJTPAYO+YiMcZMgnKyzdvmWYJX1PnCszgn7K',
        'BNES_SameSite': '4OOcDH0CIeaJGmGDBVVInvMxRwoe3/nrL6SeZAAMYuWHyU+FxQSqXA==',
    })

    if resp.status_code != 200:
        print('-> Req 1 failed with code', resp.status_code)
        return

    match = BILL_NUMBER_REGEX.search(resp.text)
    if not match:
        print('-> No bills')
        return
    bill_number = match.group(1)
    resp = requests.get('https://apps.marincounty.org/TaxBillOnline/Stub?BillNumber=%s' % bill_number, cookies={
        'ASP.NET_SessionId': 'cb43i2fteofouruu13vrqlpt',
        'BNES_ASP.NET_SessionId': 'tpYQIn2c1x9dtg4Pr0oMa6CvBOr9/zv0WbXWALNFjdQeKlUtZ3K/c1T64zQJlJTPAYO+YiMcZMgnKyzdvmWYJX1PnCszgn7K',
        'BNES_SameSite': '4OOcDH0CIeaJGmGDBVVInvMxRwoe3/nrL6SeZAAMYuWHyU+FxQSqXA==',
    })

    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
    else:
        print('-> Req 2 failed with code', resp.status_code)

with open('/home/ian/Downloads/marin/marin.geojson') as f_in:
    count = 0
    for line in f_in:
        count += 1
        if count < 6:
            # Skip geojson garbage
            continue

        record = json.loads(line[:-2])
        apn = record['properties']['Prop_ID']

        print('Queueing', count, apn)

        output_path = '/home/ian/code/prop13/scrapers/marin/scrape_output/%s.html' % (apn)
        if os.path.exists(output_path):
            continue

        process_apn(count, apn, output_path)
