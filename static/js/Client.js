var el = x => document.getElementById(x);

function showPicker() {
    // Emulates input type='file' behavior
    el("file-input").click();
}

function showPicked(input) {
    el("upload-label").innerHTML = input.files[0].name;
    var reader = new FileReader();
    reader.onload = function(e) {
        el("image-picked").src = e.target.result;
        el("image-picked").className = "";
    };
    reader.readAsDataURL(input.files[0]);
}

function analyze() {
    var uploadFiles = el("file-input").files;
    if (uploadFiles.length !== 1) alert("Please select a file to analyze!");

    el("analyze-button").innerHTML = "Predicting...";
    var xhr = new XMLHttpRequest();
    // Gets currently hosted address
    var loc = window.location;
    // Opens a post request
    // forms link like eg. http://localhost:8080/predict
    xhr.open("POST", `${loc.protocol}//${loc.hostname}:${loc.port}/predict`,
            true);
    // Alert on request error
    xhr.onerror = function() {
        alert(xhr.responseText);
    };
    // on success
    xhr.onload = function(e) {
        if (this.readyState === 4) {
          var response = JSON.parse(e.target.responseText);
          el("result-label").innerHTML = `Result = ${response["result"]}`;
        }
        el("analyze-button").innerHTML = "Predict";
    };

    // send image file data to server
    var fileData = new FormData();
    fileData.append("file", uploadFiles[0]);
    xhr.send(fileData);
}