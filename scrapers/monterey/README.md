# Monterey
Monterey uses [MPTS web](https://common3.mptsweb.com/mbc/monterey/tax/search) to collect property taxes. I use a handful of open datasets to piece together APN, Long, Lat and Address:

- [Addresses](https://montereycountyopendata-12017-01-13t232948815z-montereyco.opendata.arcgis.com/datasets/parcel-situs-address)
- [Assessments](https://montereycountyopendata-12017-01-13t232948815z-montereyco.opendata.arcgis.com/datasets/parcel-assessment?selectedAttribute=TAXABILITY)
- [Parcel Geometry](https://montereycountyopendata-12017-01-13t232948815z-montereyco.opendata.arcgis.com/datasets/parcels-data)

`scraper.py` currently scrapes the taxes for all ASMTNUMs but the final dataset includes one tax amount per APN. 