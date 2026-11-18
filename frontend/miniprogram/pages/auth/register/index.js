const { request } = require("../../../utils/api")

Page({
  data: {
    logoUrl: require("../../../config/index").LOGO_URL,
    phone: "",
    password: "",
    loading: false
  },

  onPhoneInput(e) {
    this.setData({ phone: e.detail.value })
  },
  onPasswordInput(e) {
    this.setData({ password: e.detail.value })
  },
  async handleRegister() {
    if (this.data.loading) return
    const { phone, password } = this.data

    if (!phone || phone.length !== 11) {
      wx.showToast({ title: "请输入11位手机号", icon: "none" })
      return
    }
    if (!password || password.length < 8) {
      wx.showToast({ title: "密码至少需要8个字符", icon: "none" })
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
          role: "student"
        }
      })
      const app = getApp()
      const userKey = app.globalData.config.STORAGE_KEYS.LOGIN_USER
      const tokenKey = app.globalData.config.STORAGE_KEYS.AUTH_TOKEN
      app.globalData.loginUser = regRes.data
      app.globalData.authToken = regRes.data.token || ""
      wx.setStorageSync(userKey, regRes.data)
      wx.setStorageSync(tokenKey, regRes.data.token || "")
      wx.showToast({ title: "账号创建成功", icon: "success" })
      wx.reLaunch({ url: "/pages/user/profile/index" })
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
