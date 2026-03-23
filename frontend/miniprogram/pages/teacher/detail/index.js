const { request } = require("../../../utils/api")

Page({
  data: {
    submissionId: 0,
    submission: null,
    score: "",
    teacherComment: "",
    app: getApp()
  },
  onLoad(options) {
    const app = getApp()
    const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
    const user = app.globalData.loginUser || wx.getStorageSync(key) || null
    if (!user || user.role !== "teacher") {
      wx.reLaunch({ url: "/pages/auth/login/index" })
      return
    }
    this.setData({
      submissionId: Number(options.submissionId || 0)
    })
    this.loadSubmission()
  },
  async loadSubmission() {
    const res = await request({
      url: `/api/teacher/submission/detail?submission_id=${this.data.submissionId}`
    })
    this.setData({
      submission: res.data || null,
      score: res.data ? (res.data.score || "") : "",
      teacherComment: res.data ? (res.data.teacher_comment || "") : ""
    })
  },
  preview(e) {
    const index = Number(e.currentTarget.dataset.index)
    const rawUrls = (this.data.submission && this.data.submission.answer_image_urls) || []
    const urls = rawUrls.map(url => this.data.app.globalData.baseUrl + url)
    wx.previewImage({
      current: urls[index],
      urls
    })
  },
  onScoreInput(e) {
    this.setData({ score: e.detail.value })
  },
  onCommentInput(e) {
    this.setData({ teacherComment: e.detail.value })
  },
  async submitGrade() {
    if (!this.data.submission) {
      return
    }
    await request({
      url: "/api/teacher/submission/grade",
      method: "POST",
      data: {
        submission_id: this.data.submission.id,
        score: Number(this.data.score),
        teacher_comment: this.data.teacherComment
      }
    })
    wx.showToast({ title: "批改完成", icon: "success" })
    wx.navigateBack()
  }
})
