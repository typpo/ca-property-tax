const express = require('express');
const cors = require('cors');

const { GeoIndex } = require('./lookup');

const app = express();
app.use(cors());
app.use(express.static(__dirname + '/../app'));

app.get('/lookup', async (req, res) => {
  const lat = parseFloat(req.query.lat);
  const lng = parseFloat(req.query.lng);
  const zoom = parseInt(req.query.zoom, 10);
  const minX = parseFloat(req.query.minX);
  const minY = parseFloat(req.query.minY);
  const maxX = parseFloat(req.query.maxX);
  const maxY = parseFloat(req.query.maxY);

  if (isNaN(lat) || isNaN(lng)) {
    res.status(500).json({
      error: 'Invalid latlng',
    });
    return;
  }

  let ret;
  if (zoom >= 18) {
    ret = await GeoIndex.getNearby(lat, lng, minX, minY, maxX, maxY);
  } else {
    ret = await GeoIndex.getWithinBounds(minX, minY, maxX, maxY, zoom);
  }
  res.json({
    results: ret.map(loc => {
      return [loc.address, loc.apn, loc.tax, loc.county, loc.lat, loc.lng];
    }),
  });
});

app.listen(process.env.PORT || 13000, '0.0.0.0', () => {
  console.log('App listening...');
});
