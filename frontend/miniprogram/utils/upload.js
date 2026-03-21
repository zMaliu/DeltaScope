function chooseAndCompressImages(count = 9) {
  return new Promise((resolve, reject) => {
    wx.chooseMedia({
      count,
      mediaType: ["image"],
      sourceType: ["album", "camera"],
      success: async (res) => {
        try {
          const files = res.tempFiles || []
          const compressed = []
          for (const item of files) {
            const data = await new Promise((ok, bad) => {
              wx.compressImage({
                src: item.tempFilePath,
                quality: 70,
                success: ok,
                fail: bad
              })
            })
            compressed.push(data.tempFilePath)
          }
          resolve(compressed)
        } catch (error) {
          reject(error)
        }
      },
      fail: reject
    })
  })
}

function uploadImage(filePath, uploadUrl) {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: uploadUrl,
      filePath,
      name: "file",
      success: (res) => {
        try {
          const data = JSON.parse(res.data || "{}")
          if (data.url) {
            resolve(data.url)
            return
          }
          reject(data)
        } catch (error) {
          reject(error)
        }
      },
      fail: reject
    })
  })
}

async function uploadImages(filePaths, uploadUrl) {
  const tasks = filePaths.map((item) => uploadImage(item, uploadUrl))
  return Promise.all(tasks)
}

module.exports = {
  chooseAndCompressImages,
  uploadImages
}
