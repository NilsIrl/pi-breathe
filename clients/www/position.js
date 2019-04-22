
document.getElementById("form").addEventListener('submit', function(e) {
    e.preventDefault();
    if (document.getElementById("submit").value == "Stop sending location data") {
        document.getElementById("submit").value = "Start sending location data";
        navigator.geolocation.clearWatch(watchID);
    } else {
        document.getElementById("submit").value = "Stop sending location data";
        var watchID = navigator.geolocation.watchPosition(function(position) {
            var data = new FormData();
            data.append("src", document.getElementById("id").value)
            data.append("lng", position.coords.longitude)
            data.append("lat", position.coords.latitude)
            data.append("time", position.timestamp)
            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", "http://localhost:5000/location", true);
            xhttp.onreadystatechange = function() {
                if (xhttp.readyState == XMLHttpRequest.DONE && xhttp.status == 200) {
                    document.getElementById("status").innerText = "Sent data at " + new Date();
                }
            };
            xhttp.send(data);
        });
    }
});
