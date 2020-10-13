#!/usr/bin/env python

import asyncio
import csv
import gzip
import json
import os
import time
import sys

import requests
import pyppeteer


csv.field_size_limit(sys.maxsize)

#sess = requests.Session()

async def main():
    with open('/home/ian/Downloads/Alameda_Parcels.csv') as f_in:
        count = 0
        reader = csv.DictReader(f_in)

        browser = await pyppeteer.launch(headless=True)

        for record in reader:
            count += 1
            #if count < 440000:
            #    continue

            apn = record['APN'].strip()
            if not apn:
                continue

            print(count, apn, record['TotalNetValue'])

            output_path = '/home/ian/code/prop13/scrapers/alameda/scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                continue

            url = 'https://www.acgov.org/ptax_pub_app/RealSearchInit.do?searchByParcel=true&parcelNumber=%s' % apn
            #resp = requests.get(url)

            #time.sleep(0.5)
            try:
                context = await browser.createIncognitoBrowserContext()
                page = await context.newPage()
                await page.goto(url, {'waitUntil' : 'domcontentloaded'})
                await page.waitFor('#newacgovfooter')
                html = await page.content()
                await page.close()
                await context.close()

                with gzip.open(output_path, 'wt') as f_out:
                    f_out.write(html)
            except Exception as ex:
                print('->', ex)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
