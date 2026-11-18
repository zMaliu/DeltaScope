const { request } = require("../../../utils/api")
const { formatDate } = require('../../../utils/date')

Page({
  data: { kind: "post", detail: null, detailAuthor: "", detailAvatar: '观', channelLabel: '', dateText: '', loading: true, loadError: "" },
  onLoad(options) {
    this.setData({ kind: options.kind === "resource" ? "resource" : "post" })
    this._id = options.id
    this.loadDetail(options.id)
  },
  async loadDetail(id) {
    this.setData({ loading: true, loadError: '' })
    const isResource = this.data.kind === "resource"
    const path = isResource ? `/api/student/resources/${id}` : `/api/student/forum/post/${id}`
    try {
      const res = await request({ url: path })
      const detail = res.data || null
      const author = detail && detail.author_name ? detail.author_name : detail && detail.author_id ? `同学 ${detail.author_id}` : '观微元'
      const channels = { qa: '提问答疑', share: '经验分享', checkin: '学习打卡', mentor: '师生指导' }
      this.setData({ detail, detailAuthor: author, detailAvatar: author.slice(0, 1), channelLabel: detail ? detail.course || channels[detail.channel] || '课程资料' : '', dateText: detail && detail.created_at ? formatDate(detail.created_at) : '观微元资料库' })
    } catch (error) {
      this.setData({ loadError: error.message || "内容暂时无法加载" })
    } finally { this.setData({ loading: false }) }
  },
  retry() { this.loadDetail(this._id) },
  compose() { wx.navigateTo({ url: '/pages/student/compose/index' }) },
  backToFeed() { wx.navigateBack() }
})
