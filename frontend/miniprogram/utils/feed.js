const CHANNELS = { qa: '提问答疑', checkin: '学习打卡', share: '经验分享', mentor: '师生指导' }
const ART = ['curves', 'geometry', 'orbit', 'waves']
function postCard(post, index = 0) {
  const author = post.author_name || (post.author_id ? `同学 ${post.author_id}` : '观微元')
  return {
    id: `post-${post.id}`, kind: 'post', sourceId: post.id, title: post.title, summary: post.content,
    label: post.course || CHANNELS[post.channel] || '学习社区', author, avatar: author.slice(0, 1),
    meta: post.author_id ? `${post.reply_count || 0} 讨论` : '示例内容',
    cover: `/assets/covers/${ART[index % ART.length]}.png`, tall: index % 3 === 1,
    coverTitle: post.channel === 'qa' ? '每个好问题\n都值得被看见' : post.channel === 'checkin' ? '一点一滴\n让进步发生' : '在思考中\n发现新的连接'
  }
}
function resourceCard(resource, index = 0) {
  return {
    id: `resource-${resource.id}`, kind: 'resource', sourceId: resource.id, title: resource.title, summary: resource.summary,
    label: resource.course || '课程资料', author: '观微元资料库', avatar: '观', meta: resource.status === 'published' ? '资料' : '筹备中',
    cover: `/assets/covers/${ART[(index + 1) % ART.length]}.png`, tall: index % 3 === 0,
    coverTitle: resource.course || '让知识\n有迹可循', status: resource.status
  }
}
function columns(items) {
  const result = [[], []]
  const heights = [0, 0]
  items.forEach(item => {
    const target = heights[0] <= heights[1] ? 0 : 1
    result[target].push(item)
    heights[target] += (item.tall ? 310 : 260) + 150 + Math.min((item.title || '').length, 30) * 2
  })
  return result
}
function matches(card, keyword) { return !keyword || [card.title, card.summary, card.label].join(' ').toLowerCase().includes(keyword.trim().toLowerCase()) }
function openCard(card) {
  if (card.url) { wx.navigateTo({ url: card.url }); return }
  wx.navigateTo({ url: `/pages/student/note/index?kind=${card.kind}&id=${card.sourceId}` })
}
module.exports = { postCard, resourceCard, columns, matches, openCard }
