const { request } = require("../../../utils/api")

Page({
  data: {
    list: []
  },
  onShow() {
    const app = getApp()
    const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
    const user = app.globalData.loginUser || wx.getStorageSync(key) || null
    if (!user || user.role !== "teacher") {
      wx.reLaunch({ url: "/pages/auth/login/index" })
      return
    }
    this.loadData()
  },
  async loadData() {
    const res = await request({
      url: "/api/teacher/submissions/pending"
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
  },
  goPublish() {
    wx.navigateTo({
      url: '/pages/teacher/publish/index'
    })
  },
  goProfile() {
    wx.navigateTo({
      url: "/pages/user/info/index"
    })
  }
})
