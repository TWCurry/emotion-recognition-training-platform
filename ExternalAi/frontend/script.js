var apiUrl = "http://35.190.172.118";
var imageNames = [];
// Run on page load
$( document ).ready(function() {
    $("#loader").hide();
    console.log("DOM Loaded.");
    $("#gridContainer").html(createPlaceholderContainerContents());
    downloadNewImages();
    // Create webcam object
    Webcam.set({
        width: 220,
        height: 190,
        image_format: 'jpeg',
        jpeg_quality: 100
    });
    Webcam.attach('#camera');

    // Detect whether the user has given permission (asks again, but unlikely the user will deny the second time)
    navigator.getMedia = ( navigator.getUserMedia ||
        navigator.webkitGetUserMedia ||
        navigator.mozGetUserMedia ||
        navigator.msGetUserMedia);

    navigator.getMedia({video: true}, function() {
        // // Take first image
        // takeSnapShot()
        // // Trigger function every 5 seconds
        // setInterval(takeSnapShot, 5000)
    }, function() {
        console.log("Webcam not available.");
    });
    
});

function takeSnapShot() {
    console.log("Sending image...")
    try {
        Webcam.snap(function (data) {
            params = {"imageData": data};
            $.post(apiUrl+":5000/uploadImage", params, function(resp) {
                console.log(resp);
            });
        });
    } catch (error) {
        console.log("Error:"+error);
    }
}

function createPlaceholderContainerContents() {
    returnHtml = "<table><tr>";
    for (i=0;i<2;i++) {
        returnHtml += "<td class='imgContainer'><img id='loader' src='img/spinner.gif' height='180px' width='180px'></td>";
    }
    returnHtml += "</table>";
    return returnHtml;
}

function downloadNewImages() {
    returnHtml = "<table><tr>";
    $.get("http://localhost:5000/fetchImages", function(resp) {
        downloadedData = resp.body;
        imageData = [];
        Object.keys(downloadedData).forEach(function(key) {
            Object.keys(downloadedData[key]).forEach(function(imgName) {
                imageNames.push(imgName);
                imgObj = downloadedData[key][imgName];
                rawData = imgObj.substring(2, imgObj.length - 1);
                imageData.push(rawData);
            });
        });
        index = 0;
        for (i=0;i<2;i++) {
            returnHtml += "<td class='imgContainer' id='container"+index+"'><img class='legoImage' src=\"data:image/png;base64, "+imageData[index]+"\"></td>";
            index += 1
        }
        returnHtml += "</table>";
        $("#gridContainer").html(returnHtml);
    });
}

function submit() {
    $("#loader").fadeIn();
    // Reset borders
    for (i=0;i<9;i++) {
        $("#container"+i).css("border", "5px solid transparent");
    }
    params = {"imageNames": JSON.stringify(imageNames), "typeToIdentify": $("#sltItems").val()};
    $.post("http://localhost:5000/identifyBrickType", params, function(resp) {
        resp.body.forEach(function(index) {
            $("#container"+index).css("border", "5px solid rgb(51, 255, 0)");
        });
        $("#loader").fadeOut();
        takeDelayedPhoto(1000);
    });
}

// Async function to take a photo after a specified number of miliseconds
async function takeDelayedPhoto(ms) {
    await(sleep(ms));
    takeSnapShot();
}

// Function to sleep (time in milliseconds)
function sleep(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}