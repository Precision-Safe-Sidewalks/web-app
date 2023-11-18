mapboxgl.accessToken = "pk.eyJ1IjoiYWN1cmxleTMxIiwiYSI6ImNsMDVqYmRzYTFuM2UzaXFnMThuMnE5NHMifQ.DaCM5UwTwkuLo02YUKQpFA"

const MAPBOX_CONFIG = {
  style: "mapbox://styles/mapbox/streets-v12",
  center: [-74.5, 40],
  zoom: 12,
}

class MeasurementsMap {
  constructor(containerId, projectId, centroid) {
    this.projectId = projectId;
    this.features = [];
    this.markers = [];
    this.filters = {};

    this.map = new mapboxgl.Map({ 
      ...MAPBOX_CONFIG, 
      container: containerId,
      center: centroid,
    })
  }

  setStyle(style) {
    this.map.setStyle(style)
  }

  fitBounds(bbox) {
    this.map.fitBounds(bbox)
  }

  resetBounds() {
    const buffer = 0.1
    let bbox = [Infinity, Infinity, -Infinity, -Infinity]
    
    this.markers.forEach(marker => {
      const { lng, lat } = marker.getLngLat()
      bbox[0] = Math.min(bbox[0], lng)
      bbox[1] = Math.min(bbox[1], lat)
      bbox[2] = Math.max(bbox[2], lng)
      bbox[3] = Math.max(bbox[3], lat)
    })

    const dx = (bbox[2] - bbox[0]) * buffer
    const dy = (bbox[3] - bbox[1]) * buffer
    bbox[0] -= dx
    bbox[1] -= dy
    bbox[2] += dx
    bbox[3] += dy

    this.map.fitBounds(bbox)
  }

  addFilter(property, value, render = true) {
    if (!this.filters.hasOwnProperty(property)) {
      this.filters[property] = new Set()
    }

    this.filters[property].add(value)

    if (render) {
      this.render()
    }
  }

  removeFilter(property, value, render = true) {
    if (this.filters.hasOwnProperty(property)) {
      this.filters[property].delete(value)
    }

    if (render) {
      this.render()
    }
  }

  addFeatures(features, label) {
    this.features = this.features.concat(features)
    this.render()
  }

  render() {
    this.markers.forEach(marker => marker.remove())
    this.markers = []

    this.getVisibleFeatures().map(feature => {
      const popup = new mapboxgl.Popup({ offset: 24 })
        .setHTML(this.getPopupHTML(feature))

      const pin = document.createElement("span")
      const { symbol, color } = feature.properties
      pin.className = `icon--filled icon--${color}`
      pin.textContent = symbol

      const marker = new mapboxgl.Marker({ element: pin })
        .setLngLat(feature.geometry.coordinates)
        .setPopup(popup)
        .addTo(this.map)

      this.markers.push(marker)
    })
  }

  getVisibleFeatures() {
    return this.features.filter(feature => {
      for (const property of Object.keys(this.filters)) {
        const featureValue = feature.properties[property]
        const filterValues = this.filters[property]

        if (featureValue && !filterValues.has(featureValue)) {
          return false
        }
      }

      return true
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
