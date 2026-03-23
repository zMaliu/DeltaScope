const { request } = require("../../../utils/api")

Page({
  data: {
    userInfo: {}
  },

  onShow() {
    this.loadProfile()
  },

  async loadProfile() {
    try {
      const res = await request({ url: "/api/common/profile/me" })
      this.setData({ userInfo: res.data || {} })
      
      // 更新全局 user 信息
      const app = getApp()
      const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
      const user = app.globalData.loginUser || wx.getStorageSync(key) || {}
      const merged = { ...user, ...res.data }
      app.globalData.loginUser = merged
      wx.setStorageSync(key, merged)
    } catch (error) {
      wx.showToast({ title: "加载信息失败", icon: "none" })
    }
  },

  goEditProfile() {
    wx.navigateTo({
      url: "/pages/user/profile/index?edit=1"
    })
  },

  handleLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出当前账号吗？',
      success: (res) => {
        if (res.confirm) {
          const app = getApp()
          const userKey = app.globalData.config.STORAGE_KEYS.LOGIN_USER
          const tokenKey = app.globalData.config.STORAGE_KEYS.AUTH_TOKEN
          app.globalData.loginUser = null
          app.globalData.authToken = ""
          wx.removeStorageSync(userKey)
          wx.removeStorageSync(tokenKey)
          wx.reLaunch({ url: "/pages/auth/login/index" })
        }
      }
    })
  }
})