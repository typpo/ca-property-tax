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
DATA_DIR = os.path.join(SCRIPT_DIR, os.path.join('..', '..', 'outputs', 'fresno'))
ID_SCRAPE_OUTPUT_DIR = os.path.join(DATA_DIR, 'id_scrape_output')
GEOJSON_FILE = os.path.join(DATA_DIR, 'fresno.geojson')
OUTPUT_FILE = os.path.join(DATA_DIR, 'parse_output.csv')
APN_RX = re.compile('PARCEL NUMBER.*\n.*\n.*\n.*\n[^>]*>([^<\s]+)')
TOTAL_TAX_RX = re.compile('>\s*TOTAL\s+TAX\s*<[^\$]*\$([^<]+)')
LOCATION_RX = re.compile('LOCATION.*\n.*\n.*\n[^>]+>([^<]+)')

sql_create_parcel_table = """
CREATE TABLE IF NOT EXISTS id_parcels (
    id NUMERIC PRIMARY KEY,                      -- the id used by the county assessor records
    apn TEXT NOT NULL,                           -- county specific id for parcel lookup
    location TEXT,                               -- the address or geographical description of parcel
    geo_lat NUMERIC,                             -- the latitude of the property centroid
    geo_lon NUMERIC,                             -- the longitude of the property centroid
    tax_value NUMERIC NOT NULL                   -- the appicable assessed tax
);
"""
sql_insert_parcel_from_parsed = """
INSERT OR IGNORE INTO id_parcels (id, apn, location, tax_value)
VALUES (?, ?, ?, ?);
"""
sql_update_parcel_from_geo = """
UPDATE id_parcels SET geo_lat = ?, geo_lon = ? WHERE apn = ?;
"""
sql_add_index_on_apn = """
CREATE UNIQUE INDEX IF NOT EXISTS index_apn
ON id_parcels(apn);
"""
sql_select_id_from_parsed = """
SELECT EXISTS(SELECT 1 FROM id_parcels WHERE id = ?);
"""
sql_select_apn_from_parsed = """
SELECT EXISTS(SELECT 1 FROM id_parcels WHERE apn = ?);
"""
sql_select_for_csv_from_parsed = """
SELECT location, apn, geo_lat, geo_lon, tax_value, 'FRE'
FROM id_parcels WHERE geo_lat IS NOT NULL;
"""

flatten=lambda l: sum(map(flatten, l),[]) if isinstance(l,list) else [l]

def insert_ids():
    conn = None
    try:
        db_file = os.path.join(DATA_DIR, 'fresno_parcel.db')
        print('Opening {}'.format(db_file))

        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(sql_create_parcel_table)

        files = os.listdir(ID_SCRAPE_OUTPUT_DIR)
        for f in files:
            if f.endswith('.html'):
                id = f[:-5]

                # check if id already exists
                c.execute(sql_select_id_from_parsed, (id,))
                (existsCheck,) = c.fetchone()
                if existsCheck > 0:
                    continue

                output_path = os.path.join(ID_SCRAPE_OUTPUT_DIR, f)
                html = ''
                try:
                    with gzip.open(output_path, 'rt') as f_in:
                        html = f_in.read()

                        apn = None
                        location = None
                        total_tax = None

                        try:
                            apn = APN_RX.search(html).group(1)
                        except:
                            print('--> Could not extract APN for {}'.format(id))
                            continue

                        try:
                            location = LOCATION_RX.search(html).group(1)
                        except:
                            print('--> Could not extract location for APN {}'.format(apn))
                            continue

                        try:
                            total_tax_raw = TOTAL_TAX_RX.search(html).group(1)
                            total_tax = float(total_tax_raw.replace(',',''))
                            if total_tax == 0:
                                print('--> Could not format total tax for {}'.format(id))
                        except:
                            print('--> Could not extract total tax for APN {}'.format(apn))
                            continue

                        c.execute(sql_insert_parcel_from_parsed, (int(id), apn, location, float(total_tax)))
                        conn.commit()
                except:
                    print('{} --> bad file'.format(id))
                    continue
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def update_geo():
    conn = None
    try:
        db_file = os.path.join(DATA_DIR, 'fresno_parcel.db')
        print('Opening {}'.format(db_file))

        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(sql_add_index_on_apn)

        with open(GEOJSON_FILE) as f_in:
            count = 0
            for line in f_in:
                count += 1
                if count < 6:
                    # Skip geojson cruft left by conversion
                    continue

                try:
                    json_to_parse = line.strip()
                    if json_to_parse.endswith(','):
                        json_to_parse = json_to_parse[:-1]
                    record = json.loads(json_to_parse)
                except:
                    print('-> could not parse JSON on line %d' % (count,))
                    continue

                apn = record['properties']['APN']
                if not apn:
                    continue
                formatted_apn = "{}-{}-{}".format(apn[:3], apn[3:6], apn[6:len(apn)])

                # check if apn already exists
                c.execute(sql_select_apn_from_parsed, (formatted_apn,))
                (existsCheck,) = c.fetchone()
                if existsCheck > 0:
                    continue

                if not record['geometry'] or not record['geometry']['coordinates']:
                    continue
                # There is definitely a more correct way to do this.
                flat_coords = [[xyz[0], xyz[1]] for coords in record['geometry']['coordinates'] for xyz in coords]
                flat_coords = flatten(flat_coords)
                coords = zip(flat_coords[0::2], flat_coords[1::2])

                try:
                    centroid = list(Polygon(coords).centroid.coords)[0]
                except:
                    print('-> could not find centroid')
                    continue

                print('updating {}'.format(formatted_apn))
                c.execute(sql_update_parcel_from_geo, (centroid[1], centroid[0], formatted_apn))
                conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def output_csv():
    conn = None
    try:
        db_file = os.path.join(DATA_DIR, 'fresno_parcel.db')
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
                        'address': sql_row[0],
                        'apn': sql_row[1],
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
    # insert_ids()
    # update_geo()
    output_csv()
