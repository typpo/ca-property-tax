const fs = require('fs');

const csvParse = require('csv-parse');
const geokdbush = require('geokdbush');
const KdBush = require('kdbush');

const MAX_NUM_RESULTS = 200;

const MAX_RADIUS_KM = 5;

function getRandom(arr, n) {
  var result = new Array(n),
    len = arr.length,
    taken = new Array(len);
  if (n > len)
    throw new RangeError("getRandom: more elements taken than available");
  while (n--) {
    var x = Math.floor(Math.random() * len);
    result[n] = arr[x in taken ? taken[x] : x];
    taken[x] = --len in taken ? taken[len] : len;
  }
  return result;
}

class GeoIndex {
  constructor() {
    this.index = null;
  }

  async load() {
    const stream = fs.createReadStream(__dirname + '/../data/bay_area_all.csv');

    const parser = stream.pipe(csvParse());
    const points = [];
    for await (const record of parser) {
      const [address, apn, lng, lat, tax, county] = record;
      if (tax <= 0 || !address || address === 'UNKNOWN') {
        continue;
      }
      points.push({ address, apn, county, tax: parseFloat(tax), lat: parseFloat(lat), lng: parseFloat(lng) });
    }

    this.index = new KdBush(points, p => p.lng, p => p.lat);
    this.points = points;
  }

  async getNearby(lat, lng) {
    if (!this.index) {
      console.log('Lazily initializing geo index...');
      await idx.load();
    }

    const nearest = geokdbush.around(this.index, lng, lat, MAX_NUM_RESULTS, MAX_RADIUS_KM);
    return nearest;
  }

  async getWithinBounds(minX, minY, maxX, maxY, zoom) {
    if (!this.index) {
      console.log('Lazily initializing geo index...');
      await idx.load();
    }

    const nearest = this.index.range(minX, minY, maxX, maxY).map(idx => this.points[idx]);
    /*
    if (zoom >= 18) {
      // Return all
      return nearest.slice(0, MAX_NUM_RESULTS);
    }
    */
    return getRandom(nearest, Math.min(nearest.length, MAX_NUM_RESULTS));
  }
}

const idx = new GeoIndex();

module.exports = {
  GeoIndex: idx,
};
