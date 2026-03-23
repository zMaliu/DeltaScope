const { request } = require("../../../utils/api")

Page({
  data: {
    nickname: "",
    avatarUrl: "",
    school: "",
    college: "",
    major: "",
    grade: "",
    className: "",
    realName: "",
    role: "student"
  },
  async onLoad(options) {
    const app = getApp()
    const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
    const user = app.globalData.loginUser || wx.getStorageSync(key) || null
    if (!user) {
      wx.reLaunch({ url: "/pages/auth/login/index" })
      return
    }
    this.setData({ role: user.role })
    try {
      const res = await request({ url: "/api/common/profile/me" })
      
      // 如果是从信息页主动点击修改过来的，options.edit 会为 '1'
      const isEdit = options.edit === '1'
      
      // 如果不是主动修改，且必要信息已经填过，则直接跳过此页面
      if (!isEdit) {
        const hasRequired = res.data.real_name && res.data.college && (user.role === 'teacher' || res.data.major)
        if (hasRequired) {
          if (user.role === "teacher") {
            wx.reLaunch({ url: "/pages/teacher/list/index" })
          } else {
            wx.reLaunch({ url: "/pages/student/hall/index" })
          }
          return
        }
      }

      this.setData({
        nickname: res.data.nickname || "",
        avatarUrl: res.data.avatar_url || "",
        school: res.data.school || "",
        college: res.data.college || "",
        major: res.data.major || "",
        grade: res.data.grade || "",
        className: res.data.class_name || "",
        realName: res.data.real_name || ""
      })
    } catch (error) {}
  },
  onNicknameInput(e) { this.setData({ nickname: e.detail.value }) },
  onAvatarInput(e) { this.setData({ avatarUrl: e.detail.value }) },
  onSchoolInput(e) { this.setData({ school: e.detail.value }) },
  onCollegeInput(e) { this.setData({ college: e.detail.value }) },
  onMajorInput(e) { this.setData({ major: e.detail.value }) },
  onGradeInput(e) { this.setData({ grade: e.detail.value }) },
  onClassNameInput(e) { this.setData({ className: e.detail.value }) },
  onRealNameInput(e) { this.setData({ realName: e.detail.value }) },
  
  async saveProfile() {
    if (!this.data.realName || !this.data.college) {
      wx.showToast({ title: "真实姓名和学院为必填项", icon: "none" })
      return
    }
    if (this.data.role === "student" && !this.data.major) {
      wx.showToast({ title: "学生必须填写专业", icon: "none" })
      return
    }
    try {
      const res = await request({
        url: "/api/common/profile/update",
        method: "POST",
        data: {
          nickname: this.data.nickname,
          avatar_url: this.data.avatarUrl,
          school: this.data.school,
          college: this.data.college,
          major: this.data.major,
          grade: this.data.grade,
          class_name: this.data.className,
          real_name: this.data.realName
        }
      })
      const app = getApp()
      const key = app.globalData.config.STORAGE_KEYS.LOGIN_USER
      const user = app.globalData.loginUser || wx.getStorageSync(key) || {}
      const merged = { ...user, nickname: res.data.nickname, real_name: res.data.real_name }
      app.globalData.loginUser = merged
      wx.setStorageSync(key, merged)
      
      wx.showToast({ title: "保存成功", icon: "success" })
      setTimeout(() => {
        const pages = getCurrentPages()
        if (pages.length > 1) {
          wx.navigateBack()
        } else {
          if (this.data.role === "teacher") {
            wx.reLaunch({ url: "/pages/teacher/list/index" })
          } else {
            wx.reLaunch({ url: "/pages/student/hall/index" })
          }
        }
      }, 1000)
    } catch (error) {
      wx.showToast({ title: error.message || "保存失败", icon: "none" })
    }
  }
})
