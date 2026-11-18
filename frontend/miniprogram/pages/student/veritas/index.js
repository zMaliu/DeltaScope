Page({
  data: {
    abilities: [
      {
        title: "对话式证明辅导",
        desc: "从一个问题开始，逐步拆解定理、条件和证明思路。"
      },
      {
        title: "证明题自动批改",
        desc: "帮助发现推导中遗漏的条件与逻辑断点，保留自己的思考。"
      },
      {
        title: "薄弱点诊断",
        desc: "结合学习记录，给下一次复习一个更清晰的方向。"
      }
    ],
    principles: [
      "先做少量课程场景的可信 MVP，再逐步扩大题型覆盖。",
      "所有 AI 结论都应保留依据、限制与人工复核入口。",
      "Veritas 不替代思考，只帮助学生看清推导链条。"
    ]
  },
  goWeekly() {
    wx.switchTab({ url: '/pages/student/hall/index' })
  }
})
