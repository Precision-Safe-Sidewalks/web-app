class DataTable {
  constructor(rootId, options) {
    this.root = document.getElementById(rootId)
    this.options = options
    this.currentPage = 1
    this.lastPage = 1
    this.query = null
    this.filters = {}
    this.openFilter = null
    this.sortBy = null
    this.visibleColumns = {}
    this.visibleColumnsDraft = {}

    this.initialize()
    this.render()
  }

  // Initialize the DOM elements defining the table
  initialize() {
    const actions = $(`<div class="table-actions"></div>`)
    const filters = $(`<div class="table-filters"></div>`)
    const tableContainer = $(`<div class="table-container"></div>`)
    const table = $(`<table class="table"></table>`)
    const thead = $(`<thead></thead>`)
    const tbody = $(`<tbody></tbody>`)

    // Set the default visible columns (from localStorage or from the
    // columns available in the options on first load.
    this.visibleColumns = this.options.columns?.reduce(
      (acc, cur) => ({ ...acc, [cur]: true }),
      {},
    )

    const storageKey = `${this.root.id}::columns`
    const storageColumns = localStorage.getItem(storageKey)

    if (storageColumns) {
      this.visibleColumns = { ...this.visibleColumns, ...storageColumns } 
    }

    // Set the default filters (if specified)
    this.filters = this.options?.filterOptions?.reduce(
      (acc, cur) => cur.default ? ({ ...acc, [cur.field]: cur.default }) : acc,
      {},
    )

    $(table).append(thead)
    $(table).append(tbody)
    $(tableContainer).append(table)

    $(this.root).append(filters)
    $(this.root).append(actions)
    $(this.root).append(tableContainer)

    $(window).click(this.onClickAway)
  }

  // Render the data tbale
  async render() {
    const data = await this.fetchData()
    this.renderHeader()
    this.renderData(data)
    this.renderActions(data)
    this.renderFilters(data)
  }

  // Render the table header
  async renderHeader() {
    const thead = $(this.root).find("thead")
    $(thead).empty()

    const tr = $("<tr></tr>")
    $(thead).append(tr)

    this.options.columns?.forEach(column => {
      if (this.visibleColumns[column]) {
        const th = $(`<th id="th-${column}"></th>`)
        const sortOption = this.options.sortOptions?.find(o => o.label === column)
        $(tr).append(th)

        if (!!sortOption) {
          const iconAsc = $(`<span id="id-asc" class="icon">arrow_upward_alt</span>`)
          const iconDesc = $(`<span id="id-desc" class="icon">arrow_downward_alt</span>`)
          const content = $(`<div class="flex align-items-center">${column}</div>`)

          if (this.sortBy?.label === column) {
            $(iconAsc).css("display", this.sortBy.asc ? "block" : "none")
            $(iconDesc).css("display", this.sortBy.asc ? "none": "block")
          } else {
            $(iconAsc).css("display", "none")
            $(iconDesc).css("display", "none")
          }

          $(content).css("cursor", "pointer")
          $(content).append(iconAsc)
          $(content).append(iconDesc)
          $(th).append(content)

          $(th).click(() => this.onSortColumn(sortOption))
        } else {
          $(th).text(column)
        }
      }
    })
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
      Object.values(row).forEach((value, index) => {
        const column = this.options.columns[index]
        const isVisible = this.visibleColumns[column]
        
        if (isVisible) {
          $(tr).append(`<td>${value === null ? '---' : value}</td>`)
        }
      })
      $(tbody).append(tr)
    })
  }

  renderActions(data) {
    const actions = $(this.root).find(`div[class="table-actions"]`)
    
    this.renderSearch(actions, data)
    this.renderColumnSettings(actions,  data)
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

  // Render the column settings
  renderColumnSettings(actions, data) {
    const element = $(this.root).find("#id-columns").first()

    if ($(element).length === 0) {
      const container = $(`<div id="id-columns" class="table-column-settings"></div`)

      const button = $(`
        <button id="btn-columns" class="btn--icon">
          <span class="icon">settings</span>
        </button>
      `)

      const dialog = $(`<div id="id-columns-dialog" class="dialog" data-control="btn-columns"></div>`)
      const dialogContent = $(`<div class="dialog-content"></div>`)
      const dialogTitle = $(`<div class="dialog-title">Table Columns</div>`)
      const dialogBody = $(`<div class="dialog-body"></div>`)
      const dialogActions = $(`<div class="dialog-actions"></div>`)

      this.options?.columns?.forEach((column, index) => {
        const label = $(`<label class="ml-2" style="cursor: pointer">${column}</label>`)
        const input = $(`<input type="checkbox" id="dialog_column_${index}">`)
        $(input).prop("checked", this.visibleColumns[column])

        const div = $(`<div class="pb-1"></div>`)
        $(div).on("click", () => this.onToggleColumn(index))
        $(div).append(input)
        $(div).append(label)

        $(dialogBody).append(div)
      })
      
      const saveButton = $(`<button class="btn">Save</button>`)
      saveButton.on("click", () => this.onSaveColumns())

      $(dialogActions).append(saveButton)
      $(dialogContent).append(dialogTitle)
      $(dialogContent).append(dialogBody)
      $(dialogContent).append(dialogActions)
      $(dialog).append(dialogContent)

      $(container).append(button)
      $(container).append(dialog)
      $(actions).append(container)

      initializeDialog(dialog)
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

    if (this.sortBy) {
      const value = this.sortBy.asc ? this.sortBy.sort : `-${this.sortBy.sort}`
      pageUrl.searchParams.set("sort", value)
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

  onClearFilters() {
    this.filters = {}
    this.query = null
    this.openFilter = null
    this.render()
    $(this.root).find("#id-search").val("")
  }

  onSortColumn(option) { 
    $(this.root).find("th").find(`span[class="icon"]`).css("display", "none")

    const th = $(this.root).find(`th[id="th-${option.label}"]`) 
    const iconAsc = $(th).find("#id-asc")
    const iconDesc = $(th).find("#id-desc")

    const asc = (option.label === this.sortBy?.label) ? !this.sortBy.asc : true

    $(iconAsc).css("display", asc ? "block" : "none")
    $(iconDesc).css("display", asc ? "none" : "block")
    
    this.sortBy = {...option, asc: asc}
    this.openFilter = null
    this.currentPage = 1
    this.render()
  }

  onClickAway() {
    $(`div[id^="menu-"`).removeClass("open")
    this.openFilter = null
  }

  onToggleColumn(index) {
    const input = $(`#dialog_column_${index}`)
    const isChecked = $(input).is(":checked")
    const column = this.options.columns[index]

    this.visibleColumnsDraft[column] = !isChecked
    $(input).prop("checked", !isChecked)
  }

  onSaveColumns() {
    let visibleColumns = {}

    for (const column of this.options.columns) {
      if (this.visibleColumnsDraft.hasOwnProperty(column)) {
        visibleColumns[column] = this.visibleColumnsDraft[column]
        delete this.visibleColumnsDraft[column]
      } else {
        visibleColumns[column] = this.visibleColumns[column]
      }
    }

    this.visibleColumns = visibleColumns

    const storageKey = `${this.root.id}::columns`
    localStorage.setItem(storageKey, JSON.stringify(this.visibleColumns))

    const dialog = $("#id-columns-dialog")
    $(dialog).removeClass("open")

    this.render()
  }
}
