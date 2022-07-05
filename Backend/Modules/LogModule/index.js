var fs = require('fs');
var util = require('util');
var moment = require('moment');

function LogWriter (logPath, logName, keepExistingContents) {
   // Assumes the SHIP_APP path has been s (TODO: logPath deprecated)
  this.deleteLog = () => {
    writeStream.close();
    fs.unlink(this.logPath, (error) => {
      console.log('A file could not be found on the path: ' + this.logPath);
      console.error(error);
    });
  };
  this.log = (string) => {
    var stringsList = getArrayOfStrings(string); // If there are multiple lines, break them up so a timestamp can be added to each. Timestamp won't be reflective of actual time of line because we're breaking them up post fact
    stringsList.forEach((individualString) => {
      individualString = moment().format() + ': ' + util.format(string) + '\r\n';
      this.rawLog(individualString);
    });
  };
  this.rawLog = (string) => {
    writeStream.write(string); // Writes string immediatly to log. Does nothing to it
  };

  function getArrayOfStrings (string) { // Will return an array of strings. A single string is broken into elements of an array if therer is a space
    return string.split(/\r\n|\r|\n/g); // Doesn't always work for python for some reason
  }
  // Constructor
  this.logPath = process.cwd() + '/Logs/' + logName + '.log';

  try {
    fs.existsSync(process.cwd() + '/Logs') || fs.mkdirSync(process.cwd() + '/Logs');
  } catch (error) {
    this.error(error);
  }

  try {
    var existingLogContents = null;
    if (fs.existsSync(this.logPath)) { // Because createWriteStream will delete the existing file. If it already exists, PULL out the existing data from the file
      existingLogContents = fs.readFileSync(this.logPath).toString();
    }
  } catch (error) {
    this.error(error);
  }

  var writeStream = fs.createWriteStream(this.logPath, {flags: 'w'});

  if (existingLogContents != null && keepExistingContents) { // if there is preexisting contents in the log and the user wants to keep it
    this.log(existingLogContents);
    this.log('ALL DATA BEFORE THIS POINT WAS FROM A PRE-EXISTING LOG FILE');
  }
}
LogWriter.prototype.error = (error) => {
  console.log(error);
}

module.exports = {
  LogWriter: LogWriter
};
