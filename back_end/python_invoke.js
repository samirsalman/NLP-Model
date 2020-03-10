const { spawn } = require("child_process");

class PythonInvoke {
  constructor() {}

  python = spawn("python", ["script1.py"]);

  getResults = function() {
    python.stdout.on("data", function(data) {
      console.log("Pipe data from python script ...");
      dataToSend = data.toString();
    });
    // in close event we are sure that stream from child process is closed
    python.on("close", code => {
      console.log(`child process close all stdio with code ${code}`);
      // send data to browser
      res.send(dataToSend);
    });
  };
}

module.exports = PythonInvoke;
