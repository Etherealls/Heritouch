/**
 * 全局配置：服务器地址 / 存储键名
 *
 * 设计要点（局域网真机调试关键）：
 * - 服务器地址（baseUrl）支持在「我的-设置」页动态修改，写入本地存储
 *   heritouch_server_config；通过 getter 每次读取时实时从存储取最新值，
 *   无需重启 App 即可生效（解决手机换网络后 IP 变化需重新打包的问题）；
 * - 所有数据均来自真实后端，无演示/Mock 模式。
 */

// 本地存储键（服务器配置与业务数据共用一套键名）
const STORAGE_SERVER_CONFIG = 'heritouch_server_config'

const storageKeys = {
  token: 'heritouch_token',
  userInfo: 'heritouch_user_info',
  favorites: 'heritouch_favorites',
  works: 'heritouch_works',
  wrongBook: 'heritouch_wrong_book',
  gameProgress: 'heritouch_game_progress',
  offlineCache: 'heritouch_offline_cache'
}

// 默认配置（未在设置页修改时的兜底）
const DEFAULTS = {
  baseUrl: 'http://localhost:8000/api/v1',
  timeout: 30000
}

/** 从本地存储读取用户覆盖的服务器配置（可能为 null） */
function readOverride() {
  try {
    const raw = uni.getStorageSync(STORAGE_SERVER_CONFIG)
    if (raw) {
      const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw
      if (parsed && typeof parsed === 'object') return parsed
    }
  } catch (e) {
    // 存储内容损坏时忽略，回退默认值
  }
  return null
}

/** 写回本地存储（设置页调用） */
export function saveServerConfig(partial) {
  const merged = Object.assign({}, readOverride() || {}, partial)
  try {
    uni.setStorageSync(STORAGE_SERVER_CONFIG, JSON.stringify(merged))
  } catch (e) {}
  return merged
}

/**
 * 全局配置对象：baseUrl 通过 getter 动态读取本地存储，
 * 保证设置页修改后所有 API 层（request.js）下一次请求立即使用新地址。
 */
const config = {
  get baseUrl() {
    const override = readOverride()
    return (override && override.baseUrl) || DEFAULTS.baseUrl
  },
  set baseUrl(url) {
    saveServerConfig({ baseUrl: url })
  },
  timeout: DEFAULTS.timeout,
  storageKeys,
  STORAGE_SERVER_CONFIG,
  DEFAULTS
}

export default config
