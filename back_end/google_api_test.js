// ----- Google drive -----
const fs = require("fs");
const readline = require("readline");
const { google } = require("googleapis");

// If modifying these scopes, delete token.json.
const SCOPES = ['https://www.googleapis.com/auth/drive.readonly'];
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

// This function downloads the file with
// fileId = 1vC5zkPNIh2IGq0CL8mPoiPW2TU6mLavHvRd0jdOrFeI
async function downloadFile(auth)
{
  const drive = google.drive({
    version: 'v3',
    auth: auth
  });

  const fileId = '1vC5zkPNIh2IGq0CL8mPoiPW2TU6mLavHvRd0jdOrFeI';

  var response = await drive.files.export(
    { fileId,  mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},
    { responseType: "stream" }
  );

  return new Promise((resolve, reject) => {
    const dest = fs.createWriteStream("./test.xlsx");

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

// ------------ Execution starts HERE! ------------

// Load client secrets from a local file.
fs.readFile("google_drive_api/credentials.json", (err, content) => {
  if (err) return console.log("Error loading client secret file:", err);
  // Authorize a client with credentials, then call the Google Drive API.
  credentials = JSON.parse(content)
  
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
      downloadFile(oAuth2Client).then().catch(console.error);
    }
  });

});
