Parcel data: https://www.co.fresno.ca.us/departments/public-works-planning/divisions-of-public-works-and-planning/cds/gis-shapefiles Look for `Parcels`

The Shapefile can be converted to GeoJSON:

```
ogr2ogr -f GeoJSON -t_srs EPSG:4326 fresno.geojson Fresno_Parcels.shp
```

The assessment information can be retrieved from: https://www2.co.fresno.ca.us/0410/FresnoTTCPaymentApplication/SecuredDetails.aspx?id=<numerical id>&PropertyType=1

NOTE: The records are stored by enumerated id, can be stepped through from 1 to 298820

The APN has three parts, and the assessed value can be retrieved via:

https://assrmaps.co.fresno.ca.us/binlookup/ParcelLookup.aspx?SearchType=0&Book=<APN part 1>&Page=<APN part 2>&BlockParcel=<APN part 3>
