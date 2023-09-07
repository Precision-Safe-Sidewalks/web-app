class DataTable {
  constructor(rootId, options) {
    this.root = document.getElementById(rootId)
    this.options = options
    this.currentPage = 1
    this.lastPage = 1
    this.query = null

    this.initialize()
    this.render()
  }

  // Initialize the DOM elements defining the table
  initialize() {
    const actions = $(`<div class="table-actions"></div>`)
    const table = $(`<table class="table"></table>`)
    const thead = $(`<thead></thead>`)
    const tbody = $(`<tbody></tbody>`)

    const tr = $(`<tr></tr>`)
    this.options.columns?.forEach(c => $(tr).append($(`<th>${c}</th>`)))

    $(thead).append(tr)
    $(table).append(thead)
    $(table).append(tbody)

    $(this.root).append(actions)
    $(this.root).append(table)
  }

  // Render the data tbale
  async render() {
    const data = await this.fetchData()
    this.renderData(data)
    this.renderActions(data)
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
    if ($(this.root).find("#id-search").first().length === 0) {
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

  // Fetch the current page's data from the API
  async fetchData() {
    const pageUrl = new URL(this.options.url, window.location.origin)
    pageUrl.searchParams.set("page", this.currentPage)
    pageUrl.searchParams.set("per_page", this.options.perPage)

    if (this.query) {
      pageUrl.searchParams.set("q", this.query)
    }

    const resp = await fetch(pageUrl)
    const data = await resp.json()

    return data
  }

  onFirstPage() {
    this.currentPage = 1
    this.render()
  }

  onPrevPage() {
    this.currentPage--
    this.render()
  }

  onNextPage() {
    this.currentPage++
    this.render()
  }

  onLastPage() {
    this.currentPage = this.lastPage
    this.render()
  }

  onSearch(query) {
    this.currentPage = 1
    this.query = query.trim()
    this.render()
  }
}
