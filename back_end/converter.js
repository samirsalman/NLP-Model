const excelToJson = require("convert-excel-to-json");

module.exports = function convertFile(file_path) {
  return excelToJson({
    sourceFile: file_path,
    header: {
      // Is the number of rows that will be skipped and will not be present at our result object. Counting from top to bottom
      rows: 1 // 2, 3, 4, etc.
    }
  });
};
