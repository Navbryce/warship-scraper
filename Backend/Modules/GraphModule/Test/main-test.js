var graphModule = require('../../GraphModule');
describe ('Edges Tests', function (done) { // done is used to tell mocha that the test is comp[lete]
  this.timeout(10000); // Takes longer than most other tests because each unit needs to query databases

  it ('Makes sure edges are in the database and can connect to the database', (done) => {
    setTimeout(() => { // Gives the database enough time to connect
      var edges = [];
      graphModule.getAllEdges().then((data) => {
        edges = data;
        if (edges.length > 0) {
          return done();
        } else {
          return done('An error occurred');
        }
      });
    }, 200);
  });

  it ('Makes sure can get edges with photos', (done) => {
    setTimeout(() => { // Gives the database enough time to connect
      var edges = [];
      graphModule.getEdgesWithPictures({}, {}).then((data) => {
        // console.log(data);
        edges = data;
        if (edges.length > 0) {
          return done();
        } else {
          return done('An error occurred');
        }
      });
    }, 200);
  });
});
