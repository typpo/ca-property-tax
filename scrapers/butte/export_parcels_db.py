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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, os.path.join('..', '..', 'outputs', 'butte'))
OUTPUT_FILE = os.path.join(DATA_DIR, 'parse_output.csv')

sql_select_for_csv_from_parsed = """
SELECT location, apn, geo_lat, geo_lon, tax_value, 'BUT'
FROM parcels WHERE geo_lat IS NOT NULL AND tax_value > 0;
"""

def output_csv():
    conn = None
    try:
        db_file = os.path.join(DATA_DIR, 'butte_parcel.db')
        print('Opening {}'.format(db_file))

        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(sql_select_for_csv_from_parsed)

        with open(OUTPUT_FILE, 'w') as f_out:
            fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            while True:
                fetched = c.fetchmany(1000)
                if len(fetched) == 0:
                    break
                for sql_row in fetched:
                    writer.writerow({
                        'address': sql_row[0].replace("\n", ", "),
                        'apn': "{}000".format(sql_row[1].replace("-", "")),
                        'latitude': sql_row[2],
                        'longitude': sql_row[3],
                        'tax': sql_row[4],
                        'county': sql_row[5]
                    })


    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    output_csv()
