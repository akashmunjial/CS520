var map = L.map('map', {
  center: [42.39, -72.52],
  zoom: 14
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  minZoom: '0'
}).addTo(map);

// Dummy polyline
var polyline_route = L.polyline([0,0][0,0]);
const submit = document.querySelector('#submit');

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

function update_map(response) {
  let obj = JSON.parse(response);
  console.log('Painting route...');
  // Currently pans to the starting point, for simplicity
  map.panTo(new L.LatLng(obj.route[0][0], obj.route[0][1]));
  polyline_route = L.polyline(obj.route).addTo(map);
  console.log('Done.');
}

submit.addEventListener('click', function() {
  send_request();
})