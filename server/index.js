const express = require('express');
const cors = require('cors');

const { caPropertyLookup } = require('./handlers');

const app = express();
app.use(cors());
app.use(express.static(__dirname + '/../app'));

app.get('/lookup', caPropertyLookup);

app.listen(process.env.PORT || 13000, '0.0.0.0', () => {
  console.log('App listening...');
});
