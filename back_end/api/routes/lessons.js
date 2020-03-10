const express = require("express");
const router = express.Router();

//endpoint to have last news
router.get("/", (req, res, next) => {
  res.send("lessons");
});

module.exports = router;
