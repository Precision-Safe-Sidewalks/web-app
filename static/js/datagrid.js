const ArrowUp = `<span class="icon">arrow_upward_alt</span>`
const ArrowDown = `<span class="icon">arrow_downward_alt</span>`
const ArrowDropDown = `<span class="icon">arrow_drop_down</span>`
const ChevronLeftIcon = `<span class="icon">chevron_left</span>`
const ChevronRightIcon = `<span class="icon">chevron_right</span>`
const SearchIcon = `<span class="icon">search</span>`
const SettingsIcon = `<span class="icon">settings</span>`

class DataGrid {
  constructor(rootId, options = {}) {
    this.root = document.getElementById(rootId)
    this.options = options
    this.data = []
    this.visibleColumns = {}
    this.pagination = {}
    this.dom = {}
    this.sort = null
    this.filters = {}

    this.initializeFilters()
    this.initializeColumns()
    this.initializePagination()
    this.initializeDOM()
    this.fetchData()
  }

  // Initialize the filters
  initializeFilters() {
    if (!this.options.filterOptions?.length) return

    for (const filter of this.options.filterOptions) {
      this.filters[filter.field] = filter.default || []
    }

    $(window).on("click", (event) => this.closeFilters(event))
  }

  // Initialize the visible columns
  initializeColumns() {
    const key = `${this.root.id}-columns`
    const preset = localStorage.getItem(key)

    if (preset) {
      this.visibleColumns = JSON.parse(preset)
    }

    for (const column of this.options.columns) {
      if (!this.visibleColumns.hasOwnProperty(column)) {
        this.visibleColumns[column] = true
      }
    }

    localStorage.setItem(key, JSON.stringify(this.visibleColumns))
  }

  // Initialize the pagination
  initializePagination() {
    this.pagination = {
      page: 1,
      perPage: Math.min(this.options?.perPage, 30),
      hasPrev: false,
      hasNext: false,
      count: 0,
    }
  }

  // Initialize the DOM components
  initializeDOM() {
    const filtersContainer = $(`<div class="table-filters"></div>`)
    const actionsContainer = $(`<div class="table-actions"></div>`)
    const tableContainer = $(`<div class="table-container"></div>`)

    $(this.root).append(filtersContainer)
    $(this.root).append(actionsContainer)
    $(this.root).append(tableContainer)

    this.dom = { filtersContainer, actionsContainer, tableContainer }
  }

  // Render the component in the DOM
  render() {
    this.renderTableFilters()
    this.renderTableActions()
    this.renderTable()
  }

  // Render the table filters
  renderTableFilters() {
    if (!this.options.filterOptions?.length) return

    if (this.hasOpenFilters()) return
    
    const grid = $(`<div class="table-filters-grid"></div>`)
    const btnClear = $(`<button class="ml-3 btn--tonal">Clear</button>`)
    $(btnClear).on("click", () => this.clearFilters())

    this.options.filterOptions.forEach(filterOption => {
      const { field, label, options } = filterOption
      const count = this.filters[field]?.length || 0
      const menuLabelText = count !== 0 ? `${count} selected` : "---"

      const formControl = $(`<div class="form-control"></div>`)
      $(formControl).on("click", () => this.openFilter(event, field))

      const menuLabel = $(`<div class="menu-label">${label}</div>`)
      const menuControl = $(`<div class="menu-control"></div>`)
      const menuControlText = $(`<div class="text">${menuLabelText}</div>`)
      const menu = $(`<div id="menu-${field}" class="menu"></div>`)

      options.forEach(option => {
        const menuItem = $(`<div class="menu-item">${option.value}</div>`)
        $(menuItem).on("click", (event) => this.toggleFilter(event, field, option.key))

        const menuItemIcon = $(`<span class="icon"></span>`)

        if (this.filters[field]?.indexOf(option.key) !== -1) {
          $(menuItemIcon).text("done")
        }

        $(menuItem).prepend(menuItemIcon)
        $(menu).append(menuItem)
      })

      $(menuControl).append(menuControlText)
      $(menuControl).append(ArrowDropDown)
      $(formControl).append(menuControl)
      $(formControl).append(menuLabel)
      $(formControl).append(menu)
      $(grid).append(formControl)
    })
    
    $(grid).append(btnClear)
    $(this.dom.filtersContainer).empty()
    $(this.dom.filtersContainer).append(grid)
  }

