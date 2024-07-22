function sendVariablesToCloudFunction() {

    // retrieve and process user variables
    var variablesSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("1: set variables");
    var titles = variablesSheet.getRange("C5:C43").getValues();
    var values = variablesSheet.getRange("D5:D43").getValues();
    var user_variables = {};
    for (var i = 0; i < titles.length; i++) {
      var key = titles[i][0];
      var value = values[i][0];
      if (key && value) { // Ensuring neither the key nor the value is empty
        user_variables[key] = value;
      }
    }
     
    // retrieve and process result page column headers
    var resultSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("3: see results");
    var extractResultHeaders = resultSheet.getRange("A1:U1").getValues();
    var result_headers = [];
    for (var i = 0; i < extractResultHeaders[0].length; i++) {
      var value = extractResultHeaders[0][i];
      if (value) {
        result_headers.push(value);
      }
    }
  
    // retrieve and process history page column headers
    var historySheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("4: track history");
    var extractHistoryHeaders = historySheet.getRange("A1:BA1").getValues();
    var history_headers = [];
    for (var i = 0; i < extractHistoryHeaders[0].length; i++) {
      var value = extractHistoryHeaders[0][i];
      if (value) {
        history_headers.push(value);
      }
    }
  
    // create json payload with extracted elements
    var options = {
      'method' : 'post',
      'contentType': 'application/json',
      // Convert the JavaScript object to a JSON string.
      'payload' : JSON.stringify({
        user_variables: user_variables,
        result_headers: result_headers,
        history_headers: history_headers
        })
    };
    
    // Make a POST request with a JSON payload.
    var response = UrlFetchApp.fetch('https://us-central1-rsi-wsb-tool.cloudfunctions.net/rsi-wsb-scanner-gcloud', options);
  
    var responseData = JSON.parse(response.getContentText());
  
   // Function to append data to sheet
    function appendDataToSheet(sheet, data) {
      if (data && data.length > 0) {
        var headers = Object.keys(data[0]);
        var values = data.map(row => headers.map(header => row[header]));
        
        sheet.getRange(sheet.getLastRow() + 1, 1, values.length, headers.length).setValues(values);
      }
    }
    
    // Append gSheetsResultsDF to "03: see results" sheet
    if (responseData.gSheetsResultsDF) {
      appendDataToSheet(resultSheet, responseData.gSheetsResultsDF);
    }
    
    // Append gSheetsHistoryDF to "04: track history" sheet
    if (responseData.gSheetsHistoryDF) {
      appendDataToSheet(historySheet, responseData.gSheetsHistoryDF);
    }
    
    Logger.log("Data appended successfully");
  }
  