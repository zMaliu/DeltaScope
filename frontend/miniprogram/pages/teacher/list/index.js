const { request } = require("../../../utils/api")

Page({
  data: {
    list: [], loading: true, loadError: ''
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
    this.setData({ loading: true, loadError: '' })
    try {
      const res = await request({ url: '/api/teacher/submissions/pending' })
      this.setData({ list: res.data || [] })
    } catch (error) { this.setData({ loadError: error.message || '答卷加载失败，请重试' }) }
    finally { this.setData({ loading: false }) }
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
    wx.switchTab({
      url: "/pages/user/info/index"
    })
  }
})
