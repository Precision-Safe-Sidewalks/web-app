mapboxgl.accessToken = "pk.eyJ1IjoiYWN1cmxleTMxIiwiYSI6ImNsMDVqYmRzYTFuM2UzaXFnMThuMnE5NHMifQ.DaCM5UwTwkuLo02YUKQpFA"

const MAPBOX_CONFIG = {
  style: "mapbox://styles/mapbox/streets-v12",
  center: [-74.5, 40],
  zoom: 12,
}

class MeasurementsMap {
  constructor(containerId, projectId, centroid) {
    this.projectId = projectId;
    this.map = new mapboxgl.Map({ 
      ...MAPBOX_CONFIG, 
      container: containerId,
      center: centroid,
    })
  }

  fitBounds(bbox) {
    this.map.fitBounds(bbox)
  }

  addFeatures(features, label) {
    features.map(feature => {
      const popup = new mapboxgl.Popup({ offset: 24 })
        .setHTML(`<h5>${feature.id}</h5>`)

      const pin = document.createElement("span")
      pin.className = "icon--filled"
      pin.textContent = "location_on"

      new mapboxgl.Marker({ element: pin })
        .setLngLat(feature.geometry.coordinates)
        .setPopup(popup)
        .addTo(this.map)
    })
  }
}
