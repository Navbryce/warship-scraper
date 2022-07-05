var Config = require('../ConfigModule');
var Ships = require('../ShipModule');

var mongoose = require('mongoose');

var edgeSchema = mongoose.Schema({
  edgeId: Number,
  source: String,
  target: String,
  any: Object // Catch all
});
var Edge = mongoose.model('edges', edgeSchema);

// Get config
var config = Config.getConfig();

// Connect to Mongo Database 'ABoat'
var connectedToDatabase = false;
mongoose.connect(config.mongoURI + '/' + config.dbName, {});
var database = mongoose.connection;

database.on('error', console.error.bind(console, 'Error when connecting to database.'));
database.once('open', function () {
  connectedToDatabase = true;
});

function getAllEdges () { // Returns promise
  return getEdges({}, {});
}

// Filter must be in the format of MongoQuerying syntax. returns promise if successful. a limit of 0 is equivalent to no limit
function getEdges (filter, sortObject) {
  // console.log(sortObject);
  // console.log('FILTER:' + JSON.stringify(filter));
  if (connectedToDatabase) {
    return Edge.find(filter).sort(sortObject).lean().exec(); // Returns ship promise. .lean() returns a JS object not a full document, so it can be modified without changing the database
  } else {
    console.log('Error. Not connected to database');
    throw new Error('The server is not connected to a database');
  }
}

// Get edges with pictures
function getEdgesWithPictures (filter, sortObject) { // Also tacks on the ships name. Edges don't hold picture/imageURL/boatName info because it's redundant and already in the database
  return new Promise((resolve, reject) => {
    var edgePromise = getEdges(filter, sortObject);
    edgePromise.then((edges) => {
      var orArray = [];
      filter = {$or: orArray};
      for (var edgeCounter = 0; edgeCounter < edges.length; edgeCounter++) {
        orArray.push({scrapeURL: edges[edgeCounter].source});
        orArray.push({scrapeURL: edges[edgeCounter].target});
      }
      var shipsPromise = Ships.getShips(filter, {}, 0); // will remove duplicates. so if two requests are for the sharnhorst, will return only 1 SCHARNHORST OBJECT
      shipsPromise.then((ships) => {
        // The image object map deals with the "removed" duplicates problem
        var imageObjectMap = {};
        var shipNameMap = {};
        for (var shipCounter = 0; shipCounter < ships.length; shipCounter++) {
          var ship = ships[shipCounter];
          imageObjectMap[ship.scrapeURL] = ship.pictures[0];
          shipNameMap[ship.scrapeURL] = ship.displayName;
        }
        // Add pictures from shipobjects to edges
        for (var edgeCounter = 0; edgeCounter < edges.length; edgeCounter++) {
          var edge = edges[edgeCounter];
          edge.sourceImage = imageObjectMap[edge.source];
          edge.sourceName = shipNameMap[edge.source];
          edge.targetImage = imageObjectMap[edge.target];
          edge.targetName = shipNameMap[edge.target];
          // console.log(edge);
        }
        resolve(edges);
      });
    });
  });
}

module.exports = {
  getEdges: getEdges,
  getAllEdges: getAllEdges,
  getEdgesWithPictures: getEdgesWithPictures
};
