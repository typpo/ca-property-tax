Parcel data: https://hub.arcgis.com/datasets/ButteCountyGIS::assessor-tax-parcels
The Shapefile can be converted to GeoJSON:

```
ogr2ogr -f GeoJSON butte_parcels.geojson LandUse_OpenData.shp
```

`create_parcels_db.py` will generate a db file with the GeoJSON data converted, keyed by APN

`scrape.py` will read the APN from the db file and retrieve the tax information.

`parse.py` will update the tax value from the scraped data.

`export_parcels_db.py` will output the parcels in the db file to CSV.
