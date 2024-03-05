const ArrowUp = `<span class="icon">arrow_upward_alt</span>`
const ArrowDown = `<span class="icon">arrow_downward_alt</span>`
const ChevronLeftIcon = `<span class="icon">chevron_left</span>`
const ChevronRightIcon = `<span class="icon">chevron_right</span>`
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

    this.initializeColumns()
    this.initializePagination()
    this.initializeDOM()
    this.fetchData()

    // If the previous key exists in localStorage, remove the item
    const key = `${this.root.id}::columns`
    localStorage.removeItem(key)
  }

  // Fetch the data from the API
  async fetchData() {
    const url = new URL(this.options.url, window.location.origin)
    url.searchParams.set("page", this.pagination.page)
    url.searchParams.set("per_page", this.pagination.perPage)

    if (this.sort) {
      url.searchParams.set("sort", this.sort)
    }

    // TODO: query search
    // TODO: filters
    // TODO: error handling

    const resp = await fetch(url)
    const data = await resp.json()

    this.data = data.results
    this.pagination.hasNext = !!data.next
    this.pagination.hasPrev = !!data.previous
    this.pagination.count = data.count

    this.render()
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
    const actionsContainer = $(`<div class="table-actions"></div>`)
    const tableContainer = $(`<div class="table-container"></div>`)

    $(this.root).append(actionsContainer)
    $(this.root).append(tableContainer)

    this.dom = { actionsContainer, tableContainer }
  }

  // Render the component in the DOM
  render() {
    this.renderTableActions()
    this.renderTable()
  }

  // Render the table actions
  renderTableActions() {
    const searchContainer = $(`<div class="table-search"></div>`)
    const columnsContainer = $(`<div class="table-columns"></div>`)
    const paginationContainer = $(`<div class="table-pagination"></div>`)

    this.renderTableActionsSearch(searchContainer)
    this.renderTableActionsColumns(columnsContainer)
    this.renderTableActionsPagination(paginationContainer)

    $(this.dom.actionsContainer).empty()
    $(this.dom.actionsContainer).append(searchContainer)
    $(this.dom.actionsContainer).append(columnsContainer)
    $(this.dom.actionsContainer).append(paginationContainer)
  }

  // Render the table actions for search
  renderTableActionsSearch(searchContainer) {
  }

  // Render the table actions for columns
  renderTableActionsColumns(columnsContainer) {
    const dialog = $(`<div class="dialog"></div>`)
    $(dialog).on("click", (event) => this.clickAwayDialog(event, dialog))
    
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
      const div = $(`<div class="flex--center">${column}</div>`)
      
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

      if (!this.isColumnVisible) {
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
      $(table).append(tbody)
    })
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
  clickAwayDialog(event, dialog) {
    $(event.target).is(dialog) && $(dialog).removeClass("open")
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
}
