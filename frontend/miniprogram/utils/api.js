const app = getApp()

function request({ url, method = "GET", data = {}, header = {} }) {
  const userKey = app.globalData.config.STORAGE_KEYS.LOGIN_USER
  const tokenKey = app.globalData.config.STORAGE_KEYS.AUTH_TOKEN
  const user = app.globalData.loginUser || wx.getStorageSync(userKey) || null
  const token = app.globalData.authToken || wx.getStorageSync(tokenKey) || ""
  const authHeader = token
    ? {
        Authorization: `Bearer ${token}`
      }
    : user
    ? {
        "X-User-Id": String(user.user_id),
        "X-User-Role": user.role
      }
    : {}
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.baseUrl}${url}`,
      method,
      data,
      header: {
        "Content-Type": "application/json",
        ...authHeader,
        ...header
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
          return
        }
        reject(res.data || { message: "请求失败" })
      },
      fail: reject
    })
  })
}

module.exports = {
  request
}
