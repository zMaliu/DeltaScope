const { request } = require("../../../utils/api")
const { chooseAndCompressImages, uploadImages } = require("../../../utils/upload")

Page({
  data: {
    questionId: 0,
    images: []
  },
  onLoad(options) {
    const app = getApp()
    const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
    const user = app.globalData.loginUser || wx.getStorageSync(key) || null
    if (!user || user.role !== "student") {
      wx.reLaunch({ url: "/pages/auth/login/index" })
      return
    }
    this.setData({
      questionId: Number(options.questionId || 0)
    })
  },
  async addImages() {
    const current = this.data.images
    const rest = Math.max(9 - current.length, 0)
    if (rest <= 0) {
      return
    }
    const selected = await chooseAndCompressImages(rest)
    this.setData({
      images: current.concat(selected)
    })
  },
  removeImage(e) {
    const index = Number(e.currentTarget.dataset.index)
    const next = this.data.images.filter((_, i) => i !== index)
    this.setData({ images: next })
  },
  preview(e) {
    const index = Number(e.currentTarget.dataset.index)
    wx.previewImage({
      current: this.data.images[index],
      urls: this.data.images
    })
  },
  async submitAnswer() {
    if (!this.data.questionId || this.data.images.length === 0) {
      wx.showToast({ title: "请先上传图片", icon: "none" })
      return
    }
    wx.showLoading({ title: '提交中...', mask: true })
    try {
      const app = getApp()
      const uploadUrl = `${app.globalData.baseUrl}/api/common/upload`
      const imageUrls = await uploadImages(this.data.images, uploadUrl)
      await request({
        url: "/api/student/answer/submit",
        method: "POST",
        data: {
          question_id: this.data.questionId,
          image_urls: imageUrls
        }
      })
      wx.hideLoading()
      wx.showToast({ title: "提交成功", icon: "success" })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } catch (error) {
      wx.hideLoading()
      wx.showToast({ title: error.message || "提交失败", icon: "none" })
    }
  }
})
