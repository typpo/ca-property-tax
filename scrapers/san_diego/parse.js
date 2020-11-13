const fs = require('fs')
const { parse: htmlParser } = require('node-html-parser')
const shapefile = require('shapefile')
const turf = require('@turf/turf')

const PARCEL_BASE = './parcels/PARCELS_NORTH'
const BILLS = `${PARCEL_BASE}/taxinfo`

const propertyTaxLookup = {}
const files = fs.readdirSync(BILLS).filter(file => file.includes('.html'))
let processed = 0
let taxesFound = 0
while (processed < files.length) {
  const htmlString = fs.readFileSync(`${BILLS}/${files[processed]}`)
  const html = htmlParser(htmlString)
  const apn = files[processed].split('.')[0]
  const totalTaxes = html.querySelectorAll('.gridRowNumeric.hidden-xs').filter(el => !el.getAttribute('rowspan'))
  if (totalTaxes && totalTaxes[0] && totalTaxes[1]) {
    const first = +totalTaxes[0].rawText.replace(/\$|,/g, '')
    const second = +totalTaxes[1].rawText.replace(/\$|,/g, '')
    propertyTaxLookup[apn] = first + second
    taxesFound += 1
  } else {
    console.log('No taxes found for', apn)
  }
  processed += 1
}
console.log('created property tax lookup')

const PARCELS = `${PARCEL_BASE}/WGS84/PARCELS_NORTH_WGS84.shp`
const CENTERS = `${PARCEL_BASE}/_bills.csv`
const outStream = fs.createWriteStream(CENTERS)
outStream.write('ADDRESS,APN,LONGITUDE,LATITUDE,PROPERTY_TAX,COUNTY\n')
let shapes
let parcelsMatched = 0

function log(result) {
  if (result.done) {
    outStream.end()
    console.log('\nend of shapefile stream')
    console.log(`Taxes found:  ${taxesFound}, matched ${parcelsMatched} parcels.`)
    console.log(`wrote ${CENTERS}`)
    return
  }

  if (propertyTaxLookup.hasOwnProperty(result.value.properties.APN)) {
    const centerOfMass = turf.centerOfMass(result.value)
    const {
      APN,
      SITUS_STRE: street,
      SITUS_SUFF: suffix,
      SITUS_ADDR: address
    } = result.value.properties
    const fullAddress = [address, street, suffix].join(' ').trim()
    const streetAddress = street ? `${fullAddress}` : 'unknown'
    const row = [
      streetAddress,
      APN,
      centerOfMass.geometry.coordinates[0].toFixed(6),
      centerOfMass.geometry.coordinates[1].toFixed(6),
      propertyTaxLookup[APN],
      'SD'
    ]
    outStream.write(`${row.join(',')}\n`)
    parcelsMatched += 1
  }
  shapes.read().then(log)
}

shapefile.open(PARCELS)
  .then(source => {
    shapes = source
    source.read().then(log)
  })
  .catch(error => console.error(error.stack))
