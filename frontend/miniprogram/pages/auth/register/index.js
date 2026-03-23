const { request } = require("../../../utils/api")

Page({
  data: {
    role: "student",
    phone: "",
    password: "",
    authCode: "",
    loading: false
  },

  onLoad(options) {
    if (options.role) {
      this.setData({ role: options.role })
    }
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
  onAuthCodeInput(e) {
    this.setData({ authCode: e.detail.value })
  },

  async handleRegister() {
    if (this.data.loading) return
    const { phone, password, role, authCode } = this.data

    if (!phone || phone.length !== 11) {
      wx.showToast({ title: "请输入11位手机号", icon: "none" })
      return
    }
    if (!password || password.length < 6) {
      wx.showToast({ title: "请输入6位以上密码", icon: "none" })
      return
    }
    if (role === 'teacher' && !authCode) {
      wx.showToast({ title: "请输入教研授权码", icon: "none" })
      return
    }

    this.setData({ loading: true })
    try {
      const regRes = await request({
        url: "/api/common/auth/register",
        method: "POST",
        data: {
          phone,
          password,
          role,
          auth_code: authCode
        }
      })
      
      const app = getApp()
      const userKey = app.globalData.config.STORAGE_KEYS.LOGIN_USER
      const tokenKey = app.globalData.config.STORAGE_KEYS.AUTH_TOKEN
      app.globalData.loginUser = regRes.data
      app.globalData.authToken = regRes.data.token || ""
      wx.setStorageSync(userKey, regRes.data)
      wx.setStorageSync(tokenKey, regRes.data.token || "")
      
      wx.showToast({ title: "注册成功", icon: "success" })
      setTimeout(() => {
        wx.reLaunch({ url: "/pages/user/profile/index" })
      }, 1000)
    } catch (error) {
      wx.showToast({ title: error.message || "注册失败", icon: "none" })
    } finally {
      this.setData({ loading: false })
    }
  },
  goLogin() {
    wx.navigateBack()
  }
})
