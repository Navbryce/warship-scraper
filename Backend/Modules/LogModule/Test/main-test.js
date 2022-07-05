var LogModule = require('../../LogModule');
var fs = require('fs');

describe ('Log Tests', function () { // done is used to tell mocha that the test is comp[lete]
  it ('Make sure a log is created', () => {
    var log = new LogModule.LogWriter('test', false);
    log.log('test');
    if (fs.existsSync(log.logPath)) {
      log.deleteLog();
      return true;
    } else {
      throw new Error('The test log could not be found on the path ' + this.logPath);
    }
  });
});
