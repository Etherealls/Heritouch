/**
 * 用户 API（注册 / 登录 / 信息 / 资料 / 密码 / 收藏，全部走真实后端）
 */
import { http } from '@/utils/request'
import { useUserStore } from '@/store/user'

/* 注册：POST /user/register（用户名 + 密码） */
export async function register(payload) {
  const user = await http.post('/user/register', {
    username: payload.username,
    password: payload.password,
    nickname: payload.nickname || '',
    avatar: payload.avatar || ''
  })
  useUserStore().setUser(user)
  return user
}

/* 登录：POST /user/login（用户名 + 密码） */
export async function login(payload) {
  const user = await http.post('/user/login', {
    username: payload.username,
    password: payload.password
  })
  useUserStore().setUser(user)
  return user
}

/* 获取用户信息：GET /user/info */
export async function getUserInfo() {
  return http.get('/user/info')
}

/* 更新资料：PUT /user/profile */
export async function updateProfile(payload) {
  const user = await http.put('/user/profile', payload)
  useUserStore().updateProfile(user)
  return user
}

/* 修改密码：PUT /user/password */
export async function updatePassword(oldPassword, newPassword) {
  return http.put('/user/password', { old_password: oldPassword, new_password: newPassword })
}

/* 收藏 / 取消收藏：POST /user/favorite、DELETE /user/favorite/{id} */
export async function toggleFavorite(item) {
  if (item.favorited) {
    await http.del('/user/favorite/' + item.id)
    return { favorited: false }
  }
  await http.post('/user/favorite', item)
  return { favorited: true }
}

/* 获取收藏列表：GET /user/favorites */
export async function getFavorites() {
  return http.get('/user/favorites')
}

export default { register, login, getUserInfo, updateProfile, updatePassword, toggleFavorite, getFavorites }