  // Render the table actions
  renderTableActions() {

    // If the table has been rendered before, remove the old columns and
    // pagination containers but leave the search container.
    if (this.dom.actionsContainer.children().length !== 0) {
      $(this.dom.actionsContainer).find(`div[class="table-columns"]`).remove()
      $(this.dom.actionsContainer).find(`div[class="table-pagination"]`).remove()

    // If the table has not been rendered before, create the search container
    // and add it to the parent container.
    } else {
      const searchContainer = $(`<div class="table-search"></div>`)
      this.renderTableActionsSearch(searchContainer)
      $(this.dom.actionsContainer).append(searchContainer)
    }
    
    const columnsContainer = $(`<div class="table-columns"></div>`)
    const paginationContainer = $(`<div class="table-pagination"></div>`)

    this.renderTableActionsColumns(columnsContainer)
    this.renderTableActionsPagination(paginationContainer)

    $(this.dom.actionsContainer).append(columnsContainer)
    $(this.dom.actionsContainer).append(paginationContainer)
  }

  // Render the table actions for search
  renderTableActionsSearch(searchContainer) {
    const container = $(`<div class="search-bar"></div>`)
    const input = $(`<input type="text" placeholder="Search...">`)
    $(input).on("keyup", (event) => this.search(event))
    
    $(container).append(SearchIcon)
    $(container).append(input)
    $(searchContainer).append(container)
  }

  // Render the table actions for columns
  renderTableActionsColumns(columnsContainer) {
    const dialog = $(`<div class="dialog"></div>`)
    $(dialog).on("click", (event) => this.clickAway(event, dialog))
    
    const dialogContent = $(`<div class="dialog-content"></div>`)
    const dialogTitle = $(`<div class="dialog-title">Column Visibility</div>`)
    const dialogBody = $(`<div class="dialog-body"></div>`)

    this.options.columns.forEach(column => {
      const container = $(`<div class="mb-1"></div>`)
      const input = $(`<input type="checkbox" class="mr-2">`)
      const label = $(`<label>${column}<label>`)

      $(container).on("click", () => this.toggleColumn(column, input))
      $(input).prop("checked", this.isColumnVisible(column))

      $(container).append(input)
      $(container).append(label)
      $(dialogBody).append(container)
    })

    const btn = $(`<button class="btn--icon">${SettingsIcon}</button>`)
    $(btn).on("click", () => this.toggleDialog(dialog))

    $(dialogContent).append(dialogTitle)
    $(dialogContent).append(dialogBody)
    $(dialog).append(dialogContent)
    $(columnsContainer).append(dialog)
    $(columnsContainer).append(btn)
  }

  // Render the table actions for pagination
  renderTableActionsPagination(paginationContainer) {
    const { page, perPage, count, hasPrev, hasNext } = this.pagination

    const min = (count > 0) * (((page - 1) * perPage) + 1)
    const max = Math.min(count, min + perPage - 1)
    const label = $(`<span class="mr-2">Showing ${min} - ${max} of ${count}</span>`)

    const btnPrev = $(`<button class="btn--icon">${ChevronLeftIcon}</button>`)
    $(btnPrev).prop("disabled", !hasPrev)
    $(btnPrev).on("click", () => this.prevPage())

    const btnNext = $(`<button class="btn--icon">${ChevronRightIcon}</button>`)
    $(btnNext).prop("disabled", !hasNext)
    $(btnNext).on("click", () => this.nextPage())

    $(paginationContainer).append(label)
    $(paginationContainer).append(btnPrev)
    $(paginationContainer).append(btnNext)
  }

  // Render the table
  renderTable() {
    const table = $(`<table class="table"></table>`)
    this.renderTableHeader(table)
    this.renderTableBody(table)

    $(this.dom.tableContainer).empty()
    $(this.dom.tableContainer).append(table)
  }

  // Render the table header
  renderTableHeader(table) {
    const thead = $(`<thead></thead>`)
    const tr = $(`<tr></tr>`)

    this.options.columns.forEach((column, index) => {
      const sortable = this.options.sortOptions?.find(opt => opt.label === column)
      const th = $(`<th data-column=${index}></th>`)
      const div = $(`<div class="flex align-items-center">${column}</div>`)
      
      if (sortable) {
        $(th).on("click", () => this.toggleSort(sortable.sort))
        $(th).addClass("sortable")
      
        if (this.sort === sortable.sort) {
          $(div).append(ArrowUp)
        }

        if (this.sort === `-${sortable.sort}`) {
          $(div).append(ArrowDown)
        }
      }

      if (!this.isColumnVisible(column)) {
        $(th).addClass("hidden")
      }
      
      $(th).append(div)
      $(tr).append(th)
    })

    $(thead).append(tr)
    $(table).append(thead)
  }

