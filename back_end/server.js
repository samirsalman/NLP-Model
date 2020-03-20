// ----------------- Modules used -----------------

// To convert xlsx or xls to JSON
const readXlsxFile = require("read-excel-file/node");

const hash = require("hash-string");

// To invoke python script
const pythonInvoke = require("./python_invoke");

// To interact with file system
const fs = require("fs");

const readline = require("readline");

// To use google drive APIs
const { google } = require("googleapis");

// To define RESTful web interface
const express = require("express");

// To receive and send complex http requests (example http request
// with json in the body)
var cors = require("cors");

// To parse the json received in the body of the http request
const bodyParser = require("body-parser");

// To deal with DB management
const MongoClient = require("mongodb").MongoClient;
const assert = require("assert");

// To access other routes to our server
const lessonsRoute = require("./api/routes/lessons");
const clustersRoute = require("./api/routes/clusters");

// ----------------- Global variables -----------------

// folder that contains various file stored for processing.
const DATA_FOLDER = "./tmp_data/";

// schema used to convert .xlsx document into json format.
const schema = {
  Timestamp: {
    prop: "timestamp",
    type: Date
  },
  'Codice (Inserire il "vostro codice personale" fornito per il corso)': {
    prop: "codice",
    type: String
  },
  "Data della lezione": {
    prop: "dataLezione",
    type: Date
  },
  "Descrivi il messaggio principale di questa lezione": {
    prop: "messaggio",
    type: String
  },
  "Quale argomento ti ha interessato di più di questa lezione e ne vorresti sapere di più?": {
    prop: "argomento",
    type: String
  },
  "Qual è stata la parte meno chiara di questa lezione?": {
    prop: "chiarimenti",
    type: String
  }
};

// ----------------- Google drive code -----------------

// If modifying these scopes, delete token.json.
const SCOPES = ["https://www.googleapis.com/auth/drive.readonly"];
// The file token.json stores the user's access and refresh tokens, and is
// created automatically when the authorization flow completes for the first
// time.
const TOKEN_PATH = "google_drive_api/token.json";

/**
 * Get and store new token after prompting for user authorization, and then
 * execute the given callback with the authorized OAuth2 client.
 * @param {google.auth.OAuth2} oAuth2Client The OAuth2 client to get token for.
 * @param {getEventsCallback} callback The callback for the authorized client.
 */
function getAccessToken(oAuth2Client) {
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: "offline",
    scope: SCOPES
  });
  console.log("Authorize this app by visiting this url:", authUrl);
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  rl.question("Enter the code from that page here: ", code => {
    rl.close();
    oAuth2Client.getToken(code, (err, token) => {
      if (err) return console.error("Error retrieving access token", err);
      oAuth2Client.setCredentials(token);
      // Store the token to disk for later program executions
      fs.writeFile(TOKEN_PATH, JSON.stringify(token), err => {
        if (err) return console.error(err);
        console.log("Token stored to", TOKEN_PATH);
      });
      return oAuth2Client;
    });
  });
}

// This function list all avaiable files in google drive using google
// drive APIS.
async function listFiles(auth, list) {
  const drive = google.drive({
    version: "v3",
    auth: auth
  });

  var response = await drive.files.list({
    pageSize: 20,
    fields: "nextPageToken, files(id, name)"
  });

  return response;
}

// This function downloads the file with given fileId using google
// drive APIs
async function downloadFile(auth, fileName, fileId) {
  const drive = google.drive({
    version: "v3",
    auth: auth
  });

  var response = await drive.files.export(
    {
      fileId,
      mimeType:
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    },
    { responseType: "stream" }
  );

  return new Promise((resolve, reject) => {
    const dest = fs.createWriteStream(DATA_FOLDER + fileName + ".xlsx");

    response.data
      .on("end", () => {
        console.log("Done downloading file.");
        resolve();
      })
      .on("error", err => {
        console.error("Error downloading file.");
        reject(err);
      })
      .pipe(dest);
  });
}

