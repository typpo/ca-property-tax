import concurrent.futures
import gzip
import csv
import os
import time
import pathlib

import requests
import urllib.request

from tqdm import tqdm

CONNECTIONS = 17
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPE_OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'scrape_output')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
SLEEP_TIME = 0.25

# ensure the data directory is available
pathlib.Path(SCRAPE_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


PARCEL_LOOKUP_URL = 'https://common3.mptsweb.com/MBC/monterey/tax/main/%s/2020/0000'

def process_apn(apn, output_path):

    get_url = PARCEL_LOOKUP_URL % apn
    resp = requests.get(get_url)
    if resp.status_code == 200:
        # html = resp.text.encode("utf-8")
        html = resp.text
        # print(html)
        with gzip.open(output_path, 'wt') as f_out:
            f_out.write(html)
        time.sleep(SLEEP_TIME)
    else:
        print('-> Failed with code', resp.status_code)

if __name__ == "__main__":
    assess_path = pathlib.Path("scrapers/monterey/data/monterey_assesssments.csv")
    assess_url = "https://opendata.arcgis.com/datasets/53fe7826cdec414787b904b12f2f381a_1.csv"

    if not assess_path.exists():
        print("downloading tax assessments...")
        with urllib.request.urlopen(assess_url) as response:
            with assess_path.open("wb+") as f_out:
                f_out.write(response.read())

    with assess_path.open() as f_in:
        futures = []

        reader = csv.DictReader(f_in)
    
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
            for i, record in tqdm(enumerate(reader)):

                asmtnum = record["ASMTNUM"].zfill(12)

                output_path = (SCRAPE_OUTPUT_DIR + '/%s.html') % (asmtnum)
                if os.path.exists(output_path):
                    continue

                futures.append(executor.submit(process_apn, i, asmtnum, output_path))
        
        print("Done Queueing.")
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            if i % 100 == 0:
                print('Completed', i)
            data = future.result()

        print(i)