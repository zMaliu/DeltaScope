const { request } = require("../../../utils/api")

Page({
  data: {
    channels: [{ label: "提问答疑", value: "qa" }, { label: "学习打卡", value: "checkin" }, { label: "经验分享", value: "share" }, { label: "师生指导", value: "mentor" }],
    channel: "share",
    course: "",
    title: "",
    content: "",
    publishing: false,
    canPublish: false,
    draftRestored: false
  },
  onLoad() {
    const app = getApp()
    const user = app.globalData.loginUser || {}
    this._draftKey = `learningDraft:${user.user_id}`
    const draft = wx.getStorageSync(this._draftKey)
    if (draft) this.setData({ title: draft.title || '', content: draft.content || '', course: draft.course || '', channel: draft.channel || 'share', draftRestored: true }, () => this.updateReadiness())
  },
  onHide() { this.saveDraft() },
  onUnload() { this.saveDraft() },
  saveDraft() {
    if (!this._draftKey || this._published) return
    const { title, content, course, channel } = this.data
    if (title || content || course) wx.setStorageSync(this._draftKey, { title, content, course, channel })
    else wx.removeStorageSync(this._draftKey)
  },
  updateReadiness() { this.setData({ canPublish: this.data.title.trim().length >= 4 && this.data.content.trim().length >= 4 }) },
  onCourseInput(e) { this.setData({ course: e.detail.value }) },
  onTitleInput(e) { this.setData({ title: e.detail.value }, () => this.updateReadiness()) },
  onContentInput(e) { this.setData({ content: e.detail.value }, () => this.updateReadiness()) },
  selectChannel(e) { this.setData({ channel: e.currentTarget.dataset.value }) },
  async publish() {
    if (this.data.publishing) return
    const { title, content, course, channel } = this.data
    if (title.trim().length < 4 || content.trim().length < 4) {
      wx.showToast({ title: "标题和正文至少填写 4 个字", icon: "none" })
      return
    }
    this.setData({ publishing: true })
    try {
      await request({ url: "/api/student/forum/post", method: "POST", data: { title: title.trim(), content: content.trim(), course: course.trim(), channel } })
      this._published = true
      wx.removeStorageSync(this._draftKey)
      wx.showToast({ title: "发布成功", icon: "success" })
      wx.switchTab({ url: '/pages/student/forum/index' })
    } catch (error) {
      wx.showToast({ title: error.message || "发布失败，请稍后重试", icon: "none" })
    } finally { this.setData({ publishing: false }) }
  }
})
