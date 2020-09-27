const { GeoIndex } = require('./lookup');

async function lookup(req, res) {
  const lat = parseFloat(req.params.lat);
  const lng = parseFloat(req.params.lng);

  const ret = await GeoIndex.lookup(lat, lng);
  res.json(ret);
}

module.exports = {
  lookup,
};
