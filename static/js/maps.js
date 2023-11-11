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
        .setHTML(this.getPopupHTML(feature))

      const pin = document.createElement("span")
      const { symbol, color } = feature.properties
      pin.className = `icon--filled icon--${color}`
      pin.textContent = symbol

      new mapboxgl.Marker({ element: pin })
        .setLngLat(feature.geometry.coordinates)
        .setPopup(popup)
        .addTo(this.map)
    })
  }

  getPopupHTML(feature) {
    const props = feature.properties
    const empty = "N/A"

    const TEMPLATE = [
      { label: "Object ID", key: "object_id" },
      { label: "Stage", key: "stage" },
      { label: "Address", key: "geocoded_address" },
      { label: "Special Case", key: "special_case" },
      { label: "Hazard Size", key: "hazard_size" },
      { label: "Tech", key: "tech" },
    ]

    const body = TEMPLATE.map(item => {
      return `
        <tr>
          <td>${item.label}</td>
          <td>${props[item.key] || empty}</td>
        </tr>
      `
    }).join("\n")

    return `
      <table>
        <tbody>
          ${body}
        </tbody>
      </table>
    `
  }
}