// This function downloads the entire content of the google drive
// associated with the gmail account torvergatanlp1920@gmail.com to
// the folder ./tmp_data
async function downloadDrive() {
  // Load client secrets from a local file.

  var credentials;
  var token_data;

  try {
    // read files
    var content = fs.readFileSync("google_drive_api/credentials.json");
    credentials = JSON.parse(content);
    token_data = fs.readFileSync(TOKEN_PATH);
  } catch (err) {
    // TODO: better error management
    console.log(err);
    return;
  }

  // set credentials from data obtained from files
  const { client_secret, client_id, redirect_uris } = credentials.installed;
  var oAuth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    redirect_uris[0]
  );

  oAuth2Client.setCredentials(JSON.parse(token_data));

  // We have the token and we are ready to download the
  // files. Before downloading we have to list them though.
  var response = await listFiles(oAuth2Client);
  var i;
  for (i = 0; i < response.data["files"].length; i++) {
    var fileName = response.data["files"][i].name;
    var fileId = response.data["files"][i].id;
    console.log("before downloadFile()");
    await downloadFile(oAuth2Client, fileName, fileId);
    console.log("after downloadFile()");
  }
}
async function deleteTempData(pathToFile) {
  await fs.unlink(pathToFile, function(err) {
    if (err) {
      console.log("Error to delete temp files");
      return false;
    } else {
      console.log("Deleted " + pathToFile.toString());

      return true;
    }
  });
}

// ----------------- Main code -----------------

// TODO: finish to implement this.
//
// This function reads the entire content of the file 'filename' in
// order to process the lessons that have not yet been processed.
function processFile(db, filename) {
  console.log("PROCESS FILE");

  // 1) convert xlsx or xls to JSON
  readXlsxFile(filename, { schema }).then(async function({ rows, errors }) {
    // 2) get from DB all dates (lessons) which were already
    // processed. In particular it loads the latest date processed. We
    // assume that all dates before that one were already processed.
    const metaDataCollection = db.collection("meta-data");

    var response = await metaDataCollection
      .find({}, { projection: { hash: 1 } })
      .toArray();

    response = response.map(el => el.hash);
    console.log(response);

    // 3) exclude the dates (lessons) that were already processed
    var rows_to_process = [];
    var j = 0;
    rows.forEach(row => {
      if (j < 600) {
        row["hash"] = hash(row["codice"] + row["dataLezione"]).toString();
        if (!response.includes(row["hash"])) {
          rows_to_process.push(row);
        }
      }
      j += 1;
    });

    // 4) write rows to process in file "rows_to_process.json"
    var file = fs.createWriteStream(DATA_FOLDER + "rows_to_process.json");
    file.on("error", function(err) {
      console.log(err);
    });
    data = JSON.stringify(rows_to_process);
    file.write(data);

    metaDataJSON = rows_to_process.map(el => {
      return { hash: el.hash, codice: el.codice, data: el.dataLezione };
    });

    if (metaDataJSON !== null && metaDataJSON.length > 0) {
      metaDataCollection.insertMany(metaDataJSON, function(err, result) {
        if (err) {
          console.log(err);
        } else {
          console.log("[DEBUG]: Added meta-data to DB");
          console.log("Added " + metaDataJSON.length);
        }
      });
    }

    // 5) process the rows in "rows_to_process.json" and write the
    // clusters in file './tmp_data/clusters_results.json'
    //
    // NOTE: Need specific model to do this
    //
    await pythonInvoke.getResults().on("close", (data, err) => {
      var json = require("./tmp_data/clusters_results.json");
      const collection = db.collection("documents");
      collection.insertMany(json, function(err, result) {
        if (err) {
          console.log(err);
        } else {
          console.log("[DEBUG]: Added document to DB");
          deleteTempData("./tmp_data/rows_to_process.json");
          deleteTempData("./tmp_data/clusters_results.json");
          deleteTempData("./tmp_data/data.csv");
          deleteTempData("./tmp_data/results.csv");
          deleteTempData("./tmp_data/dates.json");
          deleteTempData(filename);
        }
      });
    });

    // 6) load the file './tmp_data/clusters_results.json' on DB for
    // future querying.
  });
}

