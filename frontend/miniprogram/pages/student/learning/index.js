const { request } = require("../../../utils/api")

Page({
  data: {
    dimensions: [],
    suggestions: [],
    loading: true,
    loadError: '',
    stats: [{ label: '累计作答', value: '—' }, { label: '批改反馈', value: '—' }, { label: '学习分享', value: '—' }]
  },
  onShow() {
    const tab = this.getTabBar && this.getTabBar()
    if (tab) tab.setData({ active: 'learning' })
    this.loadDashboard()
  },
  async loadDashboard() {
    this.setData({ loading: true, loadError: '' })
    try {
      const res = await request({ url: "/api/student/learning-dashboard" })
      const dimensions = res.data.dimensions || []
      const count = label => parseInt((dimensions.find(item => item.label === label) || {}).value, 10) || 0
      this.setData({
        dimensions,
        stats: [{ label: '累计作答', value: count('每周一题') }, { label: '批改反馈', value: count('批改反馈') }, { label: '学习分享', value: count('论坛活跃') }],
        suggestions: res.data.suggestions || []
      })
    } catch (error) {
      this.setData({ loadError: error.message || '学习记录暂时无法加载' })
    } finally { this.setData({ loading: false }) }
  },
  goWeekly() { wx.switchTab({ url: '/pages/student/hall/index' }) },
  goResources() { wx.navigateTo({ url: '/pages/student/resources/index' }) },
  goGraph() { wx.navigateTo({ url: '/pages/student/graph/index' }) },
  goVisual() { wx.navigateTo({ url: '/pages/student/visual/index' }) },
  goVeritas() { wx.navigateTo({ url: '/pages/student/veritas/index' }) }
})
