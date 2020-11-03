#!/usr/bin/env python

import concurrent.futures
import gzip
import csv
import os
import time
import pathlib
import requests
import sqlite3

from sqlite3 import Error

CONNECTIONS = 20
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, os.path.join('..', '..', 'outputs', 'butte'))
PARCEL_LOOKUP_URL = 'https://common2.mptsweb.com/MBC/butte/tax/main/%s/2020/0000'
PARCEL_SOURCE_FILE = os.path.join(DATA_DIR, 'parcels_public.csv')
SCRAPE_OUTPUT_DIR = os.path.join(DATA_DIR, 'scrape_output')
SLEEP_TIME = 0.5

sql_select_apn_no_tax = """
SELECT apn FROM parcels WHERE tax_value <= 0 OR tax_value IS NULL;
"""
# ensure the data directory is available
pathlib.Path(SCRAPE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def process_apn(count, apn, output_path):
    print(count, 'Processing', apn)
    proxyDict = {
        'http': 'http://52.9.37.116:80'
    }
    get_url = PARCEL_LOOKUP_URL % apn
    resp = requests.get(get_url, proxies=proxyDict)
    if resp.status_code == 200:
        html = resp.text
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
        time.sleep(SLEEP_TIME)
    else:
        print('-> Failed with code', resp.status_code)

def run():
    conn = None
    try:
        db_file = os.path.join(DATA_DIR, 'butte_parcel.db')
        print('Opening {}'.format(db_file))

        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(sql_select_apn_no_tax)

        with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
            count = 0
            futures = []
            while True:
                fetched = c.fetchmany(1000)
                if len(fetched) == 0:
                    break
                for sql_row in fetched:
                    count = count + 1
                    apn = sql_row[0].replace('-', '') + '000'

                    print('Queueing', count, apn)

                    output_path = (SCRAPE_OUTPUT_DIR + '/%s.html') % (apn)
                    if os.path.exists(output_path):
                        continue

                    futures.append(executor.submit(process_apn, count, apn, output_path))

        for future in concurrent.futures.as_completed(futures):
            data = future.result()
            print('Completed', data)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    run()
