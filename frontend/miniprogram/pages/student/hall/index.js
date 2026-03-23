const { request } = require("../../../utils/api")

Page({
  data: {
    question: null,
    countdownText: "--:--:--",
    timer: null,
    logoUrl: "",
    app: getApp()
  },
  onLoad() {
    const app = getApp()
    const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
    const user = app.globalData.loginUser || wx.getStorageSync(key) || null
    if (!user || user.role !== "student") {
      wx.reLaunch({ url: "/pages/auth/login/index" })
      return
    }
    this.setData({
      logoUrl: app.globalData.logoUrl || ""
    })
    this.loadQuestion()
  },
  onUnload() {
    this.clearTimer()
  },
  async loadQuestion() {
    const res = await request({
      url: "/api/student/question/current"
    })
    this.setData({ question: res.data || null })
    this.startTimer()
  },
  goSubmit() {
    const { question } = this.data
    if (!question) {
      return
    }
    wx.navigateTo({
      url: `/pages/student/submit/index?questionId=${question.id}`
    })
  },
  clearTimer() {
    const { timer } = this.data
    if (timer) {
      clearInterval(timer)
      this.setData({ timer: null })
    }
  },
  startTimer() {
    this.clearTimer()
    const run = () => {
      const { question } = this.data
      if (!question || !question.deadline) {
        this.setData({ countdownText: "--:--:--" })
        return
      }
      const deadline = new Date(question.deadline).getTime()
      const now = Date.now()
      const diff = Math.max(deadline - now, 0)
      const totalSeconds = Math.floor(diff / 1000)
      const d = Math.floor(totalSeconds / 86400)
      const h = Math.floor((totalSeconds % 86400) / 3600)
      const m = Math.floor((totalSeconds % 3600) / 60)
      const s = totalSeconds % 60
      const text = `${d}天 ${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
      this.setData({ countdownText: text })
    }
    run()
    const timer = setInterval(run, 1000)
    this.setData({ timer })
  },
  goRanking() {
    wx.navigateTo({
      url: "/pages/student/ranking/index"
    })
  },
  goProfile() {
    wx.navigateTo({
      url: "/pages/user/info/index"
    })
  },
  previewQuestion(e) {
    const index = e.currentTarget.dataset.index
    const urls = this.data.question.image_urls.map(url => this.data.app.globalData.baseUrl + url)
    wx.previewImage({
      current: urls[index],
      urls
    })
  }
})
