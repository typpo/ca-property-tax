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
GEOJSON_FILE = os.path.join(DATA_DIR, 'butte_parcels.geojson')

sql_create_parcel_table = """
CREATE TABLE IF NOT EXISTS parcels (
    apn TEXT PRIMARY KEY,                        -- county specific id for parcel lookup
    location TEXT NOT NULL,                      -- the address or geographical description of parcel
    zipcode TEXT NOT NULL,                       -- the zipcode of the parcel
    geo_lat NUMERIC,                             -- the latitude of the property centroid
    geo_lon NUMERIC,                             -- the longitude of the property centroid
    use_code TEXT,                               -- property use code
    lot_size_sqft NUMERIC,                       -- the lot size in square feet
    building_size_sqft NUMERIC,                  -- the building size in square feet
    building_bed_count NUMERIC,                  -- the number of bedrooms in building
    building_bath_count NUMERIC,                 -- the number of bathrooms in building
    building_stories_count NUMERIC,              -- the number of stories in building
    building_units_count NUMERIC,                -- the number of units in building
    building_age NUMERIC,                        -- the year building is built
    tax_value NUMERIC                            -- the appicable assessed tax
);
"""
sql_select_apn_from_parsed = """
SELECT EXISTS(SELECT 1 FROM parcels WHERE apn = ?);
"""
sql_insert_parcel_from_parsed = """
INSERT INTO parcels (apn, location, zipcode, geo_lat, geo_lon, use_code, lot_size_sqft, building_size_sqft, building_bed_count, building_bath_count, building_stories_count, building_units_count, building_age)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

flatten=lambda l: sum(map(flatten, l),[]) if isinstance(l,list) else [l]

def run():
    conn = None
    try:
        db_file = os.path.join(DATA_DIR, 'butte_parcel.db')
        print('Opening {}'.format(db_file))

        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(sql_create_parcel_table)

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

                props = record['properties']
                formatted_apn = props['SiteAPN']
                if not formatted_apn:
                    continue
                if not record['geometry'] or not record['geometry']['coordinates']:
                    print('-> skip')
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

                # check if id already exists
                c.execute(sql_select_apn_from_parsed, (formatted_apn,))
                (existsCheck,) = c.fetchone()
                if existsCheck > 0:
                    continue
                if not props['SiteZip']:
                    continue

                insert_record = (
                    formatted_apn,
                    '{}\n{}'.format(props['SiteAddr'], props['SiteCity']),
                    props['SiteZip'],
                    centroid[1],
                    centroid[0],
                    props['UseCode'],
                    props['LotSizeSF'],
                    props['BuildingSF'],
                    props['Bedrooms'],
                    props['Bathrooms'],
                    props['Stories'],
                    props['Units'],
                    props['YrBuilt']
                )
                c.execute(sql_insert_parcel_from_parsed, insert_record)
            conn.commit()
            print("inserts: {}".format(c.lastrowid))
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    run()
