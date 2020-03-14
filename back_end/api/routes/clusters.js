const express = require("express");
const router = express.Router();

// To invoke python script
const pythonInvoke = require("../../python_invoke");

// To interact with file system
const fs = require("fs");

router.get("/", function(req, res) {
  console.log(`GET REQUEST AT "/clusters" from ${req.host} `);
  var struct = "";
  var response = pythonInvoke.getResults();

  response.on("message", function(message) {
    struct += message;
  });

  response.on("close", function(result) {
    fs.readFile("./tmp_data/clusters_results.json", "utf8", (err, text) => {
      if (err) {
        console.log(err);
      }
      var result = {
        message:
          "Clusters created, file ready at './tmp_data/clusters_results.json'",
        clusters: JSON.parse(text)
      };
      res.send(result);
    });
  });
});

module.exports = router;
