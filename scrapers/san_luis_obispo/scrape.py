#!/usr/bin/env python

import asyncio
import gzip
import json
import os
import time
import sys
import pyppeteer

async def scrape_apn(browser, count, apn, file):
    print('->', count, apn)

    assessment_path = os.path.join(os.path.dirname(os.path.abspath(file)), 'scrape_output/%s.assessment.html' % (apn))
    if os.path.exists(assessment_path):
        return

    context = await browser.createIncognitoBrowserContext()
    page = await context.newPage()
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

    try:
        apn_param = apn.replace('-', '')
        await page.goto(f'https://assessor.slocounty.ca.gov/assessor/pisa/SearchResults.aspx?APN={apn_param}', {'waitUntil' : 'domcontentloaded'})
        await page.setViewport({'width': 600, 'height': 800});
        await page.click('#Main_gvSearchResults tr:nth-child(2) td:nth-child(4) a')
        await page.waitForSelector('#Main_lblNetValue')
        assessment_html = await page.content()

        tax_path = os.path.join(os.path.dirname(os.path.abspath(file)), 'scrape_output/%s.tax.html' % (apn))
        if os.path.exists(tax_path):
            return

        await page.goto('https://services.slocountytax.org/Entry.aspx', {'waitUntil' : 'domcontentloaded'})
        await page.setViewport({'width': 600, 'height': 800});
        [apn1, apn2, apn3] = apn.split('-')
        await page.type('#txtAPN1', apn1)
        await page.type('#txtAPN2', apn2)
        await page.type('#txtAPN3', apn3)
        await page.click('#txtAPN4')
        await page.waitForSelector('#SecTaxBills_RadListView1_ctrl0_lblSecondInstallAmt', { 'timeout': 5000 })
        tax_html = await page.content()

        with gzip.open(assessment_path, 'wt') as assessment_out, \
             gzip.open(tax_path, 'wt') as tax_out:
            assessment_out.write(assessment_html)
            tax_out.write(tax_html)
    except Exception as ex:
        print('->', count, apn, ex)
    finally:
        await page.close()
        await context.close()

sem = asyncio.Semaphore(10)

async def safe_scrape_apn(browser, count, apn, file):
    async with sem:
        return await scrape_apn(browser, count, apn, file)

async def main(target, n):
    browser = await pyppeteer.launch(headless=True)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets/parcels.geojson')) as f_in:
        tasks = []
        count = 0
        for line in f_in:
            count += 1
            if count < 6:
                # Skip geojson metadata
                continue

            # Handle batch as a workaround to Chromium issues
            if count < target:
                continue

            if count > target + n:
                break

            try:
                record = json.loads(line[:-2])
            except:
                continue

            if 'APN' not in record['properties']:
                print('-> no APN')
                continue

            apn = record['properties']['APN']

            if not apn:
                print('-> blank APN')
                continue

            task = asyncio.ensure_future(safe_scrape_apn(browser, count, apn, __file__))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    target = int(sys.argv[1])
    n = int(sys.argv[2])
    asyncio.get_event_loop().run_until_complete(main(target, n))
