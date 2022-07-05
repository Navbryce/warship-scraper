const express = require('express');
const router = express.Router();
var graphs = require('../Modules/GraphModule');

router.get('/', function (req, res) {
  res.send('You have attempted to access the graphs backend. Return to main page.');
});
router.post('/getAllEdges', (req, res) => {
  var edgesPromise = graphs.getEdgesWithPictures({}, {});
  edgesPromise.then((edges) => {
    res.send(JSON.stringify(edges));
  });
});
module.exports = router;
