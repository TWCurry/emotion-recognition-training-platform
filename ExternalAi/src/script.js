var apiUrl = "http://35.190.172.118:5000"
// Run on page load
$( document ).ready(function() {
    console.log("DOM Loaded.");
    Webcam.set({
        width: 220,
        height: 190,
        image_format: 'jpeg',
        jpeg_quality: 100
    });
    Webcam.attach('#camera');
    
    takeSnapShot = function () {
        Webcam.snap(function (data) {
            document.getElementById('output').innerHTML = '<img src="' + data + '" width="70px" height="50px" />';
            params = {"imageData": data};
            console.log(apiUrl+"/uploadImage")
            $.post(apiUrl+"/uploadImage", params, function(resp) {
                console.log(resp);
            })
        });
    }
});