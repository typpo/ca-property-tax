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
    browser = await pyppeteer.launch(headless=True)
    with open('/home/ian/Downloads/san_diego/san_diego.geojson') as f_in:
        count = 0
        for line in f_in:
            count += 1
            if count < 6:
                # Skip geojson garbage
                continue

            record = json.loads(line[:-2])
            if 'APN' not in record['properties']:
                print('-> no APN')
                continue
            apn = record['properties']['APN']
            if not apn:
                print('-> blank APN')
                continue

            print(count, apn)

            output_path = '/home/ian/code/prop13/scrapers/san_diego/scrape_output/%s.html' % (apn)
            if os.path.exists(output_path):
                continue

            try:
                context = await browser.createIncognitoBrowserContext()
                page = await context.newPage()
                await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
                await page.goto('https://iwr.sdttc.com/paymentapplication/Search.aspx', {'waitUntil' : 'domcontentloaded'})
                await page.setViewport({'width': 600, 'height': 800});
                await page.click('#PaymentApplicationContent_lblSearchOption2')
                await page.type('#PaymentApplicationContent_tbParcelNumber', apn)
                await page.click('#PaymentApplicationContent_btnSubmitOption2')
                await page.waitForNavigation({ 'waitUntil': 'domcontentloaded' })
                html = await page.content()
                await page.close()
                await context.close()
            except Exception as ex:
                print('->', ex)
                continue

            with gzip.open(output_path, 'wt') as f_out:
                f_out.write(html)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
