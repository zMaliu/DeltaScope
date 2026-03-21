const { request } = require("../../../utils/api")

Page({
  data: {
    list: []
  },
  onShow() {
    this.loadData()
  },
  async loadData() {
    const res = await request({
      url: "/api/common/ranking?limit=50"
    })
    this.setData({
      list: res.data || []
    })
  }
})
