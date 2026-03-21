const { request } = require("../../../utils/api")

Page({
  data: {
    submissionId: 0,
    submission: null,
    score: "",
    teacherComment: ""
  },
  onLoad(options) {
    this.setData({
      submissionId: Number(options.submissionId || 0)
    })
    this.loadSubmission()
  },
  async loadSubmission() {
    const res = await request({
      url: `/api/teacher/submission/detail?submission_id=${this.data.submissionId}`,
      header: {
        "X-User-Id": "90001",
        "X-User-Role": "teacher"
      }
    })
    this.setData({ submission: res.data || null })
  },
  preview(e) {
    const index = Number(e.currentTarget.dataset.index)
    const urls = (this.data.submission && this.data.submission.answer_image_urls) || []
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
      header: {
        "X-User-Id": "90001",
        "X-User-Role": "teacher"
      },
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
