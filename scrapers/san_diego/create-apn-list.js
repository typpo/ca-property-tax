const { openDbf }= require('shapefile')
const fs = require('fs')

const parcels = './parcels/PARCELS_NORTH'
const dbfInput = `${parcels}/PARCELS_NORTH.dbf`
let table
let count = 0

const apns = []

function log(result) {
  if (result && result.value && result.value.APN) {
    apns.push(result.value.APN)
  }
  if (result.done) {
    console.log('row count', count)
    fs.writeFileSync(`${parcels}/apns-north.json`, JSON.stringify(apns, null, 2))
    console.log('wrote file')
    return
  }
  count++
  table.read().then(log)
}

openDbf(dbfInput)
  .then(dbfSource => {
    table = dbfSource
    dbfSource.read().then(log)
  })
  .catch(error => console.error(error.stack))
