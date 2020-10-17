#!/usr/bin/env python

import os
import sys
import errno
import gzip
import csv
import shutil

# All paths relative to project root
INPUT_DIR = './scrapers'
INPUT_FILENAME = 'parse_output.csv'
EXAMPLE_INPUT_PATH = f'{INPUT_DIR}/example_data.csv'
OUTPUT_PATH = './data/ca_all.csv.gz'
CSV_FIELDNAMES = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']

try:
    os.makedirs(os.path.dirname(OUTPUT_PATH))
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

csv.field_size_limit(sys.maxsize)

found_data = False

with gzip.open(OUTPUT_PATH, 'wt') as f_out, \
os.scandir(INPUT_DIR) as dir:
    writer = csv.DictWriter(f_out, fieldnames=CSV_FIELDNAMES)
    for item in dir:
        if item.is_dir():
            input_path = os.path.join(item.path, INPUT_FILENAME)
            try:
                with open(input_path, newline='') as f_in:
                    reader = csv.DictReader(f_in, fieldnames=CSV_FIELDNAMES)
                    for row in reader:
                        writer.writerow(row)
                found_data = True
                print(f"Loaded data from {input_path}")
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise
                print(f"WARNING: No data file exists at {input_path}")

if found_data == False:
    print("No input data found! Loading example data...")
    with open(EXAMPLE_INPUT_PATH, 'rb') as f_in, \
    gzip.open(OUTPUT_PATH, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

print(f"Data saved to {OUTPUT_PATH}")