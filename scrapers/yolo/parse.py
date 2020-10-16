# Parses Yolo County property tax info on local device
# Code by @typpo and @highleyman

# Notes
# Requires a local copy of the Yolo parcel map converted into a .geojson 
#      (originally available here: https://yodata-yolo.opendata.arcgis.com/datasets/f950580d0dbd4cc0a203c04fa7f3d987_0)
# I'm sure there are things that could be written a lot more cleanly, but it works on my mac at least

import csv
import gzip
import json
import os

from shapely.geometry import Polygon
from bs4 import BeautifulSoup

with open('/Users/jake/Documents/Projects/yolo_data/yolo.geojson') as f_in, \
     open('./parse_output.csv', 'w') as f_out:
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    count = 0
    for line in f_in:
        count += 1

        if count < 6:
            # Skip geojson cruft left by conversion
            continue
        try:
            record = json.loads(line[:-2])
            apn = record['properties']['MEGA_APN']
        except:
            continue
        
        try:
            coords = record['geometry']['coordinates'][0][0]
            centroid = list(Polygon(coords).centroid.coords)[0]
        except:
            continue
        
        print(count, apn, centroid)

        output_path = '/Users/jake/Documents/Projects/yolo_data/scrape_output/%s.html' % (apn)
        if not os.path.exists(output_path):
            print(apn, 'record does not exist')

        try:
            with gzip.open(output_path, 'rt') as f_in:
                html = f_in.read()
        except:
            print('--> bad file')
            continue

        soup = BeautifulSoup(html, 'html.parser')

        #extract payment info
        tab1 = soup.find('div', {'id':'h2tab1'})
        total_tax = -1 
        if tab1 != None:
            bills = tab1.find_all('dt',text='Total Due')

            if len(bills) == 3:
                #grab the total annual payment, not the 6-month one
                #no need to double value later on
                total_tax_str = bills[2].findNext('dd').string.replace('$', '').replace(',', '')
                try:
                    total_tax = float(total_tax_str)
                except:
                    print('--> Could not parse float', amount_str)
            else:
                print("bad tax records on parcel ",apn)

        else:
            print(apn,"Tax data not available.")


        #extract address
        tab2 = soup.find('div', {'id':'h2tab2'}) 
        if tab2 is not None:
            address = tab2.find('dt',text='Address').findNext('dd').string

        if address is None:
            address = "UNKNOWN"

        print(address,total_tax)


        writer.writerow({
            'address': address,
            'apn': apn,
            'latitude': centroid[1],
            'longitude': centroid[0],
            'tax': total_tax,
            'county': 'YOL',
        })
        f_out.flush()