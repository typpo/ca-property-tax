const express = require('express');
const cors = require('cors');

const { GeoIndex } = require('./lookup');

const app = express();
app.use(cors());

app.get('/lookup', async (req, res) => {
  const lat = parseFloat(req.query.lat);
  const lng = parseFloat(req.query.lng);

  if (isNaN(lat) || isNaN(lng)) {
    res.status(500).json({
      error: 'Invalid latlng',
    });
    return;
  }

  const ret = await GeoIndex.getNearby(lat, lng);
  res.json({
    results: ret,
  });
});

app.listen(process.env.PORT || 13000, '0.0.0.0', () => {
  console.log('App listening...');
});
