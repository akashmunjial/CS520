// Initialize the map and assign it to a variable for later use
// there's a few ways to declare a VARIABLE in javascript.
// you might also see people declaring variables using `const` and `let`
var map = L.map('map', {
    // Set latitude and longitude of the map center (required)
    center: [42.39, -72.52],
    // Set the initial zoom level, values 0-18, where 0 is most zoomed-out (required)
    zoom: 14
});
 
// Create a Tile Layer and add it to the map
var tiles = new L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  minZoom: '0'}).addTo(map);