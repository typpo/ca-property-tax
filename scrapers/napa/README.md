Parcel data: http://gis.napa.ca.gov/giscatalog/catalog_xml.asp Look for `parcels_public`

The Shapefile can be converted to GeoJSON:

```
ogr2ogr -f GeoJSON -t_srs EPSG:4326 napa.geojson parcels_public.shp
```
