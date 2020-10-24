## Parcel List

https://opendata.slocounty.ca.gov/datasets/planning-land-use-by-parcel/data

The parcel list gets us a list of APNs, but doesn't include addresses, coordinates, or tax data.

`curl https://opendata.arcgis.com/datasets/04535c05c1d5413b9896567cec36346e_83.geojson --output datasets/parcels.geojson`

## Address / Coordinate List

https://opendata.slocounty.ca.gov/datasets/address-points/data

The address list doesn't include APN, but should be an exact match for full address provided in the assessment.

`curl https://opendata.arcgis.com/datasets/61f3ddf2074942e6932b8f5084c20ab4_0.geojson --output datasets/addresses.geojson`

## Property Information Search, `scrape_output/<apn>.assessment.html`

https://assessor.slocounty.ca.gov/assessor/pisa/Search.aspx

The assessor's search is necessary to tie APN to address.

## Property Tax Search, `scrape_output/<apn>.tax.html`

https://services.slocountytax.org/Entry.aspx

The tax search will provide 2020 property taxes for an APN.

## Chromium Issues

After around 1000 lines, The scraper will raise a bunch of "Timeout waiting for
Navigation" exceptions and every subsequent connection to Chromium in the
Python process will get stuck, so we use the `scrape.sh` bash script to scrape
in batches of 500.
