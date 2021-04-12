var map = L.map('map', {
    center: [42.39, -72.52],
    zoom: 14
});

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    minZoom: '0'
}).addTo(map);

// If we can jsonify coordinates and update existing map:
polyline_route = L.polyline([[42.37589,-72.51338],[42.37561,-72.51978],[42.38006,-72.52015]]).addTo(map);
//polyline_route.remove()