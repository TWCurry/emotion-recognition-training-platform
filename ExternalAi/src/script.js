var apiUrl = "http://35.190.172.118:5000"
// Run on page load
$( document ).ready(function() {
    console.log("DOM Loaded.");
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
            document.getElementById('output').innerHTML = '<img src="' + data + '" width="70px" height="50px" />';
            params = {"imageData": data};
            $.post(apiUrl+"/uploadImage", params, function(resp) {
                console.log(resp);
            })
        });
      } catch (error) {
          console.log("Error:"+error);
      }
}