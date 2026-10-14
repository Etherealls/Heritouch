/**
 * 通用工具函数
 */

/** 日期格式化 */
export function formatTime(ts, fmt = 'YYYY-MM-DD HH:mm') {
  if (!ts) return ''
  const d = new Date(ts)
  const map = {
    YYYY: d.getFullYear(),
    MM: String(d.getMonth() + 1).padStart(2, '0'),
    DD: String(d.getDate()).padStart(2, '0'),
    HH: String(d.getHours()).padStart(2, '0'),
    mm: String(d.getMinutes()).padStart(2, '0'),
    ss: String(d.getSeconds()).padStart(2, '0')
  }
  return fmt.replace(/YYYY|MM|DD|HH|mm|ss/g, (k) => map[k])
}

/** 相对时间（刚刚 / x分钟前 / x天前） */
export function fromNow(ts) {
  const diff = Date.now() - new Date(ts).getTime()
  if (diff < 60 * 1000) return '刚刚'
  if (diff < 3600 * 1000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 24 * 3600 * 1000) return Math.floor(diff / 3600000) + '小时前'
  if (diff < 30 * 24 * 3600 * 1000) return Math.floor(diff / 86400000) + '天前'
  return formatTime(ts, 'YYYY-MM-DD')
}

/** 生成唯一 ID */
export function uid() {
  return 'id_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

/** 数组乱序（抽题用） */
export function shuffle(arr) {
  const a = arr.slice()
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

/** 深拷贝 */
export function clone(obj) {
  return JSON.parse(JSON.stringify(obj))
}

/** 保存图片到相册（兼容 APP / 小程序 / H5 降级） */
export function saveImageToAlbum(url) {
  return new Promise((resolve, reject) => {
    // #ifdef H5
    uni.showToast({ title: 'H5 端请长按图片保存', icon: 'none' })
    reject(new Error('h5 not supported'))
    // #endif
    // #ifndef H5
    uni.downloadFile({
      url,
      success(res) {
        if (res.statusCode !== 200) return reject(new Error('下载失败'))
        uni.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: () => {
            uni.showToast({ title: '已保存到相册', icon: 'success' })
            resolve()
          },
          fail: reject
        })
      },
      fail: reject
    })
    // #endif
  })
}

/** 分享（小程序端复用原生分享，APP/H5 用 uni.share 或复制链接） */
export function shareText(title, summary) {
  // #ifdef MP-WEIXIN
  // 小程序分享由 onShareAppMessage 生命周期处理，此处仅提示
  uni.showShareMenu({ withShareTicket: true })
  // #endif
  // #ifndef MP-WEIXIN
  uni.setClipboardData({
    data: `【${title}】${summary || ''} —— 来自 指尖非遗App`,
    success: () => uni.showToast({ title: '链接已复制，可分享给好友', icon: 'none' })
  })
  // #endif
}
