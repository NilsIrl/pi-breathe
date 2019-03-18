var form = document.getElementById("form");
form.addEventListener("submit", function (e) {
    e.preventDefault();
    var origin = document.getElementById("origin").value;
    var destination = document.getElementById("destination").value;

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var request = JSON.parse(xhttp.responseText);
            center_lat = (request['bounds']['northeast']['lat'] + request['bounds']['southwest']['lat']) / 2;
            center_lng = (request['bounds']['northeast']['lng'] + request['bounds']['southwest']['lng']) / 2;
            map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: center_lat, lng: center_lng},
                zoom: 15,
            });
            var path = new google.maps.Polyline({
                path: google.maps.geometry.encoding.decodePath(request['overview_polyline']['points']),
                geodesic: true,
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2
            });
            path.setMap(map);
            var list = document.getElementById("instructions");
            while (list.lastChild) {
                list.removeChild(list.lastChild);
            }
            console.log(request);
            for (step in request['legs'][0]['steps']) {
                var li = document.createElement("li");
                li.innerHTML = request['legs'][0]['steps'][step]['html_instructions'];
                list.appendChild(li);
            }
        }
    };
    xhttp.open("GET", "http://localhost:5000/direction?src=debug_with_seb&rank_preference=distance&origin=" + origin + "&destination=" + destination, true);
    xhttp.send();
});
