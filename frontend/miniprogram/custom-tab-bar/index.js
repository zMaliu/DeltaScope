Component({
  data: { active: 'home', hidden: false },
  lifetimes: { attached() { this.syncTab() } },
  pageLifetimes: { show() { this.syncTab() } },
  methods: {
    syncTab() {
      const pages = getCurrentPages()
      const route = pages.length ? pages[pages.length - 1].route : ''
      const tabs = { 'pages/student/hall/index': 'home', 'pages/student/learning/index': 'learning', 'pages/student/forum/index': 'community', 'pages/user/info/index': 'me' }
      this.setData({ active: tabs[route] || 'home' })
    }
  }
})