  // Render the table body
  renderTableBody(table) {
    const tbody = $(`<tbody></tbody>`)
  
    this.data.forEach(row => {
      const tr = $(`<tr></tr>`)
      const values = Object.keys(row).map(key => row[key])

      this.options.columns.forEach((column, index) => {
        if (this.isColumnVisible(column)) {
          const value = values[index] !== null ? values[index] : "---"
          const td = $(`<td data-column=${index}>${value}</td>`)
          $(tr).append(td)
        }
      })

      $(tbody).append(tr)
    })

    if (this.data.length === 0) {
      $(tbody).append(`<tr><td align="center" colspan="100%">No available data</td></tr>`)
    } 
      
    $(table).append(tbody)
  }

  // Fetch the data from the API
  async fetchData() {
    const url = new URL(this.options.url, window.location.origin)
    url.searchParams.set("page", this.pagination.page)
    url.searchParams.set("per_page", this.pagination.perPage)

    if (this.sort) {
      url.searchParams.set("sort", this.sort)
    }

    Object.keys(this.filters).forEach(key => {
      this.filters[key].forEach(
        value => url.searchParams.append(key, value)
      )
    })

    // TODO: error handling

    const resp = await fetch(url)
    const data = await resp.json()

    this.data = data.results
    this.pagination.hasNext = !!data.next
    this.pagination.hasPrev = !!data.previous
    this.pagination.count = data.count

    this.render()
  }

  // Return true if the column is visible in the table
  isColumnVisible(column) {
    return !!this.visibleColumns[column]
  }

  // Decrement the page
  prevPage() {
    this.pagination.page--
    this.fetchData()
  }

  // Increment the page
  nextPage() {
    this.pagination.page++
    this.fetchData()
  }

  // Click away from a dialog
  clickAway(event, element) {
    $(event.target).is(element) && $(element).removeClass("open")
  }
  
  // Toggle a dialog open/closed
  toggleDialog(dialog) {
    $(dialog).hasClass("open")
      ? $(dialog).removeClass("open")
      : $(dialog).addClass("open")
  }

  // Toggle the visibility of a column
  toggleColumn(column, input) {
    this.visibleColumns[column] = !this.visibleColumns[column]
    $(input).prop("checked", this.visibleColumns[column])

    const key = `${this.root.id}-columns`
    localStorage.setItem(key, JSON.stringify(this.visibleColumns))

    const index = this.options.columns.indexOf(column)
    const elements = $(this.root).find(`[data-column=${index}]`)

    this.visibleColumns[column]
      ? $(elements).removeClass("hidden")
      : $(elements).addClass("hidden")
  }

  // Toggle the sorting column and direction
  toggleSort(column) {
    switch (this.sort) {
      case column:
        this.sort = `-${column}`
        break
      case `-${column}`:
        this.sort = column
      default:
        this.sort = column
    }

    this.fetchData()
  }

  // Togle a filter
  toggleFilter(event, field, value) {
    event.stopPropagation()

    const isSelected = this.filters[field].indexOf(value) === -1
    const icon = $(event.target).find(`span[class="icon"]`)
    const formControl = $(event.target).parents(`div[class="form-control"]`)
    const menuControlText = $(formControl).find(`div[class="text"]`)

    isSelected
      ? this.filters[field].push(value)
      : this.filters[field] = this.filters[field].filter(v => v !== value)

    isSelected
      ? $(icon).text("done")
      : $(icon).text("")

    isSelected
      ? $(menuControlText).text(`${this.filters[field].length} selected`)
      : $(menuControlText).text("---")

    this.fetchData()
  }

  // Open a filter menu
  openFilter(event, field) {
    event.stopPropagation()
    const menuId = `menu-${field}`

    $(`div[id^="menu-"]`)
      .filter((_, menu) => menu.id !== menuId)
      .removeClass("open")

    const menu = $(`#${menuId}`).addClass("open")
  }

  // Close all filters
  closeFilters(event) {
    const formControls = this.dom.filtersContainer.find(`div[class="form-control"]`)
    const isFilter = $(formControls).has(event.target).length !== 0

    if (!isFilter) {
      $(`div[id^="menu-"]`).removeClass("open")
    }
  }

  // Clear the filters
  clearFilters() {
    Object.keys(this.filters)
      .filter(key => key !== "q")
      .forEach(key => this.filters[key] = [])

    this.fetchData()
  }

  // Return true if there are any open filters
  hasOpenFilters() {
    return $(`div[id^="menu-"]`)
      .filter((_, menu) => $(menu).hasClass("open")).length > 0
  }

  // Search using the text search query
  search(event) {
    const query = event.target.value.trim()
    this.filters.q = !!query ? [query] : []
    this.fetchData()
  }
}
