const { request } = require("../../../utils/api")

Page({
  data: {
    question: null,
    countdownText: "--:--:--",
    timer: null,
    logoUrl: ""
  },
  onLoad() {
    const app = getApp()
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
      url: "/api/student/question/current",
      header: {
        "X-User-Id": "10001",
        "X-User-Role": "student"
      }
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
  }
})
