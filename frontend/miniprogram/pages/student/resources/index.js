const { request } = require("../../../utils/api")
const { resourceCard, matches, openCard } = require("../../../utils/feed")

Page({
  data: {
    resources: [],
    visibleResources: [],
    count: 0,
    filters: [],
    currentCategory: "",
    keyword: "",
    loading: false,
    loadError: ""
  },
  onShow() {
    this.loadResources()
  },
  async loadResources(category = this.data.currentCategory) {
    if (typeof category !== 'string') category = this.data.currentCategory
    const requestId = (this._requestId || 0) + 1
    this._requestId = requestId
    this.setData({ loading: true, loadError: "" })
    try {
      const res = await request({
        url: `/api/student/resources?category=${encodeURIComponent(category || "")}`
      })
      if (requestId !== this._requestId) return
      this._resources = (res.data.resources || []).map(resourceCard)
      this.setData({
        resources: res.data.resources || [],
        filters: res.data.filters || [],
        currentCategory: category || ""
      })
      this.applyFilter()
    } catch (error) {
      if (requestId === this._requestId) this.setData({ loadError: error.message || "资源加载失败" })
    } finally {
      if (requestId === this._requestId) this.setData({ loading: false })
    }
  },
  switchFilter(e) {
    const value = e.currentTarget.dataset.value || ""
    this.loadResources(value)
  },
  retry() { this.loadResources() },
  onSearch(e) { this.setData({ keyword: e.detail.value }, () => this.applyFilter()) },
  clearSearch() { this.setData({ keyword: "" }, () => this.applyFilter()) },
  applyFilter() {
    const resources = (this._resources || []).filter(resource => matches(resource, this.data.keyword))
    this.setData({ visibleResources: resources, count: resources.length })
  },
  openCard(e) { const card = (this._resources || []).find(resource => resource.id === e.currentTarget.dataset.id); if (card) openCard(card) }
})
