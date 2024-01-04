class DataTable {
  constructor(rootId, options) {
    this.root = document.getElementById(rootId)
    this.options = options
    this.currentPage = 1
    this.lastPage = 1
    this.query = null
    this.filters = {}
    this.openFilter = null

    this.initialize()
    this.render()
  }

  // Initialize the DOM elements defining the table
  initialize() {
    const actions = $(`<div class="table-actions"></div>`)
    const filters = $(`<div class="table-filters"></div>`)
    const table = $(`<table class="table"></table>`)
    const thead = $(`<thead></thead>`)
    const tbody = $(`<tbody></tbody>`)

    const tr = $(`<tr></tr>`)
    this.options.columns?.forEach(c => $(tr).append($(`<th>${c}</th>`)))

    $(thead).append(tr)
    $(table).append(thead)
    $(table).append(tbody)

    $(this.root).append(filters)
    $(this.root).append(actions)
    $(this.root).append(table)

    $(window).click(this.onClickAway)
  }

  // Render the data tbale
  async render() {
    const data = await this.fetchData()
    this.renderData(data)
    this.renderActions(data)
    this.renderFilters(data)
  }

  // Render the table data
  async renderData(data) {
    const tbody = $(this.root).find("tbody").first()
    tbody.empty()

    if (data.count === 0) {
      $(tbody).append(`<tr><td align="center" colspan="100%">No available data</td></tr>`)
      return
    }

    data.results?.forEach(row => {
      const tr = $("<tr></tr>")
      Object.values(row).forEach(value => {
        $(tr).append(`<td>${value === null ? '---' : value}</td>`)
      })
      $(tbody).append(tr)
    })
  }

  renderActions(data) {
    const actions = $(this.root).find(`div[class="table-actions"]`)
    
    this.renderSearch(actions, data)
    this.renderPagination(actions, data)
  }

  // Render the search bar
  renderSearch(actions, data) {
    const element = $(this.root).find("#id-search").first()

    if ($(element).length === 0) {
      const search = $(`<input id="id-search" type="text" placeholder="Search...">`)
      $(search).on("keyup", (event) => this.onSearch(event.target.value))
      
      const container = $(`<div class="search-bar"></div>`)
      $(container).append(`<span class="icon">search</span>`)
      $(container).append(search)
      $(actions).prepend(container)
    }
  }

  // Render the table pagination
  renderPagination(actions, data) { 
    this.lastPage = Math.ceil(data.count / this.options.perPage)
    
    let pagination = $(actions).find(`div[class="table-pagination"]`)
    $(pagination).find("button").off("click")
    $(pagination).remove()
    pagination = $(`<div class="table-pagination"></div>`)

    const start = this.options.perPage * (this.currentPage - 1) + 1
    const end = Math.min(data.count, this.options.perPage * this.currentPage)
    $(pagination).append(`<span class="mr-2">Showing ${start} - ${end} of ${data.count}</span>`)

    const firstButton = $(`<button class="btn--icon"><span class="icon">first_page</span></button>`)
    $(firstButton).prop("disabled", this.currentPage === 1)
    $(firstButton).on("click", () => this.onFirstPage())
    $(pagination).append(firstButton)
    
    const prevButton = $(`<button class="btn--icon"><span class="icon">chevron_left</span></button>`)
    $(prevButton).prop("disabled", !data.previous)
    $(prevButton).on("click", () => this.onPrevPage())
    $(pagination).append(prevButton)

    const nextButton = $(`<button class="btn--icon"><span class="icon">chevron_right</span></button>`)
    $(nextButton).prop("disabled", !data.next)
    $(nextButton).on("click", () => this.onNextPage())
    $(pagination).append(nextButton)
    
    const lastButton = $(`<button class="btn--icon"><span class="icon">last_page</span></button>`)
    $(lastButton).prop("disabled", data.count <= this.options.perPage * this.currentPage)
    $(lastButton).on("click", () => this.onLastPage())
    $(pagination).append(lastButton)

    $(actions).append(pagination)
  }
  
  // Render the filters
  renderFilters(data) {
    $(`div[class="table-filters"]`).empty()

    if (!!this.options.filterOptions) {
      const container = $(`div[class="table-filters"]`)
      const grid = $(`<div class="table-filters-grid"></div>`)

      const clearButton = $(`<button class="ml-3 btn--tonal">Clear</button>`)
      $(clearButton).click(() => this.onClearFilters())

      $(container).append(grid)
      $(container).append(clearButton)

      this.options.filterOptions.map(f => {
        const count = (this.filters[f.field] || []).length
        const menuText = count > 0 ? `${count} selected` : "---"

        const formControl = $(`<div class="form-control"></div>`)
        const menuLabel = $(`<div class="menu-label">${f.label}</div>`)
        const menuControl = $(`<div class="menu-control"></div>`)
        const menuControlText = $(`<div class="text">${menuText}</div>`)
        const menuControlIcon = $(`<span class="icon">arrow_drop_down</span>`)
        const menu = $(`<div id="menu-${f.field}" class="menu"></div>`)
        
        f.options.forEach(o => {
          const menuItem = $(`<div class="menu-item">${o.value}<div>`)
          const menuItemIcon = $(`<span class="icon"></span>`)

          if (this.filters[f.field]?.indexOf(o.key) > -1) {
            $(menuItemIcon).text("done")
          }

          $(menuItem).click((e) => this.onClickFilterItem(e, f.field, o.key))
          $(menuItem).prepend(menuItemIcon)
          $(menu).append(menuItem)
        })

        $(menuControl).append(menuControlText)
        $(menuControl).append(menuControlIcon)
        $(formControl).click((e) => this.onClickFilter(e, f))
        $(formControl).append(menuControl)
        $(formControl).append(menuLabel)
        $(formControl).append(menu)
        $(grid).append(formControl)
      })

      if (this.openFilter) {
        $(`#${this.openFilter}`).trigger("click")
      }
    
      const filters = $(this.root).find(`div[class="table-filters"]`)
      $(filters).append(container)
    }
  }

  // Handler for clicking a filter
  onClickFilter(e, filter) {
    e.stopPropagation()

    $(`div[id^="menu-"`)
      .filter((_, menu) => $(menu).attr("id") !== `menu=${filter.field}`)
      .removeClass("open")

    const menu = $(`#menu-${filter.field}`)
    const open = $(menu).hasClass("open")

    if (open) {
      this.openFilter = null
      $(menu).removeClass("open")
    } else {
      this.openFilter = `menu-${filter.field}`
      $(menu).addClass("open")
    }
  }
  
  // Handler for clicking a filter menu item
  onClickFilterItem(e, field, value) {
    e.stopPropagation()

    if (!this.filters.hasOwnProperty(field)) {
      this.filters[field] = [value]
    } else {
      this.filters[field].indexOf(value) === -1
        ? this.filters[field].push(value)
        : this.filters[field] = this.filters[field].filter(o => o !== value)
    }

    this.render()
  }

  // Fetch the current page's data from the API
  async fetchData() {
    const pageUrl = new URL(this.options.url, window.location.origin)
    pageUrl.searchParams.set("page", this.currentPage)
    pageUrl.searchParams.set("per_page", this.options.perPage)

    if (this.query) {
      pageUrl.searchParams.set("q", this.query)
    }

    if (this.filters) {
      Object.keys(this.filters).forEach(key => {
        this.filters[key].forEach(value => {
          pageUrl.searchParams.append(key, value)
        })
      })
    }

    const resp = await fetch(pageUrl)
    const data = await resp.json()

    return data
  }

  onFirstPage() {
    this.currentPage = 1
    this.openFilter = null
    this.render()
  }

  onPrevPage() {
    this.currentPage--
    this.openFilter = null
    this.render()
  }

  onNextPage() {
    this.currentPage++
    this.openFilter = null
    this.render()
  }

  onLastPage() {
    this.currentPage = this.lastPage
    this.openFilter = null
    this.render()
  }

  onSearch(query) {
    this.currentPage = 1
    this.query = query.trim()
    this.openFilter = null
    this.render()
  }

  onClearFilters() {
    this.filters = {}
    this.query = null
    this.openFilter = null
    this.render()
    $(this.root).find("#id-search").val("")
  }

  onClickAway() {
    $(`div[id^="menu-"`).removeClass("open")
    this.openFilter = null
  }
}
