# CA property tax map

Property tax scrapers and a map.  Online at https://www.officialdata.org/ca-property-tax.

This code is a work in progress and contains references to my local filesystem!

## Crawling

This app crawls and saves data from county property tax sites.  Crawlers are written in Python.  Set up your Python environment using [Poetry](https://python-poetry.org/).  

Crawl/scrape/parse code lives in the `scrapers/` directory.  Each county has `scrape.py` and `parse.py`.  The "scrape" step downloads the HTML tax page for every Assessor Parcel Number (APN).  The "parse" step pulls out tax and address information.

## Serving

A simple node app hosts the map and a `/lookup` endpoint.  On start it loads all parse outputs in a geospatial index.  Install node dependencies with `yarn install` and then run the app in `server/index.js`.
