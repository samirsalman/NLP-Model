const spawn = require("child_process").spawn;

function getResults() {
  var python = spawn("python", ["./script1.py"]);

  process.stdout.on("data", function(chunk) {
    var textChunk = chunk.toString("utf8"); // buffer to string

    util.log(textChunk);
  });
}

module.exports = { getResults };
