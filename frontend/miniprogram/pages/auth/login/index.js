const { request } = require("../../../utils/api")

Page({
  data: {
    role: "student", // 'student' or 'teacher'
    phone: "",
    password: "",
    loading: false
  },
  
  onLoad() {
    // 页面加载
  },

  switchRole(e) {
    const role = e.currentTarget.dataset.role
    this.setData({ role })
  },

  onPhoneInput(e) {
    this.setData({ phone: e.detail.value })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value })
  },

  goRegister() {
    wx.navigateTo({
      url: `/pages/auth/register/index?role=${this.data.role}`
    })
  },

  async handleLogin() {
    if (this.data.loading) return
    const { phone, password, role } = this.data
    
    if (!phone || phone.length !== 11) {
      wx.showToast({ title: "请输入11位手机号", icon: "none" })
      return
    }
    if (!password) {
      wx.showToast({ title: "请输入密码", icon: "none" })
      return
    }

    this.setData({ loading: true })
    try {
      const res = await request({
        url: "/api/common/auth/login",
        method: "POST",
        data: {
          phone,
          password,
          role
        }
      })
      this.applyAuthData(res.data)
      wx.reLaunch({ url: "/pages/user/profile/index" })
    } catch (error) {
      wx.showToast({ title: error.message || "登录失败", icon: "none" })
    } finally {
      this.setData({ loading: false })
    }
  },

  applyAuthData(authData) {
    const app = getApp()
    const userKey = app.globalData.config.STORAGE_KEYS.LOGIN_USER
    const tokenKey = app.globalData.config.STORAGE_KEYS.AUTH_TOKEN
    app.globalData.loginUser = authData
    app.globalData.authToken = authData.token || ""
    wx.setStorageSync(userKey, authData)
    wx.setStorageSync(tokenKey, authData.token || "")
  }
})
