const app = getApp()

function request({ url, method = "GET", data = {}, header = {} }) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.baseUrl}${url}`,
      method,
      data,
      header: {
        "Content-Type": "application/json",
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
