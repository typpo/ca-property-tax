Parcels: https://gis.cccounty.us/Downloads/Assessor/

Convert parcels to geojson:
```
ogr2ogr -f GeoJSON contra_costa.geojson Parcels_Public_August2020.shp
```

XY coords are in 0403 - California Zone 3 US Survey Feet

Help with coord systems:
- https://gis.stackexchange.com/questions/120083/converting-a-california-coordinate-system-zone-6-value
- https://stackoverflow.com/questions/49742767/pyproj-transformation-from-ca-state-plane-coordinates-to-lat-long-not-as-expect
- https://pyproj4.github.io/pyproj/stable/examples.html
- https://gis.stackexchange.com/questions/217939/converting-state-plane-coordinates-to-latitude-longitude
- https://www.earthpoint.us/StatePlane.aspx
- https://www.conservation.ca.gov/cgs/Pages/Program-RGMP/california-state-plane-coordinate-system.aspx