async function downloadFilesFromDrive() {
  return fs.readFile("google_drive_api/credentials.json", (err, content) => {
    if (err) return console.log("Error loading client secret file:", err);
    // Authorize a client with credentials, then call the Google Drive API.
    credentials = JSON.parse(content);

    const { client_secret, client_id, redirect_uris } = credentials.installed;
    var oAuth2Client = new google.auth.OAuth2(
      client_id,
      client_secret,
      redirect_uris[0]
    );

    fs.readFile(TOKEN_PATH, async (err, token) => {
      if (err) {
        // If we don't have the token, we have to get it from google
        // servers.
        return getAccessToken(oAuth2Client);
      } else {
        oAuth2Client.setCredentials(JSON.parse(token));

        // We have the token and we are ready to download the
        // files. Before downloading we have to list them though.
        var response = await listFiles(oAuth2Client).catch(err, () =>
          console.log(err)
        );
        console.log(response);
        fs.readFile(TOKEN_PATH, async (err, token) => {
          if (err) {
            // If we don't have the token, we have to get it from google
            // servers.
            return getAccessToken(oAuth2Client);
          } else {
            oAuth2Client.setCredentials(JSON.parse(token));

            // We have the token and we are ready to download the
            // files. Before downloading we have to list them though.
            var response = await listFiles(oAuth2Client).catch(err, () =>
              console.log(err)
            );

            var i = 0;
            for (j in response.data["files"]) {
              console.log(response.data["files"][j]);

              var fileId = response.data["files"][j].id;
              var fileName = response.data["files"][j].name;

              var procedure = await downloadFile(
                oAuth2Client,
                fileName,
                fileId
              );
              const dest = fs.createWriteStream(
                DATA_FOLDER + fileName + ".xlsx"
              );

              procedure
                .on("end", () => {
                  console.log("Done downloading file.");
                  console.log("FILE DOWNLOAD COMPLETED" + i);
                  i += 1;
                })
                .on("error", err => {
                  console.error("Error downloading file.");
                  reject(err);
                })
                .pipe(dest);
            }
          }
        });
      }
    });
  });
}

// TODO: implement this.
//
// This is the function that process the entire contents of the google
// drive associated to the gmail account torvergatanlp1920@gmail.com.
function processDrive(filename) {
  console.log("STUB: processDrive()!\n");

  // 1) execute downloadDrive() to download all files from google
  // drive to ./tmp_data/ folder.

  // 2) find all .xlsx files in ./tmp_data and process each of them
  // using processFile(filename) function.

  // 3) delete all .xlsxs files in ./tmp_data.
}

// TODO: implement this.
//
// This is the main function when the server startsup. This function
// periodically executes the function processDrive().
async function main() {
  console.log("STUB: processDrive()!\n");

  // TODO: use set interval
  const client = new MongoClient(MONGODB_URI);

  // Connect to db server
  client.connect(async function(err) {
    if (err) {
      console.log(err);
    }

    await downloadDrive();
    console.log("after");
    const filename =
      "./tmp_data/2018_2019_FoI Class Feedback Form (Responses).xlsx";
    const db = client.db(dbName);
    processFile(db, filename);

    app.listen(PORT, function() {
      console.log(`I'm listening on port : `, PORT);
    });
  });
}

// ----------------- Code that gets executed -----------------

// Setup RESTful API endpoints
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use("/lessons", lessonsRoute);
app.use("/clusters", clustersRoute);

app.get("/", (req, res) => {
  res.send(`Homepage, request from ${req.host}`);
});

// Setup mongoDB connection variables
// TODO: switch this for remote url when ready
const MONGODB_URI =
  "mongodb+srv://progettoNLP1920:nlpisbad@nlproject1920-zmx1q.mongodb.net/test?retryWrites=true&w=majority";
const dbName = "NLProject1920";
const client = new MongoClient(MONGODB_URI);

// Connect to db server
main();
