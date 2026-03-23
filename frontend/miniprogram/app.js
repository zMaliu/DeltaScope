const CONFIG = require("./config/index")

App({
  onLaunch() {
    const user = wx.getStorageSync(CONFIG.STORAGE_KEYS.LOGIN_USER) || null
    const token = wx.getStorageSync(CONFIG.STORAGE_KEYS.AUTH_TOKEN) || ""
    this.globalData.loginUser = user
    this.globalData.authToken = token
  },
  globalData: {
    config: CONFIG,
    baseUrl: CONFIG.BASE_URL,
    logoUrl: CONFIG.LOGO_URL,
    loginUser: null,
    authToken: ""
  }
})
