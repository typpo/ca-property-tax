
import csv
import gzip
import json
import os
import sys
import pandas as pd
import pathlib
import urllib.request
import geopandas as gpd


from tqdm import tqdm
from shapely.geometry import Polygon
from bs4 import BeautifulSoup

csv.field_size_limit(sys.maxsize)


def get_taxes():
    taxes_path = pathlib.Path("scrapers/monterey/data/taxes.csv")
    assess_path = pathlib.Path("scrapers/monterey/data/monterey_assesssments.csv")

    if not taxes_path.exists():
        with assess_path.open() as f_in:
            reader = csv.DictReader(f_in)
            with open('./scrapers/monterey/data/taxes.csv', "w+") as tax_f:
                writer = csv.writer(tax_f, delimiter=',')
                writer.writerow(("asmtnum", "tax"))

                for i, record in tqdm(enumerate(reader)):

                    apn = record['ASMTNUM'].zfill(12)
                    
                    output_path = './scrapers/monterey/scrape_output/%s.html' % (apn)
                    if not os.path.exists(output_path):
                        print(apn, 'record does not exist')
                        break
                    try:
                        with gzip.open(output_path, 'rt') as f_in:
                            html = f_in.read()
                    except:
                        print(output_path)
                        print('--> bad file')
                        continue

                    soup = BeautifulSoup(html, 'html.parser')
                    for header in soup.find_all("h4"):
                        if header.text == 'Totals - 1st and 2nd Installments':
                            dt = header.find_next_siblings("dl")
                            total_due = str(dt[0].find_all("dd")[0].text)
                            total_due = total_due.replace(",", "")
                            total_due = total_due.replace("$", "")
                            total_due = float(total_due)

                            writer.writerow((apn, total_due))
    
    return pd.read_csv(taxes_path)

if __name__ == "__main__":
    # download geometry
    geom_path = pathlib.Path("scrapers/monterey/data/geometry.zip")
    if not geom_path.exists():
        print("downloading geometry...")
        geom_url = "https://opendata.arcgis.com/datasets/53fe7826cdec414787b904b12f2f381a_0.zip"
        with urllib.request.urlopen(geom_url) as response:
            with open("scrapers/monterey/data/geometry.zip", "wb+") as f_out:
                f_out.write(response.read())
    
    geom = gpd.read_file("zip://" + str(geom_path.absolute()))

    # download addresses
    addr_path = pathlib.Path("scrapers/monterey/data/addresses.csv")
    addr_url = "https://opendata.arcgis.com/datasets/53fe7826cdec414787b904b12f2f381a_3.csv"
    if not addr_path.exists():
        print("downloading addresses...")
        with urllib.request.urlopen(addr_url) as response:
            with addr_path.open("wb+") as f_out:
                f_out.write(response.read())

    addresses = pd.read_csv(addr_path)
    
    taxes = get_taxes()
    
    print("geometry: ", geom.shape)
    print("addresses: ", addresses.shape)
    print("taxes: ", taxes.shape)

    # Clean geom
    geom = geom[["geometry", "APN"]]
    geom = geom.drop_duplicates(subset=["APN"])
    
    # Clean ADdresses
    addresses["address"] = addresses["SITUS1"] + " " + addresses["SITUS2"]
    addresses["ASMTNUM"] = addresses["ASMTNUM"].astype(str)
    addresses["ASMTNUM"] = addresses["ASMTNUM"].str.zfill(12)
    addresses = addresses[["address", "ASMTNUM"]]
    addresses = addresses.drop_duplicates(subset='ASMTNUM')

    taxes['asmtnum'] = taxes['asmtnum'].astype(str)
    taxes['asmtnum'] = taxes['asmtnum'].str.zfill(12)

    # Merge everything together
    final = geom.merge(addresses, left_on="APN", right_on='ASMTNUM', how='left', validate="one_to_one")

    final = final.merge(taxes, left_on="APN", right_on="asmtnum", how="left", validate="one_to_one")

    final['lat'] = final.geometry.centroid.y
    final['long'] = final.geometry.centroid.x

    final = final.rename(columns={"APN": "apn"})
    final["county"] = "Monterey"
    final["apn"] = final["apn"].astype(str)


    fields = ["apn", "tax", "address", "lat", "long", "county"]
    final[fields].to_csv("scrapers/monterey/data/final.csv", index=False)
    print()
    print(final.tax.isna().value_counts())
    print(final.address.isna().value_counts())
