#!/usr/bin/env python

import csv
import gzip
import json
import os
import re
import sys
import pathlib
import sqlite3

from shapely.geometry import Polygon
from sqlite3 import Error

csv.field_size_limit(sys.maxsize)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, os.path.join('..', '..', 'outputs', 'butte'))
SCRAPE_OUTPUT_DIR = os.path.join(DATA_DIR, 'scrape_output')
OUTPUT_FILE = os.path.join(DATA_DIR, 'parse_output.csv')
AMOUNTS_REGEX = re.compile('h4\>Totals\s\-.*\n.*\n.*\n.*\>Total Due\<.*\n[^\>]+\>([^\<]+)')

sql_update_tax = """
UPDATE parcels SET tax_value = ? WHERE apn = ?;
"""
sql_select_apn = """
SELECT EXISTS(SELECT 1 FROM parcels WHERE apn = ? AND tax_value > 0);
"""

def update_tax():
    conn = None
    try:
        db_file = os.path.join(DATA_DIR, 'butte_parcel.db')
        print('Opening {}'.format(db_file))

        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        files = os.listdir(SCRAPE_OUTPUT_DIR)
        for f in files:
            if f.endswith('.html'):
                unformatted_apn = f[:-5]
                apn = '{}-{}-{}'.format(unformatted_apn[0:3], unformatted_apn[3:6], unformatted_apn[6:9])

                # check if id already exists
                c.execute(sql_select_apn, (apn,))
                (existsCheck,) = c.fetchone()
                if existsCheck > 0:
                    continue

                output_path = os.path.join(SCRAPE_OUTPUT_DIR, f)
                html = ''
                try:
                    amount = 0
                    with gzip.open(output_path, 'rt') as f_in:
                        html = f_in.read()

                        try:
                            amounts_grps = AMOUNTS_REGEX.search(html)
                            amount_str = amounts_grps.group(1).replace(',', '').replace('$', '')
                            amount += float(amount_str)
                        except:
                            print('--> Could not parse float %s' % unformatted_apn)
                            amount = -1
                            continue

                        c.execute(sql_update_tax, (amount, apn))
                        conn.commit()
                except:
                    print('Error for {}'.format(unformatted_apn))
                    continue
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    update_tax()
