Parcel data: https://data.acgov.org/datasets/b55c25ae04fc47fc9c188dbbfcd51192_0

Convert geodb to geojson: `ogr2ogr -f GeoJSON alameda.geojson ./7eb61d71fe084eb6b979a19235c83724.gdb/`

Use codes info: https://www.acgov.org/MS/prop/useCodeList.aspx

Alternative: do it without a scrape using the `TotalNetValue` field.  However this requires estimating local tax rates.
