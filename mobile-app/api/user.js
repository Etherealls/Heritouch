/**
 * 用户 API（登录 / 信息 / 资料 / 收藏）
 */
import config from '@/utils/config'
import { http, mockDelay } from '@/utils/request'
import { useUserStore } from '@/store/user'

/* 登录 / 注册：POST /user/login（微信 openid 或设备唯一标识） */
export async function login(payload = {}) {
  const userStore = useUserStore()
  const openid = payload.openid || 'dev_' + Date.now().toString(36)
  if (config.useMock) {
    await mockDelay(600)
    const user = {
      id: 1,
      openid,
      nickname: payload.nickname || '非遗体验官',
      avatar: payload.avatar || '/static/images/avatar-default.jpg',
      score: 0,
      token: 'mock_token_' + Date.now()
    }
    userStore.setUser(user)
    return user
  }
  const user = await http.post('/user/login', { openid, nickname: payload.nickname, avatar: payload.avatar })
  userStore.setUser(user)
  return user
}

/* 获取用户信息：GET /user/info */
export async function getUserInfo() {
  if (config.useMock) {
    await mockDelay(200)
    return useUserStore().userInfo || {}
  }
  return http.get('/user/info')
}

/* 更新资料：PUT /user/profile */
export async function updateProfile(payload) {
  if (config.useMock) {
    await mockDelay(300)
    const userStore = useUserStore()
    userStore.updateProfile(payload)
    return userStore.userInfo
  }
  return http.put('/user/profile', payload)
}

/* 收藏 / 取消收藏：POST /user/favorite、DELETE /user/favorite/{id} */
export async function toggleFavorite(item) {
  const key = `${item.type}_${item.id}`
  const userStore = useUserStore()
  if (config.useMock) {
    await mockDelay(150)
    const favorites = uni.getStorageSync(config.storageKeys.favorites) || []
    const idx = favorites.findIndex((f) => `${f.type}_${f.id}` === key)
    if (idx === -1) {
      favorites.unshift({ ...item, fav_time: Date.now() })
      uni.setStorageSync(config.storageKeys.favorites, favorites)
      userStore.favorites = favorites
      return { favorited: true }
    }
    favorites.splice(idx, 1)
    uni.setStorageSync(config.storageKeys.favorites, favorites)
    userStore.favorites = favorites
    return { favorited: false }
  }
  if (item.favorited) {
    await http.del('/user/favorite/' + item.id)
    return { favorited: false }
  }
  await http.post('/user/favorite', item)
  return { favorited: true }
}

/* 获取收藏列表：GET /user/favorites */
export async function getFavorites() {
  if (config.useMock) {
    await mockDelay(150)
    return uni.getStorageSync(config.storageKeys.favorites) || []
  }
  return http.get('/user/favorites')
}

export default { login, getUserInfo, updateProfile, toggleFavorite, getFavorites }
