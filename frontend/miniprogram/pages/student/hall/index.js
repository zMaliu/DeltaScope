const { request } = require('../../../utils/api')
const { timestamp } = require('../../../utils/date')
const { postCard, resourceCard, columns, matches, openCard } = require('../../../utils/feed')
Page({
  data: { question: null, result: null, status: '', statusText: '待发布', countdownText: '--:--:--', nickname: '', greeting: '你好', avatarText: '我', submittedCount: 0, feedbackCount: 0, expired: false, baseUrl: '', keyword: '', activeFilter: 'all', loading: true, loadError: '', feedError: '', feedColumns: [[], []], filters: [{ value: 'all', label: '为你推荐' }, { value: 'post', label: '学习笔记' }, { value: 'resource', label: '精选资料' }] },
  onShow() {
    const tab = this.getTabBar && this.getTabBar()
    if (tab) tab.setData({ active: 'home' })
    const app = getApp()
    const user = app.globalData.loginUser || wx.getStorageSync(app.globalData.config.STORAGE_KEYS.LOGIN_USER)
    if (!user || user.role !== 'student') { wx.reLaunch({ url: '/pages/auth/login/index' }); return }
    const nickname = user.nickname && user.nickname !== '未设置昵称' ? user.nickname : (user.real_name || '同学')
    const hour = new Date().getHours()
    const greeting = hour < 11 ? '早上好' : hour < 14 ? '中午好' : hour < 18 ? '下午好' : '晚上好'
    this.setData({ nickname, greeting, avatarText: nickname.slice(0, 1), baseUrl: app.globalData.baseUrl, logoUrl: app.globalData.logoUrl })
    this.loadPage()
  },
  onHide() { this.clearTimer() },
  onUnload() { this.clearTimer() },
  async onPullDownRefresh() { try { await this.loadPage() } finally { wx.stopPullDownRefresh() } },
  async loadPage() {
    this.setData({ loading: true, loadError: '', feedError: '' })
    await Promise.all([this.loadQuestion(), this.loadFeed(), this.loadLearning()])
    this.setData({ loading: false })
  },
  async loadLearning() {
    try {
      const res = await request({ url: '/api/student/learning-dashboard' })
      const dimensions = res.data.dimensions || []
      const count = label => parseInt((dimensions.find(item => item.label === label) || {}).value, 10) || 0
      this.setData({ submittedCount: count('每周一题'), feedbackCount: count('批改反馈') })
    } catch (error) { this.setData({ submittedCount: 0, feedbackCount: 0 }) }
  },
  async loadQuestion() {
    try {
      const res = await request({ url: '/api/student/question/current' })
      const question = res.data ? {
        ...res.data,
        display_image_urls: (res.data.image_urls || []).map(url => /^https?:\/\//.test(url) ? url : this.data.baseUrl + url)
      } : null
      this.setData({ question, result: null, expired: false, status: '', statusText: question ? '待完成' : '待发布' })
      if (question) {
        const result = await request({ url: `/api/student/answer/result?question_id=${question.id}` })
        const status = result.data ? result.data.status : ''
        this.setData({ result: result.data, status, statusText: status === 'graded' ? '已批改' : status === 'submitted' ? '待批改' : '待完成' })
      }
      this.startTimer()
    } catch (error) { this.clearTimer(); this.setData({ loadError: error.message || '本周题目暂时无法加载' }) }
  },
  async loadFeed() {
    const results = await Promise.all([
      request({ url: '/api/student/forum' }).then(res => ({ posts: res.data.posts || [] })).catch(() => ({ failed: true, posts: [] })),
      request({ url: '/api/student/resources' }).then(res => ({ resources: res.data.resources || [] })).catch(() => ({ failed: true, resources: [] }))
    ])
    this._feed = [...results[0].posts.map(postCard), ...results[1].resources.map(resourceCard)]
    this.setData({ feedError: results.some(result => result.failed) ? '部分内容加载失败，下拉可重试' : '' })
    this.applyFilter()
  },
  onSearch(e) { this.setData({ keyword: e.detail.value }); this.applyFilter() },
  clearSearch() { this.setData({ keyword: '' }); this.applyFilter() },
  switchFilter(e) { this.setData({ activeFilter: e.currentTarget.dataset.value }); this.applyFilter() },
  applyFilter() { this.setData({ feedColumns: columns((this._feed || []).filter(card => (this.data.activeFilter === 'all' || card.kind === this.data.activeFilter) && matches(card, this.data.keyword))) }) },
  openCard(e) { const card = (this._feed || []).find(card => card.id === e.currentTarget.dataset.id); if (card) openCard(card) },
  goSubmit() {
    if (this.data.status === 'graded') {
      const result = this.data.result || {}
      wx.showModal({ title: `本次得分 ${result.score == null ? '—' : result.score}`, content: result.teacher_comment || '老师已完成批改，继续保持思考。', showCancel: false })
      return
    }
    if (this.data.question && !this.data.expired && this.data.status !== 'submitted') wx.navigateTo({ url: `/pages/student/submit/index?questionId=${this.data.question.id}` })
  },
  goRanking() { wx.navigateTo({ url: '/pages/student/ranking/index' }) },
  goSearch() { getApp().globalData.communitySearch = true; wx.switchTab({ url: '/pages/student/forum/index' }) },
  goForum() { wx.switchTab({ url: '/pages/student/forum/index' }) },
  goCompose() { wx.navigateTo({ url: '/pages/student/compose/index' }) },
  goLearning() { wx.switchTab({ url: '/pages/student/learning/index' }) },
  goResources() { wx.navigateTo({ url: '/pages/student/resources/index' }) },
  goProfile() { wx.switchTab({ url: '/pages/user/info/index' }) },
  clearTimer() { if (this._timer) { clearInterval(this._timer); this._timer = null } },
  startTimer() {
    this.clearTimer()
    const tick = () => {
      const q = this.data.question
      if (!q || !q.deadline) { this.setData({ countdownText: '--:--:--' }); return }
      const deadline = timestamp(q.deadline)
      if (!Number.isFinite(deadline)) { this.setData({ countdownText: '--:--:--' }); return }
      const seconds = Math.floor(Math.max(deadline - Date.now(), 0) / 1000)
      const pad = n => String(n).padStart(2, '0')
      this.setData({ expired: seconds <= 0, countdownText: seconds <= 0 ? '本期已截止' : `${Math.floor(seconds / 86400)}天 ${pad(Math.floor(seconds % 86400 / 3600))}:${pad(Math.floor(seconds % 3600 / 60))}:${pad(seconds % 60)}` })
    }
    tick(); this._timer = setInterval(tick, 1000)
  },
  previewQuestion(e) {
    const urls = (this.data.question.image_urls || []).map(url => /^https?:\/\//.test(url) ? url : this.data.baseUrl + url)
    wx.previewImage({ current: urls[e.currentTarget.dataset.index], urls })
  }
})
