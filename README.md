# CA property tax map

Property tax scrapers and a map.  Online at https://www.officialdata.org/ca-property-tax.

How this project is organized:
- `app/` - The HTML page that displays the map
- `server/` - The backend that handles geospatial searches
- `scrapers/` - The crawlers that scrape and parse property tax pages

You may notice that some scraper code contains references to large datafiles on a local filesystem.  These files are quite large and must be shared separately.  You do not need these files to make a contribution to this project, especially if you are helping to add a new county.

Please feel free to contact me or open an issue if you have a question or need help.  I am working on making this project more contributor-friendly!

## How to add a county

Property taxes are handled at the county level.  So, we have to interface with county tax systems to add new data to the map.

Every county has a different system.  The process usually looks like this:

1. Find a GIS file containing all Parcels (aka properties) in the county.  Most counties have a data pages.  Examples: [Stanislaus](http://gis.stancounty.com/giscentral/public/downloads.jsp?main=4), [San Francisco](https://data.sfgov.org/Geographic-Locations-and-Boundaries/Parcels-Active-and-Retired/acdm-wktn).  Parcels are uniquely identified by a string called an APN (Assessor Parcel Number) or AIN.  If you're lucky, the file will also have zoning information.  If you're really lucky, maybe it has tax info all in one place - but I haven't encountered that yet.

2. Find the county's property tax lookup page.  Usually this is an enterprisey/legacy system.  Example: [San Francisco](https://sanfrancisco-ca.county-taxes.com/public) has one of the nicest systems. [LA](https://vcheck.ttc.lacounty.gov/) has one of the worst.

3. Figure out how to automate lookup for property tax for a given APN.  Best case scenario is that it's plain HTML returned by a GET request (e.g. [see SF code](https://github.com/typpo/ca-property-tax/blob/master/scrapers/san_francisco/scrape.py)).  Or, the page might be Javascript dependent and requires a headless browser like puppeteer (e.g. [Alameda](https://github.com/typpo/ca-property-tax/blob/master/scrapers/alameda/scrape.py)).  Even worse, it may be behind a captcha (like [LA](https://github.com/typpo/ca-property-tax/blob/master/scrapers/los_angeles/scrape.py), but fortunately we can workaround if you manually obtain a valid session cookie).

4. Write the scraper and parser (see below).  Most new scrapers can be based on an existing scraper.

## Crawling

This project crawls and saves data from county property tax sites.  The data is processed into a CSV that is loaded by the web app.  Crawlers are written in Python.  Set up your Python environment by installing [Poetry](https://python-poetry.org/) and running `poetry install`.

Crawl/scrape/parse code lives in the `scrapers/` directory.  Each county's crawl has two steps:

1. `scrape.py` - Downloads the HTML of each property tax page, usually by querying for APN
2. `parse.py` - Parses the HTML of each property tax page into CSV output: `Street address,APN,Centroid Lat,Centroid Lng,Annual Tax,County code`.  This gzipped CSV is served by the app.

Here's a sample final output for San Mateo:
```
101 SAN DIEGO AVE,003011260,-122.4663697567297,37.708206018415844,9173.9,SM
125 SHAKESPEARE ST,003031010,-122.46300058163514,37.708164756800194,4494.82,SM
101 SANTA CRUZ AVE,003013320,-122.46550298776202,37.70817709008342,9383.36,SM
102 SANTA CRUZ AVE,003011010,-122.4660214643012,37.70820149758747,3518.94,SM
860 BRUNSWICK ST,004261220,-122.45122997419291,37.70810413461794,9187.42,SM
425 W MAPLE WAY,068100240,-122.2796584694945,37.45555043044969,19058.62,SM
100 SANTA BARBARA AVE,003013390,-122.465166112976,37.70817368941809,11951.38,SM
55 RICE ST,004031010,-122.45759671865413,37.70822035145098,11856.58,SM
16 RAVILLA CT,004340490,-122.44807089917549,37.70835813680627,3148.0,SM
34 RICE ST,004032010,-122.45677712332471,37.70823557691507,2218.78,SM
```

Note that the parse and scrape steps are separate so that we can improve the parser without having to do a very costly and slow scrape of tax pages, and so we can share raw scraped datasets for validation and other purposes.

Some counties struggle to serve traffic or will rate limit.  It's important that crawling is respectful to the technical limitations of the county, otherwise this data will become even harder to get.

## Serving

A simple node app hosts the map and a `/lookup` endpoint.  On start it loads all parsed data into a geospatial index.  Install node dependencies with `yarn install`, populate the dataset with `yarn populate`, and then run the app with `yarn start`.  Then access via http://localhost:13000

## TODO

- Add support for more counties
- Expose a toggle for commercial/residential properties only (where data is available)
- Obtain Redfin or Zillow or other property value estimates so that we can display property tax as a % of property value
- Automatically surface interesting places?
