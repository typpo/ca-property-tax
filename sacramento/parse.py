# Parses Sacramento County property tax info on local device
# Code by @typpo and @highleyman

# Notes

# Requires a local copy of Parcel_Centroids.csv (available for download here: https://data.saccounty.net/datasets/7da6753c252b42af9f85751dc5b27bbb_0) 
#   For this code to work, please add an 11th column called 'CLEAN_APN' to Parcel_Centroids.csv which consists of the full 14 digit APN in string format." ))
#   In general, I'm sure there are things that could be written a lot more cleanly, but it works on my mac at least :)

import csv
import gzip
import json
import os

currentyear = '2020' #update in future if need be

# make initial centroid dictionary with form {apn: centroid} from Parcel_Centroids.csv directly
with open('./Parcel_Centroids.csv', mode='r') as infile:
    next(infile)
    reader = csv.reader(infile)
    # make sure that the 11th field is the CLEAN_APN field in Parcel_Centroids.csv
    centroids_by_apn = {rows[10]:[float(rows[7]),float(rows[8])] for rows in reader}

# get other parcel info from Geojson file
with open('./parse_output.csv', 'w') as f_out:
    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county'] #other fields could be added if desired
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    count = 0
    goodcount = 0
    taxcount = 0

    for apn, centroid in centroids_by_apn.items():
        count += 1

        print(count, apn, centroid)

        output_path = './scrape_output/%s.html' % (apn)

        if not os.path.exists(output_path):
            print(apn, 'record does not exist')
        else:
            with gzip.open(output_path, 'rt') as scrape_file:
                try:
                    record = json.loads(scrape_file.read())
                except:
                    print('--> could not read')
                    #continue

            # address = "UNKNOWN" # default value
            address = record['GlobalData']['Address']
            if address is None or address == "":
                address = "UNKNOWN"
            else:
                goodcount += 1

            # This section adds all listed property taxes for the designated year, including supplemental 
            #   (secured and unsecured) and escape bills. If you only want the annual bill,
            #   you can change the if statement to include a check for bill['AssessmentType']=="Annual".
            #   This code will print out all tax values, which you can feel free to disable if you don't want so much output.
            total_tax = -1 #default coding; will remain when there is no tax data available
            billcount = record['BillCount']
            if billcount > 0:
                taxcount += 1
                total_tax = 0.0
                for i in range(billcount):
                    bill = record['Bills'][i]
                    #if it's the Annual, secured bill (aka the normal annual property tax, not supplemental ones or unsecured ones)
                    if bill['RollDate'] == currentyear:
                        try:
                            tax_string = bill['BillAmount']
                            tax = float(tax_string.replace(',', ''))
                            total_tax += tax

                            print(bill['BillType'],bill['AssessmentType'],tax)

                        except (IndexError, ValueError):
                            print('-> bad value')
                    else:
                        print("Did you update the 'currentyear' variable?")


            print("address:",address,"total tax:",total_tax)
            

            writer.writerow({
                'address': address,
                'apn': apn,
                'latitude': centroid[1],
                'longitude': centroid[0],
                'tax': total_tax,
                'county': 'SAC',
            })
            f_out.flush()

# Print some of the mildly interesting counts
    print("number of parcels total:",count)
    print("number of parcels with address information:",goodcount)
    print("number of parcels with tax information:",taxcount)
