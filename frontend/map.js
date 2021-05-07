// Create the map (defaulted to Amherst) and provide mandatory OSM attribution

const map = L.map('map', {
  center: [42.39, -72.52],
  zoom: 14
})

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  minZoom: '0'
}).addTo(map)

// functions to pan the map to a specified location

async function sendSearchRequest() {
  const resp = await fetch('/search', {
    method: 'POST',
    body: new FormData(document.getElementById('search-form'))
  })
  updateMapSearch(await resp.json())
}

const searchSubmit = document.getElementById('search-submit')

function updateMapSearch({ coords }) {
  if (coords.length) {
    // Pan to the requested place
    map.panTo(new L.LatLng(coords[0], coords[1]))
  } else {
    alert('Place not found')
  }
}

// Event listener to submit the route request

searchSubmit.addEventListener('click', sendSearchRequest)

// The sendRouteRequest and updateMapRoute functions manage the communication to the backend

let newRouteLine, shortRouteLine

async function sendRouteRequest() {
  const resp = await fetch('/api', {
    method: 'POST',
    body: new FormData(document.getElementById('form'))
  })
  updateMapRoute(await resp.json())
}

const submit = document.getElementById('submit')
const throbber = document.getElementById('throbber')
const statsBox = document.getElementById('stats')

function updateMapRoute({ error, stats, route, short_route: shortRoute }) {
  if (error === 'timeout') {
    alert('Timed out while looking for path')
  } else if (error === 'badcoords') {
    alert('Please select both an origin and a destination')
  } else if (!route.length) {
    alert('No path found')
  } else {
    // Pan to the center of the origin and destination
    map.panTo(new L.LatLng(
      (route[route.length-1][0] + route[0][0]) / 2, 
      (route[route.length-1][1] + route[0][1]) / 2
    ))
    shortRouteLine = L.polyline(shortRoute)
    shortRouteLine.setStyle({color:'blue'})
    shortRouteLine.addTo(map)
    newRouteLine = L.polyline(route)
    newRouteLine.setStyle({color:'red'})
    newRouteLine.addTo(map)
    // Print stats
    const prettyStats = [
      `Shortest path length: ${stats[0]}m`,
      `Shortest path elevation gain: ${stats[1]}m`
    ]
    if (stats[2] !== -1 || stats[3] !== -1) {
      prettyStats.push(
        `New path length: ${stats[2]}m`,
        `New path elevation gain: ${stats[3]}m`
      )
    }
    statsBox.textContent = prettyStats.join('\n')
    statsBox.style.visibility = 'visible'
  }
  submit.disabled = false
  throbber.style.visibility = 'hidden'
}

// Event listener to submit the route request

submit.addEventListener('click', () => {
  // Immediately erase existing route and show spinner
  newRouteLine?.remove()
  shortRouteLine?.remove()
  submit.disabled = true
  statsBox.style.visibility = 'hidden'
  throbber.style.visibility = 'visible'
  sendRouteRequest()
})

// The following functions use mouse clicks to get coordinates
// They also place a marker at the origin and destination
// Note that the markers can be heavily customized

let originMarker = new L.marker()
const originInput = document.getElementById('origin')

let destinationMarker = new L.marker()
const destinationInput = document.getElementById('destination')

map.on('click', e => {
  originInput.value = e.latlng.toString().slice(6)
  originMarker.remove()
  originMarker = L.marker(e.latlng).addTo(map)
})

map.on('contextmenu', e => {
  destinationInput.value = e.latlng.toString().slice(6)
  destinationMarker.remove()
  destinationMarker = L.marker(e.latlng).addTo(map)
})
