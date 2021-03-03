#!/usr/bin/env python

import argparse
from collections import defaultdict
import csv
from pprint import pprint

def get_arguments():
  parser = argparse.ArgumentParser(description='Validate output files')
  parser.add_argument('csv_files', nargs='+', type=argparse.FileType('r'))
  return parser.parse_args()

def find_duplicates(count_dict, min_cnt=2):
  return list((k, cnt) for k, cnt
              in sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
              if cnt >= min_cnt)

def validate():
  args = get_arguments()

  for csv_file in args.csv_files:
    csv_reader = csv.DictReader(csv_file)

    errors = 0
    num_lines = 0
    print('***', csv_file.name, '***')

    addresses = defaultdict(int)
    apns = defaultdict(int)

    if csv_reader.fieldnames != ['address', 'apn', 'longitude', 'latitude',
                                 'tax', 'county']:
      print('* Header fields do not match ({})'.format(csv_reader.fieldnames))
      errors += 1

      # Incorrect fieldnames is a fatal error since we can't accurately check
      #   field values
      break

    for lineno, line in enumerate(csv_reader):
      lat = float(line['latitude'])
      lon = float(line['longitude'])

      if lat < 32.5 or lat > 42:
        print('* Line {}: Latitude is unexpected ({})'.format(lineno, lat))
        errors += 1

      if lon < -124.4 or lon > -114.13:
        print('* Line {}: Longitude is unexpected ({})'.format(lineno, lon))
        errors += 1

      addresses[line['address']] += 1
      apns[line['apn']] += 1

      num_lines += 1

      if errors > 100:
        print('Over 100 errors...')
        break


    print('{} errors found'.format(errors))
    dup_addresses = find_duplicates(addresses)
    if dup_addresses:
      print('Warning: {} duplicate addresses found'.format(len(dup_addresses)))
      pprint(dup_addresses[:10])

    dup_apns = find_duplicates(apns)
    if dup_apns:
      print('Warning: {} duplicate APNs found'.format(len(dup_addresses)))
      pprint(dup_apns[:10])

    print('{} records scanned'.format(num_lines))


if __name__ == "__main__":
    validate()
