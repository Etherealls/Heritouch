/**
 * 基于 uni.request 的 HTTP 封装
 * - 统一 baseURL / 超时 / 错误提示
 * - 自动携带 Authorization Token
 * - Promise 化，支持 GET/POST/PUT/DELETE
 */
import config from './config'

function request(options) {
  const { url, method = 'GET', data = {}, header = {} } = options
  const token = uni.getStorageSync(config.storageKeys.token) || ''
  // 每次请求实时读取最新服务器地址（设置页修改后无需重启即生效）
  const baseUrl = config.baseUrl
  return new Promise((resolve, reject) => {
    uni.request({
      url: baseUrl + url,
      method,
      data,
      timeout: config.timeout,
      header: Object.assign(
        {
          'Content-Type': 'application/json',
          Authorization: token ? 'Bearer ' + token : ''
        },
        header
      ),
      success(res) {
        const body = res.data || {}
        if (res.statusCode >= 200 && res.statusCode < 300 && (body.code === 0 || body.code === undefined || body.code === 200)) {
          resolve(body.data !== undefined ? body.data : body)
        } else {
          const msg = body.message || body.msg || `请求失败(${res.statusCode})`
          uni.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
        }
      },
      fail(err) {
        uni.showToast({ title: '网络异常，请检查服务器地址', icon: 'none' })
        reject(err)
      }
    })
  })
}

export const http = {
  get: (url, data) => request({ url, method: 'GET', data }),
  post: (url, data) => request({ url, method: 'POST', data }),
  put: (url, data) => request({ url, method: 'PUT', data }),
  del: (url, data) => request({ url, method: 'DELETE', data })
}

/** 模拟网络延迟（Mock 模式下使用） */
export function mockDelay(ms = 350) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export default request
