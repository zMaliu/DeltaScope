const { request } = require("../../../utils/api")
const { uploadFile } = require("../../../utils/upload")

Page({
  data: {
    maxScore: "",
    deadlineDate: "",
    deadlineTime: "",
    imageUrls: [],
    loading: false,
    app: getApp()
  },

  onShow() {
    // 设置默认截止时间为明天晚上 23:59
    const tmr = new Date(Date.now() + 86400000)
    const y = tmr.getFullYear()
    const m = String(tmr.getMonth() + 1).padStart(2, '0')
    const d = String(tmr.getDate()).padStart(2, '0')
    this.setData({
      deadlineDate: `${y}-${m}-${d}`,
      deadlineTime: "23:59"
    })
  },

  onScoreInput(e) { this.setData({ maxScore: e.detail.value }) },
  onDateChange(e) { this.setData({ deadlineDate: e.detail.value }) },
  onTimeChange(e) { this.setData({ deadlineTime: e.detail.value }) },

  async chooseImage() {
    try {
      const res = await new Promise((resolve, reject) => {
        wx.chooseMedia({
          count: 9 - this.data.imageUrls.length,
          mediaType: ['image'],
          sourceType: ['album', 'camera'],
          success: resolve,
          fail: reject
        })
      })
      
      wx.showLoading({ title: '上传中' })
      const newUrls = [...this.data.imageUrls]
      for (const file of res.tempFiles) {
        const uploadRes = await uploadFile(file.tempFilePath)
        if (uploadRes && uploadRes.url) {
          newUrls.push(uploadRes.url)
        }
      }
      this.setData({ imageUrls: newUrls })
    } catch (e) {
      if (e.errMsg && !e.errMsg.includes('cancel')) {
        wx.showToast({ title: '选择或上传失败', icon: 'none' })
      }
    } finally {
      wx.hideLoading()
    }
  },

  async submitPublish() {
    if (this.data.loading) return
    const { maxScore, deadlineDate, deadlineTime, imageUrls } = this.data

    if (!maxScore || isNaN(maxScore) || Number(maxScore) <= 0) {
      return wx.showToast({ title: "请输入有效的满分", icon: "none" })
    }
    if (!imageUrls.length) {
      return wx.showToast({ title: "请至少上传一张题目图片", icon: "none" })
    }

    const deadlineStr = `${deadlineDate} ${deadlineTime}:00`

    this.setData({ loading: true })
    try {
      await request({
        url: "/api/teacher/question/publish",
        method: "POST",
        data: {
          title: `本周新题(${deadlineDate})`,
          content: "请看图作答",
          image_urls: imageUrls,
          max_score: Number(maxScore),
          deadline: deadlineStr
        }
      })
      wx.showToast({ title: "发布成功", icon: "success" })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } catch (error) {
      wx.showToast({ title: error.message || "发布失败", icon: "none" })
    } finally {
      this.setData({ loading: false })
    }
  }
})