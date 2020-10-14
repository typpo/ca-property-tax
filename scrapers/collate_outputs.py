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
CSV_OUTPUT_PATH = './data/all_regions.csv'
GZ_OUTPUT_PATH = './data/all_regions.csv.gz'
CSV_FIELDNAMES = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']

csv.field_size_limit(sys.maxsize)

collated_data = []

with os.scandir(INPUT_DIR) as dir:
    for item in dir:
        if item.is_dir():
            input_path = os.path.join(item.path, INPUT_FILENAME)
            try:
                with open(input_path, newline='') as f_in:
                    reader = csv.DictReader(f_in, fieldnames=CSV_FIELDNAMES)
                    for row in reader:
                        collated_data.append(row)
                print(f"Loaded data from {input_path}")
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise
                print(f"WARNING: No data file exists at {input_path}")

try:
    os.makedirs(os.path.dirname(GZ_OUTPUT_PATH))
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

if len(collated_data) == 0:
    print("No input data found! Loading example data...")
    collated_csv_path = EXAMPLE_INPUT_PATH
else:
    with open(CSV_OUTPUT_PATH, 'w') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=CSV_FIELDNAMES)
        writer.writerows(collated_data)
    collated_csv_path = CSV_OUTPUT_PATH

with open(collated_csv_path, 'rb') as f_in:
    with gzip.open(GZ_OUTPUT_PATH, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

print(f"Data saved to {GZ_OUTPUT_PATH}")