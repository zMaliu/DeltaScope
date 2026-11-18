const { request } = require("../../../utils/api")

Page({
  data: {
    userInfo: {},
    detailsOpen: false,
    maskedPhone: '',
    certOpen: false,
    certCode: '',
    certError: '',
    certifying: false,
    stats: [{ label: '累计作答', value: '—' }, { label: '批改反馈', value: '—' }, { label: '学习分享', value: '—' }],
    logoUrl: require("../../../config/index").LOGO_URL
  },

  onShow() {
    const tab = this.getTabBar && this.getTabBar()
    if (tab) tab.setData({ active: 'me', hidden: false })
    this.loadProfile()
  },
  onHide() { this.setData({ certOpen: false, certCode: '' }); this.setNavHidden(false) },
  setNavHidden(hidden) {
    const tab = this.getTabBar && this.getTabBar()
    if (tab) tab.setData({ hidden })
  },

  async loadProfile() {
    try {
      const res = await request({ url: "/api/common/profile/me" })
      const profile = res.data || {}
      const phone = profile.phone || ''
      this.setData({ userInfo: profile, maskedPhone: /^\d{11}$/.test(phone) ? phone.slice(0, 3) + '****' + phone.slice(-4) : phone })
      if (profile.role === 'student') this.loadStats()
      
      // 更新全局 user 信息
      const app = getApp()
      const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
      const user = app.globalData.loginUser || wx.getStorageSync(key) || {}
      const merged = { ...user, ...res.data }
      app.globalData.loginUser = merged
      wx.setStorageSync(key, merged)
    } catch (error) {
      wx.showToast({ title: "加载信息失败", icon: "none" })
    }
  },
  async loadStats() {
    try {
      const res = await request({ url: '/api/student/learning-dashboard' })
      const dimensions = res.data.dimensions || []
      const count = label => parseInt((dimensions.find(item => item.label === label) || {}).value, 10) || 0
      this.setData({ stats: [{ label: '累计作答', value: count('每周一题') }, { label: '批改反馈', value: count('批改反馈') }, { label: '学习分享', value: count('论坛活跃') }] })
    } catch (error) { /* Keep unavailable counters distinct from zero. */ }
  },
  toggleDetails() { this.setData({ detailsOpen: !this.data.detailsOpen }) },
  goLearning() { wx.switchTab({ url: '/pages/student/learning/index' }) },
  goResources() { wx.navigateTo({ url: '/pages/student/resources/index' }) },
  goHome() {
    const role = this.data.userInfo.role
    if (role === 'teacher' || role === 'admin') wx.reLaunch({ url: role === 'teacher' ? '/pages/teacher/list/index' : '/pages/admin/permission/index' })
    else wx.switchTab({ url: '/pages/student/hall/index' })
  },

  goEditProfile() {
    wx.navigateTo({
      url: "/pages/user/profile/index?edit=1"
    })
  },

  certifyTeacher() { this.setNavHidden(true); this.setData({ certOpen: true, certCode: '', certError: '' }) },
  closeCertification() {
    if (this.data.certifying) return
    this.setData({ certOpen: false, certCode: '' })
    this.setNavHidden(false)
  },
  stopPropagation() {},
  onCertInput(e) { this.setData({ certCode: e.detail.value, certError: '' }) },
  async submitCertification() {
    if (this.data.certifying) return
    const teacherAuthCode = this.data.certCode.trim()
    if (!teacherAuthCode) { this.setData({ certError: '请填写教师认证码' }); return }
    this.setData({ certifying: true, certError: '' })
    try {
      const res = await request({ url: '/api/common/auth/select-role', method: 'POST', data: { target_role: 'teacher', teacher_auth_code: teacherAuthCode } })
      const app = getApp()
      const authData = res.data || {}
      const userKey = app.globalData.config.STORAGE_KEYS.LOGIN_USER
      const tokenKey = app.globalData.config.STORAGE_KEYS.AUTH_TOKEN
      const user = { ...(app.globalData.loginUser || wx.getStorageSync(userKey) || {}), ...this.data.userInfo, ...authData }
      app.globalData.loginUser = user
      app.globalData.authToken = authData.token || ''
      wx.setStorageSync(userKey, user)
      wx.setStorageSync(tokenKey, authData.token || '')
      this.setData({ userInfo: { ...this.data.userInfo, role: 'teacher' }, certOpen: false, certCode: '' })
      this.setNavHidden(false)
      wx.showToast({ title: '教师认证成功', icon: 'success' })
      wx.reLaunch({ url: '/pages/teacher/list/index' })
    } catch (error) {
      this.setData({ certError: error.message || '认证暂未完成，请稍后重试' })
    } finally { this.setData({ certifying: false }) }
  },

  handleLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出当前账号吗？',
      success: (res) => {
        if (res.confirm) {
          const app = getApp()
          const userKey = app.globalData.config.STORAGE_KEYS.LOGIN_USER
          const tokenKey = app.globalData.config.STORAGE_KEYS.AUTH_TOKEN
          app.globalData.loginUser = null
          app.globalData.authToken = ""
          wx.removeStorageSync(userKey)
          wx.removeStorageSync(tokenKey)
          wx.reLaunch({ url: "/pages/auth/login/index" })
        }
      }
    })
  }
})
