// Create the map (defaulted to Amherst) and provide mandatory OSM attribution

var map = L.map('map', {
  center: [42.39, -72.52],
  zoom: 14
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  minZoom: '0'
}).addTo(map);

// The send_request and update_map functions manage the communication to the backend
// The names are self-explanatory
// It also instantiates dummy polyline so it can be replaced later

var polyline_route = L.polyline([0,0][0,0]);

function send_request() {
  console.log('Sending route request...');
  // Immediately erase existing route - add throbber?
  polyline_route.remove();
  let request = new XMLHttpRequest();
  // Set the callback function once the route is loaded
  request.onreadystatechange = function() {
    if(request.readyState === 4) {
      console.log('Route recieved.');
      update_map(request.response);
    }
  }
  // Open and send the request
  request.open('POST', '/api');
  request.send(new FormData(document.querySelector('#form')));
}

const submit = document.querySelector('#submit');
const throbber = document.querySelector('#throbber');

function update_map(response) {
  let obj = JSON.parse(response);
  if(obj.route.length === 0) {
    alert('No path found');
    console.log('No path found');
  } else {
    console.log('Painting route...');
    // Pan to the center of the origin and destination
    map.panTo(new L.LatLng((obj.route[obj.route.length-1][0] + obj.route[0][0]) / 2, 
                          (obj.route[obj.route.length-1][1] + obj.route[0][1]) / 2));
    polyline_route = L.polyline(obj.route, color='#ff0000');
    polyline_route.setStyle({color:'red'});
    polyline_route.addTo(map);
    console.log('Done.');
  }
  submit.disabled = false;
  throbber.style.visibility = 'hidden';
}

// Event listener to submit the route request

submit.addEventListener('click', function() {
  send_request();
  submit.disabled = true;
  throbber.style.visibility = 'visible';
})

// The following functions use mouse clicks to get coordinates
// They also place a marker at the origin and destination
// Note that the markers can be heavily customized

var origin_marker = new L.marker();
var origin_input = document.querySelector('#origin');

var destination_marker = new L.marker();
var destination_input = document.querySelector('#destination');

map.on('click', function(e){
  //console.log('Origin: (' + e.latlng.lat + ', ' + e.latlng.lng + ')');
  origin_input.value = e.latlng.toString().substring(6);
  origin_marker.remove();
  origin_marker = L.marker(e.latlng).addTo(map);
});

map.on('contextmenu', function(e){
  //console.log('Destination: (' + e.latlng.lat + ', ' + e.latlng.lng + ')');
  destination_input.value = e.latlng.toString().substring(6);
  destination_marker.remove();
  destination_marker = L.marker(e.latlng).addTo(map);
});