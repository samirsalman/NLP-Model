const express = require("express");
const router = express.Router();
const MongoClient = require('mongodb').MongoClient;

// Setup mongoDB connection variables
// TODO: switch this for remote url when ready
const MONGODB_URI = 'mongodb://localhost:27017';
const dbName = 'NLProject1920'
const client = new MongoClient(MONGODB_URI);
var db;

client.connect(function(err) {
  if(err) {
    console.log(err);
  }

  db = client.db(dbName);
});

//endpoint to have last news
router.get("/:date", (req, res, next) => {
  db.collection("documents").find({date: {$regex: req.params.date}}).toArray(function(err, result) {
    if (err) throw err;
    res.send(result)
  });
});

module.exports = router;
