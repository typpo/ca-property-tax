#!/usr/bin/env python

import concurrent.futures
import gzip
import json
import os
import re

import requests

ENC_REGEX = re.compile('trPropInfo_CurrentTaxes\.aspx\?enc=([^\']+)\';')

CONNECTIONS = 20

def process_apn(count, apn, output_path):
    print(count, 'Processing', apn)
    resp = requests.post('https://www.mytaxcollector.com/trSearchProcess.aspx', {
        'hidRedirect': '',
        'hidGotoEstimate': '',
        'txtStreetNumber': '',
        'txtStreetName': '',
        'cboStreetTag': '(Any Street Tag)',
        'cboCommunity': '(Any City)',
        'txtParcelNumber': apn,
        'txtPropertyID': '',
        'ctl00$contentHolder$cmdSearch': 'Search',
    })

    if resp.status_code != 200:
        print('-> Req 1 failed with code', resp.status_code)
        return

    match = ENC_REGEX.search(resp.text)
    if not match:
        print('-> No bills')
        return
    enc = match.group(1)
    resp = requests.get('https://www.mytaxcollector.com/trPropInfo_CurrentTaxes.aspx?enc=%s' % enc, cookies={
        'ASP.NET_SessionId': '55qohxk0pojd0ho2a0auhhad',
    }, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Referer': 'https://www.mytaxcollector.com/trSearchProcess.aspx',
    })
    print('https://www.mytaxcollector.com/trPropInfo_CurrentTaxes.aspx?enc=%s' % enc)

    if resp.status_code == 200:
        html = resp.text
        parcel_with_separators = '%s-%s-%s-0000' % (
            apn[:4],
            apn[4:7],
            apn[7:],
        )
        if html.find(parcel_with_separators) < 0:
            print('-> bad resp, couldnt find', parcel_with_separators)
            return
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
            f_out.flush()
    else:
        print('-> Req 2 failed with code', resp.status_code)

with open('/home/ian/Downloads/san_bernadino/sbdo.geojson') as f_in:
    count = 0
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        for line in f_in:
            count += 1
            if count < 6:
                # Skip geojson garbage
                continue

            record = json.loads(line[:-2])
            apn = record['properties']['ParcelNumb']
            if not apn:
                continue

            output_path = '/home/ian/code/prop13/scrapers/san_bernadino/scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                continue

            print('queue', count, apn)
            futures.append(executor.submit(process_apn, count, apn.strip(), output_path))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)
