var apiUrl = "http://35.190.172.118"
// Run on page load
$( document ).ready(function() {
    console.log("DOM Loaded.");
    $("#gridContainer").html(createContainerContents());
    downloadImages();
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
            })
        });
    } catch (error) {
          console.log("Error:"+error);
    }
}

function createContainerContents() {
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

function downloadImages() {
    $.get(apiUrl+":5002/fetchImages", function(resp) {
        console.log(resp);
    })
}