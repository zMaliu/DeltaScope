const { request } = require("../../../utils/api")

Page({
  data: {
    nodes: [],
    loading: true, loadError: ''
  },
  onShow() {
    this.loadGraph()
  },
  async loadGraph() {
    this.setData({ loading: true, loadError: '' })
    try {
      const res = await request({ url: "/api/student/knowledge-graph" })
      this.setData({ nodes: res.data.nodes || [] })
    } catch (error) {
      this.setData({ loadError: error.message || '知识目录加载失败，请重试' })
    } finally { this.setData({ loading: false }) }
  }
})
