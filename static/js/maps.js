mapboxgl.accessToken = "pk.eyJ1IjoiYWN1cmxleTMxIiwiYSI6ImNsMDVqYmRzYTFuM2UzaXFnMThuMnE5NHMifQ.DaCM5UwTwkuLo02YUKQpFA"

const DEFAULT_STYLE = "mapbox://styles/mapbox/streets-v12"
const DEFAULT_ZOOM = 12

const SOURCE = "measurements"
const LAYER = "measurements"
const LAYER_LABELS = `${LAYER}-labels`

class MeasurementsMap {
  constructor(container, projectId, center) {
    this.projectId = projectId
    this.mapConfig = { center, container, zoom: DEFAULT_ZOOM }
    this.mapData = null
    this.mapLabels = "none"
    this.mapFilter = null
    this.map = null

    this.buildMap(DEFAULT_STYLE)
  }

  async buildMap(style) {
    if (this.map) {
      this.mapConfig.center = this.map.getCenter()
      this.mapConfig.zoom = this.map.getZoom()
      this.mapConfig.container = this.map.getContainer()
      this.mapLabels = this.map.getLayoutProperty(LAYER_LABELS, "visibility")
      this.mapFilter = this.map.getFilter(LAYER)
      this.map.remove()
    }

    this.map = new mapboxgl.Map({ style, ...this.mapConfig })

    this.map.on("load", () => this.onMapLoad())
    this.map.on("click", LAYER, (e) => this.onMapClick(e))
    this.map.on("mouseenter", LAYER, () => this.onMouseEnter())
    this.map.on("mouseleave", LAYER, () => this.onMouseLeave())
  }

  // Handler for processing the map after it loads. This adds the source
  // and symbol layers.
  async onMapLoad() {
    await this.fetchSymbols()
    let bounds = this.map.getBounds()

    if (!this.mapData) {
      this.mapData = await this.fetchFeatures()
      bounds = this.mapData.bbox
    }
    
    await this.map.addSource(SOURCE, {
      type: "geojson",
      data: this.mapData,
    })
   
    await this.map.addLayer({
      id: LAYER,
      source: SOURCE,
      type: "symbol",
      layout: {
        "icon-image": ["get", "symbol"],
        "icon-allow-overlap": true,
        "icon-size": ["interpolate", ["exponential", 2], ["zoom"], 15, 0.15, 22, 8],
        "icon-anchor": "bottom",
      },
      paint: {
        "icon-color": ["get", "color"],
      },
    })

    await this.map.addLayer({
      id: LAYER_LABELS,
      source: SOURCE,
      type: "symbol",
      layout: {
        "text-field": ["get", "object_id"],
        "text-anchor": "top",
        "text-allow-overlap": false,
        "text-size": 10,
        "visibility": this.mapLabels,
      },
    })

    await this.map.setFilter(LAYER, this.mapFilter)
    await this.map.setFilter(LAYER_LABELS, this.mapFilter)

    this.map.fitBounds(bounds)
  }

  // Handler for clicking a layer on the map to display a popup
  async onMapClick(e) {
    const feature = e.features[0]
    const coordinates = feature.geometry.coordinates.slice()
    const html = this.getPopupHTML(feature)
  
    new mapboxgl.Popup()
      .setLngLat(coordinates)
      .setHTML(html)
      .addTo(this.map)
  }

  // Handler for toggling the cursor when the mouse enters the layer
  async onMouseEnter() {
    this.map.getCanvas().style.cursor = "pointer"
  }

  // Handler for toggling the cursor when the mouse leaves the layer
  async onMouseLeave() {
    this.map.getCanvas().style.cursor = ""
  }

  // Handler for applying filters to the layer
  async addFilter(property, value) {
    const layer = this.map.getLayer(LAYER)

    if (!layer) {
      return
    }
    
    const currentFilter = this.map.getFilter(LAYER)
    const nextFilter = ["!=", ["get", property], value]

    if (currentFilter === undefined) {
      this.map.setFilter(LAYER, ["all", nextFilter])
      this.map.setFilter(LAYER_LABELS, ["all", nextFilter])
    } else {
      this.map.setFilter(LAYER, [...currentFilter, nextFilter])
      this.map.setFilter(LAYER_LABELS, [...currentFilter, nextFilter])
    }
  }

  // Handler fo removing filters from the layer
  async removeFilter(property, value) {
    const currentFilter = this.map.getFilter(LAYER)
    const layer = this.map.getLayer(LAYER)

    if (currentFilter === undefined || layer === undefined) {
      return
    }

    const nextFilter = currentFilter
      .slice(1, -1)
      .filter(f => (!(f[1][1] === property && f[2] === value)))

    if (nextFilter.length === 0) {
      this.map.setFilter(LAYER, null)
      this.map.setFilter(LAYER_LABELS, null)
    } else {
      this.map.setFilter(LAYER, ["all", ...nextFilter])
      this.map.setFilter(LAYER_LABELS, ["all", ...nextFilter])
    }
  }

  // Handler to toggle the visbility for the labels
  async toggleLabels() {
    const layer = this.map.getLayer(LAYER_LABELS)
  
    if (!!layer) {
      this.map.getLayoutProperty(LAYER_LABELS, "visibility") === "visible"
        ? this.map.setLayoutProperty(LAYER_LABELS, "visibility", "none")
        : this.map.setLayoutProperty(LAYER_LABELS, "visibility", "visible")
    }
  }

  // Handler to reset the bounds to the buffered bounding box
  // of all the visible features on the map
  async fitToView() {
    const filter = this.map.getFilter(LAYER)
    const features = this.map.querySourceFeatures(SOURCE, filter)
    const bbox = this.calculateBounds(features)
    this.map.fitBounds(bbox)
  }

  // Fetch the symbols required for rendering the map. These are loaded
  // directly into the map on each build.
  async fetchSymbols() {
    const resp = await fetch("/api/symbology/icons/")
    const data = await resp.json()

    data.forEach(({name, url}) => {
      this.map.loadImage(url, (error, image) => {
        if (error) throw error
        this.map.addImage(name, image, { sdf: true })
      })
    })
  }

  // Fetch the GeoJSON Feature Collection containing all of the
  // features for the current project
  async fetchFeatures() {
    let page = 1
    let features = []

    while (page !== null) {
      const url = `/api/measurements/?project=${this.projectId}&page=${page}`
      const resp = await fetch(url)

      if (!resp.ok) {
        throw new Error(`Error fetching project ${this.projectId} data`)
      }

      const { results, next } = await resp.json()
      features = [...features, ...results.features]
      page = !!next ? page + 1 : null
    }

    const bbox = this.calculateBounds(features)

    return {type: "FeatureCollection", bbox, features} 
  }

  // Calculate the buffered bounding box from a set of GeoJSON
  // features. The buffer is a fraction of the minimum bounds.
  calculateBounds(features) {
    if (!features) {
      return [0, 0, 0, 0]
    }

    const [minX, minY, maxX, maxY] = features.reduce((bbox, feature) => (
      [
        Math.min(bbox[0], feature.geometry.coordinates[0]),
        Math.min(bbox[1], feature.geometry.coordinates[1]),
        Math.max(bbox[2], feature.geometry.coordinates[0]),
        Math.max(bbox[3], feature.geometry.coordinates[1]),
      ]
    ), [Infinity, Infinity, -Infinity, -Infinity])

    const buffer = 0.1
    const dx = (maxX - minX) * buffer
    const dy = (maxY - minY) * buffer

    return [minX - dx, minY - dy, maxX + dx, maxY + dy]
  }

  // Return the HTML template for the feature to render inside the
  // popup menu
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
