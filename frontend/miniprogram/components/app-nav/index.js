Component({
  properties: { active: { type: String, value: 'home' } },
  data: { items: [] },
  lifetimes: { attached() { this.updateItems() } },
  pageLifetimes: { show() { this.updateItems() } },
  methods: {
    updateItems() {
      const app = getApp()
      const user = app.globalData.loginUser || wx.getStorageSync(app.globalData.config.STORAGE_KEYS.LOGIN_USER) || {}
      const items = user.role === 'teacher' ? [
        { key: 'home', label: '工作台', icon: 'home', url: '/pages/teacher/list/index' },
        { key: 'publish', label: '发布题目', icon: 'plus', url: '/pages/teacher/publish/index' },
        { key: 'me', label: '我的', icon: 'me', url: '/pages/user/info/index' }
      ] : user.role === 'admin' ? [
        { key: 'home', label: '权限管理', icon: 'home', url: '/pages/admin/permission/index' },
        { key: 'me', label: '我的', icon: 'me', url: '/pages/user/info/index' }
      ] : [
        { key: 'home', label: '发现', icon: 'home', url: '/pages/student/hall/index' },
        { key: 'learning', label: '学习', icon: 'book', url: '/pages/student/learning/index' },
        { key: 'publish', label: '发布', icon: 'plus', url: '/pages/student/compose/index' },
        { key: 'community', label: '社区', icon: 'community', url: '/pages/student/forum/index' },
        { key: 'me', label: '我的', icon: 'me', url: '/pages/user/info/index' }
      ]
      this.setData({ items })
    },
    go(e) {
      const item = this.data.items.find(item => item.key === e.currentTarget.dataset.key)
      if (!item || item.key === this.data.active) return
      if (item.key === 'publish') { wx.navigateTo({ url: item.url }); return }
      const tabs = ['/pages/student/hall/index', '/pages/student/learning/index', '/pages/student/forum/index', '/pages/user/info/index']
      if (tabs.includes(item.url)) wx.switchTab({ url: item.url })
      else wx.reLaunch({ url: item.url })
    }
  }
})
