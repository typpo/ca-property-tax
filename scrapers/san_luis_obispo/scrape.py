#!/usr/bin/env python

import asyncio
import gzip
import json
import os
import time
import sys

import requests
import pyppeteer

async def main():
    browser = await pyppeteer.launch(headless=True)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets/parcels.geojson')) as f_in:
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

            assessment_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scrape_output/%s.assessment.html' % (apn))
            if os.path.exists(assessment_path):
                continue

            try:
                context = await browser.createIncognitoBrowserContext()
                page = await context.newPage()
                await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
                apn_param = apn.replace('-', '')
                await page.goto(f'https://assessor.slocounty.ca.gov/assessor/pisa/SearchResults.aspx?APN={apn_param}', {'waitUntil' : 'domcontentloaded'})
                await page.setViewport({'width': 600, 'height': 800});
                await page.click('#Main_gvSearchResults tr:nth-child(2) td:nth-child(4) a')
                await page.waitForSelector('#Main_lblNetValue')
                assessment_html = await page.content()
                await page.close()
                await context.close()
            except Exception as ex:
                print('->', ex)
                continue

            tax_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scrape_output/%s.tax.html' % (apn))
            if os.path.exists(tax_path):
                continue

            try:
                context = await browser.createIncognitoBrowserContext()
                page = await context.newPage()
                await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
                await page.goto('https://services.slocountytax.org/Entry.aspx', {'waitUntil' : 'domcontentloaded'})
                await page.setViewport({'width': 600, 'height': 800});
                [apn1, apn2, apn3] = apn.split('-')
                await page.type('#txtAPN1', apn1)
                await page.type('#txtAPN2', apn2)
                await page.type('#txtAPN3', apn3)
                await page.click('#txtAPN4')
                await page.waitForSelector('#SecTaxBills_RadListView1_ctrl0_lblSecondInstallAmt', { 'timeout': 5000 })
                tax_html = await page.content()
                await page.close()
                await context.close()
            except Exception as ex:
                print('->', ex)
                continue

            with gzip.open(assessment_path, 'wt') as assessment_out, \
                 gzip.open(tax_path, 'wt') as tax_out:
                assessment_out.write(assessment_html)
                tax_out.write(tax_html)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
