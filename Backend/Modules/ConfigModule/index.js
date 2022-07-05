var config = null;

config = {
  host: process.env.HOST ?? "0.0.0.0",
  port: process.env.PORT ?? "8080",
  mongoURI: process.env.MONGO_URI,
  dbName: process.env.MONGO_DB_NAME
}

function getConfig () {
  return config;
}

module.exports = {
  getConfig: getConfig
};
