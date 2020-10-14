Parcels: https://gis.cccounty.us/Downloads/Assessor/

Convert parcels to geojson:
```
ogr2ogr -f GeoJSON contra_costa.geojson Parcels_Public_August2020.shp
```

XY coords are in 0403 - California Zone 3 US Survey Feet
