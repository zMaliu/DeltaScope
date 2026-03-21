const { request } = require("../../../utils/api")
const { chooseAndCompressImages, uploadImages } = require("../../../utils/upload")

Page({
  data: {
    questionId: 0,
    images: []
  },
  onLoad(options) {
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
    const app = getApp()
    const uploadUrl = `${app.globalData.baseUrl}/api/common/upload`
    const imageUrls = await uploadImages(this.data.images, uploadUrl)
    await request({
      url: "/api/student/answer/submit",
      method: "POST",
      header: {
        "X-User-Id": "10001",
        "X-User-Role": "student"
      },
      data: {
        question_id: this.data.questionId,
        image_urls: imageUrls
      }
    })
    wx.showToast({ title: "提交成功", icon: "success" })
  }
})
