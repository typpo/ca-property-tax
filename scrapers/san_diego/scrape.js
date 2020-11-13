const request = require('request')
const { parse } = require('node-html-parser')
const fs = require('fs')
const searchFields = require('./searchFields.json')

const REGION = 'north'
const PARCEL_BASE = './parcels/PARCELS_NORTH'
const batchSize = 200
const processedFile = `${PARCEL_BASE}/apns-${REGION}-processed.json`
const failFile = `${PARCEL_BASE}/apns-${REGION}-failed.json`
const taxes = `${PARCEL_BASE}/taxinfo`

const apnList = JSON.parse(fs.readFileSync(`${PARCEL_BASE}/apns-${REGION}.json`))
const processed = JSON.parse(fs.readFileSync(processedFile))
const processedLookup = processed.reduce((acc, cur) => {
  acc[cur] = 1
  return acc
}, {})

const HOST = 'iwr.sdttc.com'
const SEARCH_PATH = '/paymentapplication/Search.aspx'

let batchesRetrieved = 0
let batch
let retrieved = 0
let failed = []

const unprocessed = apnList.filter(apn => !processedLookup.hasOwnProperty(apn))
console.log(`total / unprocessed ${apnList.length} / ${unprocessed.length}`)
const numberOfBatches = Math.floor(unprocessed.length / batchSize + 1)

const getAnnualPropertyTax = (apn, callback) => {
  processed.push(apn)
  // do a GET to establish a session
  console.time(`${apn} bill retrieval`)
  request(`https://${HOST}${SEARCH_PATH}`, (error, response, body) => {
    const cookies = response.headers['set-cookie'].join('; ')

    // parse response body into dom, find:  __VIEWSTATEGENERATOR, __VEWISTATE, __EVENTVALIDATION
    const root = parse(body)
    const __VIEWSTATEGENERATOR = root.querySelector('#__VIEWSTATEGENERATOR').getAttribute('value')
    const __VIEWSTATE = root.querySelector('#__VIEWSTATE').getAttribute('value')
    const __EVENTVALIDATION = root.querySelector('#__EVENTVALIDATION').getAttribute('value')

    // POST for the search
    request.post(`https://${HOST}${SEARCH_PATH}`, {
      form: {
        __VIEWSTATEGENERATOR,
        __VIEWSTATE,
        __EVENTVALIDATION,
        ...searchFields,
        'ctl00$PaymentApplicationContent$tbParcelNumber': apn,
      },
      headers: {
        'User-Agent': 'request',
        'Cookie': cookies
      }
    }, (error, response, body) => {
      // search redirects when results are available, one more GET for the result
      request(`https://${HOST}${response.headers.location}`, {
        headers: {
          'User-Agent': 'request',
          'Cookie': cookies
        }
      }, (error, response, body) => {
        console.timeEnd(`${apn} bill retrieval`)
        if (body) {
          fs.writeFileSync(`${taxes}/${apn}.html`, body)
        } else {
          failed.push(apn)
        }

        retrieved += 1
        callback()
      })
    })
  })
}

const getNext = () => {
  if (retrieved < batch.length) {
    getAnnualPropertyTax(batch[retrieved], getNext)
  } else {
    console.log(`\n${retrieved - failed.length} successful, ${failed.length} failed.`)
    batchesRetrieved += 1
    nextBatch()
  }
}

const nextBatch = () => {
  fs.writeFileSync(processedFile, JSON.stringify(processed))

  const pastFailures = JSON.parse(fs.readFileSync(failFile))
  const allFailures = [
    ...pastFailures,
    ...failed
  ]
  fs.writeFileSync(failFile, JSON.stringify(allFailures))

  retrieved = 0
  failed = []
  const batchStart = batchesRetrieved * batchSize
  const batchEnd = batchStart + batchSize
  console.log('\nbatch start/end', batchStart, batchEnd)
  batch = unprocessed.slice(batchStart, batchEnd)
  if (batchesRetrieved < numberOfBatches) {
    getNext()
  } else {
    console.log('DONE with batches')
  }
}

nextBatch()
