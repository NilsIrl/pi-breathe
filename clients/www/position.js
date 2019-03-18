
document.getElementById("form").addEventListener('submit', function(e) {
    e.preventDefault();
    var watchID = navigator.geolocation.watchPosition(function(position) {
        var data = new FormData();
        data.append("src", document.getElementById("id").value)
        data.append("lng", position.coords.longitude)
        data.append("lat", position.coords.latitude)
        data.append("time", position.timestamp)
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "http://localhost/location", true);
        xhttp.onreadystatechange = function() {
            if (xhttp.readySate == XMLHttpRequest.DONE && xhttp.status == 200) {
                document.getElementById("status").value = "Sent data at " + new Date();
            }
        };
        xhttp.send(data);
    });
});
