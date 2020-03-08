// Libraries
const express = require('express');

const app = express();

app.get("/", function(req, res) {
    res.end("Hello World!")
})

// Listen using PORT env variable, or 3000 if not defined
app.listen(process.env.PORT || 3000);     
