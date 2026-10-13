/**
 * 全局配置：服务器地址 / Mock 开关 / 存储键名
 * 说明：学生实训与演示场景下默认开启 Mock（USE_MOCK=true），
 * 无需后端即可完整体验全部功能；接入真实后端后改为 false 并配置服务器地址。
 */
const config = {
  // 后端服务基础地址（FastAPI，见 server/ 目录）
  baseUrl: 'http://localhost:8000/api/v1',
  // Mock 开关：true = 使用本地模拟数据，false = 请求真实后端
  useMock: true,
  // 请求超时（ms）
  timeout: 30000,
  // 本地存储键
  storageKeys: {
    token: 'heritouch_token',
    userInfo: 'heritouch_user_info',
    favorites: 'heritouch_favorites',
    works: 'heritouch_works',
    wrongBook: 'heritouch_wrong_book',
    gameProgress: 'heritouch_game_progress',
    offlineCache: 'heritouch_offline_cache'
  }
}

// 允许从设置页动态覆盖（uni.storage 优先级最高）
try {
  const override = uni.getStorageSync('heritouch_server_config')
  if (override) Object.assign(config, JSON.parse(override))
} catch (e) {}

export default config
