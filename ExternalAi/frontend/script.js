var apiUrl = "http://35.190.172.118"
// Run on page load
$( document ).ready(function() {
    console.log("DOM Loaded.");
    $("#gridContainer").html(createPlaceholderContainerContents());
    downloadNewImages();
    // Create webcam object
    Webcam.set({
        width: 60,
        height: 45,
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
        // Take first image
        takeSnapShot()
        // Trigger function every 5 seconds
        setInterval(takeSnapShot, 5000)
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
    for (y=0;y<3;y++) {
        for (x=0;x<3;x++) {
            returnHtml += "<td class='imgContainer'>Loading...</td>";
        } 
        returnHtml += "</tr>";
    }
    returnHtml += "</table>";
    return returnHtml;
}

function downloadNewImages() {
    returnHtml = "<table><tr>";
    $.get(apiUrl+":5002/fetchImages", function(resp) {
        downloadedData = resp.body;
        imageData = [];
        Object.keys(downloadedData).forEach(function(key) {
            imgObj = downloadedData[key];
            rawData = imgObj.substring(2, imgObj.length - 1);
            imageData.push(rawData);
            // $("#test").html("<img src=\"data:image/png;base64, "+rawData+"\">");
        });
        index = 0;
        for (y=0;y<3;y++) {
            for (x=0;x<3;x++) {
                returnHtml += "<td class='imgContainer'><img class='legoImage' src=\"data:image/png;base64, "+imageData[index]+"\"></td>";
                index += 1
            } 
            returnHtml += "</tr>";
        }
        returnHtml += "</table>";
        $("#gridContainer").html(returnHtml);
    });
}