#!/usr/bin/env python

import concurrent.futures
import gzip
import csv
import os
import time
import pathlib

import requests

PARCEL_TABLE_INDEX_MAX = 298820 # found by brute
CONNECTIONS = 20
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, os.path.join('..', '..', 'outputs', 'fresno'))
PARCEL_HOMEPAGE_URL = 'https://www2.co.fresno.ca.us/0410/FresnoTTCPaymentApplication/Welcome.aspx'
PARCEL_LOOKUP_URL = 'https://www2.co.fresno.ca.us/0410/FresnoTTCPaymentApplication/SecuredDetails.aspx?id=%s&PropertyType=1'
ID_SCRAPE_OUTPUT_DIR = os.path.join(DATA_DIR, 'id_scrape_output')
SLEEP_TIME = 0.25

# ensure the data directory is available
pathlib.Path(ID_SCRAPE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def refresh_session(request_session):
    # fetch homepage to get session id
    request_session.get(PARCEL_HOMEPAGE_URL)


def process_id(request_session, id, output_path, try_again = False):
    print('Processing', id)
    proxyDict = {
        'http': 'http://52.9.37.116:80'
    }
    get_url = PARCEL_LOOKUP_URL % id
    resp = request_session.get(get_url, allow_redirects=False, proxies=proxyDict)
    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
        time.sleep(SLEEP_TIME)
    elif resp.status_code == 302 and not try_again:
        refresh_session(request_session)
        process_id(request_session, id, output_path, True)
    else:
        print('-> Failed with code', resp.status_code)

def main():
    count = 0
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        with requests.session() as request_session:
            for index in range(PARCEL_TABLE_INDEX_MAX):
                count += 1

                print('Queueing', count)

                output_path = (ID_SCRAPE_OUTPUT_DIR + '/%s.html') % (count)
                if os.path.exists(output_path):
                    continue

                futures.append(executor.submit(process_id, request_session, count, output_path))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        print('Completed', data)

if __name__ == '__main__':
    main()
