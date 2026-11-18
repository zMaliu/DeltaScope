const { request } = require("../../../utils/api")

Page({
  data: {
    logoUrl: require("../../../config/index").LOGO_URL,
    phone: "",
    password: "",
    loading: false,
    error: '',
    showPassword: false
  },
  onLoad() {
    const app = getApp()
    if (app.globalData.loginUser && app.globalData.authToken) {
      wx.reLaunch({ url: app.globalData.loginUser.role === 'admin' ? '/pages/admin/permission/index' : '/pages/user/profile/index' })
    }
  },
  onPhoneInput(e) {
    this.setData({ phone: e.detail.value, error: '' })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value, error: '' })
  },
  togglePassword() { this.setData({ showPassword: !this.data.showPassword }) },

  goRegister() {
    wx.navigateTo({
      url: "/pages/auth/register/index"
    })
  },

  async handleLogin() {
    if (this.data.loading) return
    const { phone, password } = this.data
    
    if (!/^\d{11}$/.test(phone)) {
      this.setData({ error: '请输入 11 位手机号' })
      return
    }
    if (!password) {
      this.setData({ error: '请输入登录密码' })
      return
    }

    this.setData({ loading: true })
    try {
      const res = await request({
        url: "/api/common/auth/login",
        method: "POST",
        data: {
          phone,
          password
        }
      })
      this.applyAuthData(res.data)
      wx.reLaunch({ url: res.data.role === "admin" ? "/pages/admin/permission/index" : "/pages/user/profile/index" })
    } catch (error) {
      this.setData({ error: error.message || '暂时无法登录，请检查网络后重试' })
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
