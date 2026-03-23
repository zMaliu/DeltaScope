const { request } = require("../../../utils/api")

Page({
  data: {
    keyword: "",
    users: []
  },
  onShow() {
    const app = getApp()
    const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
    const user = app.globalData.loginUser || wx.getStorageSync(key) || null
    if (!user || user.role !== "admin") {
      wx.reLaunch({ url: "/pages/auth/login/index" })
      return
    }
  },
  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value })
  },
  async searchUsers() {
    try {
      const res = await request({
        url: `/api/common/admin/users/search?keyword=${encodeURIComponent(this.data.keyword || "")}`
      })
      this.setData({ users: res.data || [] })
    } catch (error) {
      wx.showToast({ title: error.message || "查询失败", icon: "none" })
    }
  },
  async grantTeacher(e) {
    const account = e.currentTarget.dataset.account
    await this.changeRole("/api/common/admin/role/teacher/grant", account)
  },
  async revokeTeacher(e) {
    const account = e.currentTarget.dataset.account
    await this.changeRole("/api/common/admin/role/teacher/revoke", account)
  },
  async changeRole(url, account) {
    try {
      await request({
        url,
        method: "POST",
        data: { account }
      })
      wx.showToast({ title: "操作成功", icon: "success" })
      this.searchUsers()
    } catch (error) {
      wx.showToast({ title: error.message || "操作失败", icon: "none" })
    }
  }
})
