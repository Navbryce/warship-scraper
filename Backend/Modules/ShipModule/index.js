var Config = require('../ConfigModule');
var mongoose = require('mongoose');

var shipSchema = mongoose.Schema({
  scrapeURL: String,
  configuration: String,
  displayName: String,
  name: String,
  importantDates: Object,
  awards: Object,
  armament: Object,
  armor: Object,
  description: String,
  physicalAttributes: Object,
  pictures: Object,
  complement: Number,
  any: Object // Catch all. Ships are dynamic and don't always have the same attributes
});
var Ship = mongoose.model('ships', shipSchema);

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

// Filter must be in the format of MongoQuerying syntax. returns promise if successful. a limit of 0 is equivalent to no limit
function getShips (filter, sortObject, limit) {
  // console.log(sortObject);
  console.log('FILTER:' + JSON.stringify(filter));
  if (connectedToDatabase) {
    return Ship.find(filter).sort(sortObject).limit(limit).exec(); // Returns ship promise
  } else {
    throw new Error('The server is not connected to a database');
  }
}

// Returns promise. Gets the {numberOfShips} ships with a displayName > minDisplayName. Ships must also meet filter. Each 'filter' for a field should be in the form of an OBJECT!
function getShipsAfterName (minDisplayName, filter, sort, numberOfShips) {
  if (filter.displayName != null) { // If the filter already has something on it, add the minimum filter to the existing one
    filter.displayName.$gt = minDisplayName;
  } else {
    filter.displayName = {$gt: minDisplayName}; // There is no filter for the displayName
  }
  if (connectedToDatabase) {
    return getShips(filter, sort, numberOfShips);
  } else {
    throw new Error('The server is not connected to a database');
  }
}

module.exports = {
  getShips: getShips,
  getShipsAfterName: getShipsAfterName
};
