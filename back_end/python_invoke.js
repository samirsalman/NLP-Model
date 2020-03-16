const { PythonShell } = require("python-shell");

function getResults() {
  var options = {
    mode: "text",
    args: ["./tmp_data/rows_to_process.json"]
  };

  /*lo script prende in input il path del dataset e crea 4 file 
    - cluster_results.json: rappresenta il file risultante con i clustet
    - data.csv: contiene informazioni riguardanti frasi e vettori e similarità tra frasi
    - results.csv: contiene informazioni riguardanti frasi e vettori
    - dates.json: contiene tutte le date contenute nel dataset

  ])*/
  return PythonShell.run("./py_process/main.py", options, function(
    err,
    results
  ) {
    if (err) throw err;
    // results is an array consisting of messages collected during execution
    console.log("results: %j", results);
  });
}

module.exports = { getResults };

