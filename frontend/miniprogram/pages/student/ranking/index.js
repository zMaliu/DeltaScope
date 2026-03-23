const { request } = require("../../../utils/api")

Page({
  data: {
    list: [],
    currentUserId: null
  },
  onShow() {
    const app = getApp()
    const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
    const user = app.globalData.loginUser || wx.getStorageSync(key) || null
    if (user) {
      this.setData({ currentUserId: user.user_id })
    }
    this.loadData()
  },
  async loadData() {
    const res = await request({
      url: "/api/common/ranking?limit=50"
    })
    this.setData({
      list: res.data || []
    })
  },
  viewFeedback(e) {
    const questionId = e.currentTarget.dataset.questionId
    if (!questionId) return
    const app = getApp()
    const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
    const user = app.globalData.loginUser || wx.getStorageSync(key) || null
    
    const item = this.data.list.find(i => i.question_id === questionId && i.user_id === user?.user_id)
    if (item && item.teacher_comment) {
      wx.showModal({
        title: '老师评语',
        content: item.teacher_comment,
        showCancel: false,
        confirmText: '知道了'
      })
    }
  }
})
