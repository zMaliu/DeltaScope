const { request } = require("../../../utils/api")
const { postCard, columns, matches, openCard } = require("../../../utils/feed")

Page({
  data: {
    filters: [{ label: "推荐", value: "" }, { label: "提问答疑", value: "qa" }, { label: "学习打卡", value: "checkin" }, { label: "经验分享", value: "share" }, { label: "师生指导", value: "mentor" }],
    activeFilter: "",
    keyword: "",
    searchFocus: false,
    feedColumns: [[], []],
    count: 0,
    loading: false,
    loadError: ""
  },
  onShow() {
    const tab = this.getTabBar && this.getTabBar()
    if (tab) tab.setData({ active: 'community' })
    const app = getApp()
    this.setData({ searchFocus: !!app.globalData.communitySearch })
    app.globalData.communitySearch = false
    this.loadForum()
  },
  async onPullDownRefresh() { try { await this.loadForum() } finally { wx.stopPullDownRefresh() } },
  async loadForum() {
    const requestId = (this._requestId || 0) + 1
    this._requestId = requestId
    this.setData({ loading: true, loadError: "" })
    try {
      const channel = this.data.activeFilter
      const res = await request({ url: `/api/student/forum${channel ? `?channel=${encodeURIComponent(channel)}` : ""}` })
      if (requestId !== this._requestId) return
      this._posts = (res.data.posts || []).map(postCard)
      this.applyFilter()
    } catch (error) {
      if (requestId === this._requestId) this.setData({ loadError: error.message || "社区内容加载失败" })
    } finally { if (requestId === this._requestId) this.setData({ loading: false }) }
  },
  switchChannel(e) {
    const activeFilter = e.currentTarget.dataset.value || ""
    this.setData({ activeFilter }, () => this.loadForum())
  },
  onSearch(e) { this.setData({ keyword: e.detail.value }, () => this.applyFilter()) },
  clearSearch() { this.setData({ keyword: "" }, () => this.applyFilter()) },
  applyFilter() {
    const posts = (this._posts || []).filter(post => matches(post, this.data.keyword))
    this.setData({ feedColumns: columns(posts), count: posts.length })
  },
  compose() { wx.navigateTo({ url: "/pages/student/compose/index" }) },
  openCard(e) { const card = (this._posts || []).find(post => post.id === e.currentTarget.dataset.id); if (card) openCard(card) }
})
