Parcels data: https://yodata-yolo.opendata.arcgis.com/datasets/f950580d0dbd4cc0a203c04fa7f3d987_0

Convert to geojson:
```
ogr2ogr -f GeoJSON yolo.geojson ./22af730750264d81a733373c107c3563.gdb/
```

Use field `MEGA_APN` to perform tax lookup: https://common2.mptsweb.com/MBC/yolo/tax/main/030310003000/2020/0000 (for MEGA_APN `030310003000`)
