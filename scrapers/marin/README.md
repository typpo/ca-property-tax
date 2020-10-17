Parcels: http://www.marinmap.org/dnn/DataServices/GISDataDownload.aspx

```
ogr2ogr -f GeoJSON marin.geojson parcel.shp
```

Tax lookup:

https://apps.marincounty.org/TaxBillOnline/

```
curl 'https://apps.marincounty.org/TaxBillOnline/?PropertyId=001-032-59' \
  -naH 'Cookie: ASP.NET_SessionId=cb43i2fteofouruu13vrqlpt; BNES_ASP.NET_SessionId=tpYQIn2c1x9dtg4Pr0oMa6CvBOr9/zv0WbXWALNFjdQeKlUtZ3K/c1T64zQJlJTPAYO+YiMcZMgnKyzdvmWYJX1PnCszgn7K; BNES_SameSite=4OOcDH0CIeaJGmGDBVVInvMxRwoe3/nrL6SeZAAMYuWHyU+FxQSqXA=='
```
