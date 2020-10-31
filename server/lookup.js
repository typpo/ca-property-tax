const fs = require('fs');
const zlib = require('zlib');

const csvParse = require('csv-parse');
const geokdbush = require('geokdbush');
const KdBush = require('kdbush');

const MAX_NUM_RESULTS = 250;

const MAX_RADIUS_KM = 5;

const NUM_GRIDS = 8;
const GRID_NUM_DECIMALS_ROUNDED = 3;

function getRandom(arr, n) {
  let len = arr.length;
  let result = new Array(n);
  let taken = new Array(len);
  if (n > len)
    throw new RangeError('getRandom: more elements taken than available');
  while (n--) {
    const x = Math.floor(Math.random() * len);
    result[n] = arr[x in taken ? taken[x] : x];
    taken[x] = --len in taken ? taken[len] : len;
  }
  return result;
}

function round(value, precision = GRID_NUM_DECIMALS_ROUNDED) {
  const multiplier = Math.pow(10, precision || 0);
  return Math.round(value * multiplier) / multiplier;
}

class GeoIndex {
  constructor() {
    this.index = null;
  }

  async load() {
    console.log('Loading index...');
    const gunzip = zlib.createGunzip();
    const stream = fs.createReadStream(__dirname + '/../data/ca_all.csv.gz');

    const parser = stream.pipe(gunzip).pipe(csvParse({
      relax_column_count_more: true,
    }));
    const points = [];
    for await (const record of parser) {
      const [address, apn, lng, lat, tax, county, zone] = record;
      const taxNum = parseFloat(tax);
      if (taxNum <= 0 || address === 'UNKNOWN') {
        continue;
      }
      points.push({ address, apn, county, tax: taxNum, lat: parseFloat(lat), lng: parseFloat(lng) });
    }

    this.index = new KdBush(points, p => p.lng, p => p.lat);
    this.points = points;
    console.log('Loaded index:', points.length, 'locations');
  }

  async getNearby(lat, lng, minX, minY, maxX, maxY, commercialOnly) {
    if (!this.index) {
      console.warn('Geo index not yet loaded');
      return null;
    }

    const filterFn = commercialOnly ? (record) => record.address.indexOf('(Commercial)') > -1 : undefined;
    const nearest = geokdbush.around(this.index, lng, lat, MAX_NUM_RESULTS * 4, MAX_RADIUS_KM, filterFn);
    console.log('Selecting nearest from', nearest.length, commercialOnly);
    return nearest.filter(record => {
      return minY <= record.lat && record.lat <= maxY && minX <= record.lng && record.lng <= maxX;
    }).slice(0, MAX_NUM_RESULTS);
  }

  async getWithinBounds(minX, minY, maxX, maxY, zoom, commercialOnly) {
    if (minX >= maxX || minY >= maxY) {
      console.log('Invalid bounds');
      return [];
    }
    if (!this.index) {
      console.warn('Geo index not yet loaded');
      return null;
    }

    const rawResults = this.index.range(minX, minY, maxX, maxY);
    console.log('Selecting random from', rawResults.length, commercialOnly);

    let rawResultsRandom = rawResults;
    if (rawResult.length > MAX_NUM_RESULTS) {
      rawResultsRandom = getRandom(nearest, Math.min(nearest.length, MAX_NUM_RESULTS));
    }
    let nearest = rawResultsRandom.map(idx => this.points[idx]);
    if (commercialOnly) {
      nearest = nearest.filter((record) => record.address.indexOf('(Commercial)') > -1);
    }
    return nearest;
    /*
    if (nearest.length <= MAX_NUM_RESULTS) {
      return nearest;
    }

    // Sanity check bounds
    minX = Math.max(-140, round(minX));
    minY = Math.max(25, round(minY));
    maxX = Math.min(-110, round(maxX));
    maxY = Math.min(40, round(maxY));

    const gridX = round((maxX - minX) / NUM_GRIDS);
    const gridY = round((maxY - minY) / NUM_GRIDS);

    const ret = [];
    let count = 0;
    for (let x1 = minX; x1 < maxX; x1 += gridX || count > 1e5) {
      for (let y1 = minY; y1 < maxY; y1 += gridY || count > 1e5) {
        count++;
        const x1Min = round(x1);
        const y1Min = round(y1);
        const x1Max = round(x1 + gridX);
        const y1Max = round(y1 + gridY);
        let gridContents = this.index.range(
          x1Min, y1Min, x1Max, y1Max,
        ).slice(0, 10000).map(idx => this.points[idx]);
        if (commercialOnly) {
          gridContents = gridContents.filter((record) => record.address.indexOf('(Commercial)') > -1);
        }
        if (gridContents.length < 1) {
          continue;
        }
        let maxResult = gridContents[0];
        let minResult = gridContents[0];
        gridContents.forEach(record => {
          if (record.tax > maxResult.tax) {
            maxResult = record;
          }
          if (record.tax < minResult.tax) {
            minResult = record;
          }
        });
        ret.push(maxResult);
        if (maxResult !== minResult) {
          ret.push(minResult);
        }
      }
    }
    return ret;
    */
  }
}

const idx = new GeoIndex();
idx.load();

module.exports = {
  GeoIndex: idx,
};
