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
      url: "/api/teacher/submissions/pending",
      header: {
        "X-User-Id": "90001",
        "X-User-Role": "teacher"
      }
    })
    this.setData({
      list: res.data || []
    })
  },
  openDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/teacher/detail/index?submissionId=${id}`
    })
  }
})
