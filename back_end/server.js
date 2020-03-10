// ----------------- Modules used -----------------

// To convert xlsx or xls to JSON
const readXlsxFile = require("read-excel-file/node");

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

// To access other routes to our server
const lessonsRoute = require("./api/routes/lessons");

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
function downloadDrive() {
  // Load client secrets from a local file.
  fs.readFile("google_drive_api/credentials.json", (err, content) => {
    if (err) return console.log("Error loading client secret file:", err);
    // Authorize a client with credentials, then call the Google Drive API.
    credentials = JSON.parse(content);

    const { client_secret, client_id, redirect_uris } = credentials.installed;
    var oAuth2Client = new google.auth.OAuth2(
      client_id,
      client_secret,
      redirect_uris[0]
    );

    // Check if we have previously stored a token.
    fs.readFile(TOKEN_PATH, (err, token) => {
      if (err) {
        // If we don't have the token, we have to get it from google
        // servers.
        return getAccessToken(oAuth2Client);
      } else {
        oAuth2Client.setCredentials(JSON.parse(token));

        // We have the token and we are ready to download the
        // files. Before downloading we have to list them though.
        listFiles(oAuth2Client)
          .then(response => {
            response.data["files"].forEach(file => {
              const fileId = file.id;
              const fileName = file.name;

              // Download the file
              downloadFile(oAuth2Client, fileName, fileId)
                .then()
                .catch(console.error);
            });
          })
          .catch(console.error);
      }
    });
  });
}

// ----------------- Main code -----------------

// TODO: finish to implement this.
//
// This function reads the entire content of the file 'filename' in
// order to process the lessons that have not yet been processed.
function processFile(filename) {
  // 1) convert xlsx or xls to JSON
  readXlsxFile(filename, { schema }).then(({ rows, errors }) => {
    // 2) get from DB all dates (lessons) which were already processed
    var processed_dates = []; // ["4-3-2019"] to exclude the fourth of march

    // 3) exclude the dates (lessons) that were already processed
    var rows_to_process = [];
    rows.forEach(row => {
      var student_date =
        row["dataLezione"].getDate() +
        "-" +
        row["dataLezione"].getMonth() +
        "-" +
        row["dataLezione"].getFullYear();
      var timestamp_date =
        row["timestamp"].getDate() +
        "-" +
        row["timestamp"].getMonth() +
        "-" +
        row["timestamp"].getFullYear();

      if (!processed_dates.includes(student_date)) {
        rows_to_process.push(row);
      }
    });

    // 4) write rows to process in file "rows_to_process.json"
    var file = fs.createWriteStream(DATA_FOLDER + "rows_to_process.json");
    file.on("error", function(err) {
      console.log(err);
    });
    data = JSON.stringify(rows_to_process);
    file.write(data);

    // 5) process the rows in "rows_to_process.json" and write the
    // clusters in file './tmp_data/clusters_results.json'

    // 6) load the file './tmp_data/clusters_results.json' on DB for
    // future querying.
  });
}

// TODO: implement this.
//
// This is the main function that process the entire contents of the
// google drive associated to the gmail account
// torvergatanlp1920@gmail.com.
function processDrive(filename) {
  console.log("STUB: processDrive()!\n");

  // 1) execute downloadDrive() to download all files from google
  // drive to ./tmp_data/ folder.

  // 2) find all .xlsx files in ./tmp_data and process each of them
  // using processFile(filename) function.

  // 3) delete all .xlsxs files in ./tmp_data.
}

// ----------------- Database code -----------------

// ----------------- RESTful web interface -----------------
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use("/lessons", lessonsRoute);

app.get("/", function(req, res) {
  res.send("Hello World!");
});

app.listen(PORT, function() {
  console.log(`I'm listening on port : `, PORT);
});

pythonInvoke.getResults();

// ----------------- Code that gets executed -----------------

// downloadDrive();

const filename = "tmp_data/2018_2019_FoI Class Feedback Form (Responses).xlsx";
//sprocessFile(filename);
