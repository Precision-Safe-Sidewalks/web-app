mapboxgl.accessToken = "pk.eyJ1IjoiYWN1cmxleTMxIiwiYSI6ImNsMDVqYmRzYTFuM2UzaXFnMThuMnE5NHMifQ.DaCM5UwTwkuLo02YUKQpFA"

const MAPBOX_CONFIG = {
  style: "mapbox://styles/mapbox/streets-v12",
  //style: "mapbox://styles/acurley31/clqoa2mem00ic01p5dnemgq8q",
  center: [0, 0],
  zoom: 12,
}

class MeasurementsMap {
  constructor(containerId, projectId, center = null) {
    this.projectId = projectId;
    this.features = [];
    this.markers = [];
    this.filters = {};
    this.zoom = null;

    this.map = new mapboxgl.Map({ 
      ...MAPBOX_CONFIG, 
      container: containerId,
      center: center ? center : MAPBOX_CONFIG.center,
    })

    //this.map.on("zoom", (event) => this.onZoom(event))

    this.map.on("load", async () => {
      await this.fetchIcons()
      const data = await this.fetchFeatures()
    
      this.map.addSource(
        "measurements", 
        {
          type: "geojson", 
          data: data,
          tolerance: 0,
        },
      )

      this.map.addLayer({
        id: "measurements-markers",
        type: "symbol",
        source: "measurements",
        layout: {
          "icon-image": ["get", "symbol"],
          "icon-allow-overlap": true,
          "icon-size": ['interpolate', ['linear'], ['zoom'], 15, 0.5, 20, 2]
        },
        paint: {
          "icon-color": ["get", "color"],
          "icon-halo-color": ["get", "color"],
          "icon-halo-width": 2,
        },
      })

      this.resetBounds()
    })
  }

  async fetchIcons() {
    const resp = await fetch("/api/symbology/icons/")
    const data = await resp.json()

    data.forEach(({ name, url }) => {
      this.map.loadImage(url, (error, image) => {
        if (error) throw error;
        this.map.addImage(name, image, { sdf: true })
      })
    })
  }

  async fetchFeatures() {
    let url = `/api/measurements/?project=${this.projectId}`
    let data = {type: "FeatureCollection", features: []}

    while (url !== null) {
      const resp = await fetch(url)

      if (!resp.ok) {
        throw new Error(`Error fetching measurements for project ${this.projectId}`)
      }

      const { results, next } = await resp.json()
      data.features = data.features.concat(results.features)

      if (next !== null) {
        const origin = (new URL(next)).origin
        url = next.replace(origin, "")
      } else {
        url = null
      }
    }

    this.features = data.features

    return data
  }

  setStyle(style) {
    this.map.setStyle(style)
  }

  fitBounds(bbox) {
    this.map.fitBounds(bbox)
  }

  resetBounds() {
    if (this.markers.length === 0) {
      return
    }

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

  onZoom(event) {
    const zoom = Math.round(this.map.getZoom())

    if (zoom !== this.zoom) {
      this.zoom = zoom;

      this.markers.forEach(marker => {
        const element = marker.getElement()
        
        Array.from(element.classList)
          .filter(className => className.startsWith("zoom-"))
          .forEach(className => element.classList.remove(className))
      
        element.classList.add(`zoom-${zoom}`)
      })
    }
  }
}
