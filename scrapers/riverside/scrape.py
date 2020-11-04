#!/usr/bin/env python

import concurrent.futures
import gzip
import json
import os
import re

import requests

CONNECTIONS = 10

def process_apn(count, apn, output_path):
    print(count, 'Processing', apn)
    url = f'https://ca-riverside-ttc.publicaccessnow.com/AccountSearch/AccountSummary.aspx?p={apn}&a={apn}&m='
    resp = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    })

    if resp.status_code != 200:
        print('-> Req failed with code', resp.status_code)
        return
    html = resp.text
    if html.find(f'>{apn}</td>') < 0:
        print('-> bad resp, couldnt find', apn)
        return
    with gzip.open(output_path, 'wt') as f_out:
        f_out.write(html)
        f_out.flush()

with open('/home/ian/Downloads/riverside/riverside.geojson') as f_in:
    count = 0
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        for line in f_in:
            count += 1
            if count < 6:
                # Skip geojson garbage
                continue

            try:
                record = json.loads(line[:-2])
            except:
                print('End of json')
                break
            apn = record['properties']['APN']
            if not apn:
                continue

            output_path = '/home/ian/code/prop13/scrapers/riverside/scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                continue

            print('queue', count, apn)
            futures.append(executor.submit(process_apn, count, apn, output_path))
            #process_apn(count, apn, output_path)

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)
