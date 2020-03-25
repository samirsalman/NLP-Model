const express = require("express");
const router = express.Router();
const MongoClient = require("mongodb").MongoClient;

// mongoDB connection variables
const MONGODB_URI = "mongodb+srv://progettoNLP1920:nlpisbad@nlproject1920-zmx1q.mongodb.net/test?retryWrites=true&w=majority";
const dbName = "NLProject1920";
const client = new MongoClient(MONGODB_URI);
var db;

client.connect(function(err) {
  if (err) {
    console.log(err);
  }

  db = client.db(dbName);
});

// This endpoint returns the clusters associated with the latest
// lecture.
router.get('/latest', (req, res, next) => {  
  db.collection("documents")
    .find()
    .sort({"date":-1})
    .limit(3)
    .toArray(function(err, result) {
      if(err) throw err;
      else {
	res.send(result);
      }
    });
});

// This endpoints returns the clusters associated with the given
// lesson. For example, doing /lessons/03-04-2019 will return the
// clusters that are associated to the lesson made on the third day of
// April.
router.get("/:date", (req, res, next) => {
  db.collection("documents")
    .find({ date: { $regex: req.params.date } })
    .toArray(function(err, result) {
      if (err) throw err;
      res.send(result);
    });
});

router.get("/students/:id", (req, res, next) => {
  db.collection("documents")
    .find({ person_id: { $regex: req.params.id } })
    .toArray(function(err, result) {
      if (err) throw err;
      res.send(result);
    });
});

module.exports = router;
