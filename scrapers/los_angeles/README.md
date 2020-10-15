Data from https://geohub.lacity.org/datasets/6d85cb5f5f5641c6aa95203849ca05bb_0

This was helpful in describing parts of the dataset:
https://data.lacounty.gov/Parcel-/Assessor-Parcels-Data-2019/csig-gtr7

Lookup AIN here: https://portal.assessor.lacounty.gov/  (I don't think this does anything that we can't get from the GIS dataset)

Lookup property tax here: https://vcheck.ttc.lacounty.gov/index.php?page=selections

The scraper requires a session cookie:
- Go to the property tax link
- Complete the captcha
- Go to property tax inquiry
- Look up an AIN (like 5517-015-015) -> "Inquiry only"
- Copy `token` form param and `SSID` cookie into the parser from POST request to https://vcheck.ttc.lacounty.gov/proptax.php?page=main
