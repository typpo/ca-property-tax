const fs = require('fs');

const csvParse = require('csv-parse');
const geokdbush = require('geokdbush');
const KdBush = require('kdbush');

const MAX_NUM_RESULTS = 100;

const MAX_RADIUS_KM = 5;

class GeoIndex {
  constructor() {
    this.index = null;
  }

  async load() {
    const stream = fs.createReadStream(__dirname + '/../data/san_mateo_partial.csv');

    const parser = stream.pipe(csvParse());
    const points = [];
    for await (const record of parser) {
      const [number, street, lng, lat, tax] = record;
      if (tax <= 0) {
        continue;
      }
      points.push({ number, street, tax: parseFloat(tax), lat: parseFloat(lat), lng: parseFloat(lng) });
    }

    this.index = new KdBush(points, p => p.lng, p => p.lat);
  }

  async getNearby(lat, lng) {
    if (!this.index) {
      console.log('Lazily initializing geo index...');
      await idx.load();
    }

    const nearest = geokdbush.around(this.index, lng, lat, MAX_NUM_RESULTS, MAX_RADIUS_KM);
    return nearest.map(loc => {
      return {
        number: loc.number,
        street: loc.street,
        tax: loc.tax,
        lat: loc.lat,
        lng: loc.lng,
      };
    });
  }
}

const idx = new GeoIndex();

module.exports = {
  GeoIndex: idx,
};
