Parcels:  https://rdw.sandag.org/Account/gisdtview?dir=Parcel (free registration required)

Tax:  https://iwr.sdttc.com/paymentapplication/Search.aspx

Parcels are split in three regions:  north, south, and east. Re-project parcels shapefiles from state plane to wgs84 before doing the parse step so that parcel coordinates in the output csv are latitude and longitude.

Run `npm i` for dependencies.

Use `create-apn-list.js` to read a .dbf file and create a new file with all APNs from a shapefile. In `scrape.js`, specify the output directory for scraped files. Do the same for `parse.js` which will create a .csv file that can be used by the web app.
