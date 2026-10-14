/**
 * 用户状态 Store：登录态、资料、收藏、积分
 * 数据持久化于 uni.storage（离线可用）
 */
import { defineStore } from 'pinia'
import config from '@/utils/config'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    userInfo: {},
    favorites: []
  }),
  getters: {
    isLogin: (state) => !!state.token,
    nickname: (state) => state.userInfo.nickname || state.userInfo.username || '未登录',
    username: (state) => state.userInfo.username || '',
    avatar: (state) => state.userInfo.avatar || '',
    totalScore: (state) => state.userInfo.score || 0
  },
  actions: {
    /* 从本地存储恢复登录态（App 启动时调用） */
    restore() {
      this.token = uni.getStorageSync(config.storageKeys.token) || ''
      this.userInfo = uni.getStorageSync(config.storageKeys.userInfo) || {}
      this.favorites = uni.getStorageSync(config.storageKeys.favorites) || []
    },
    /* 登录成功后写入 */
    setUser(user) {
      this.token = user.token || ''
      this.userInfo = { ...user }
      delete this.userInfo.token
      uni.setStorageSync(config.storageKeys.token, this.token)
      uni.setStorageSync(config.storageKeys.userInfo, this.userInfo)
    },
    updateProfile(payload) {
      this.userInfo = { ...this.userInfo, ...payload }
      uni.setStorageSync(config.storageKeys.userInfo, this.userInfo)
    },
    addScore(score) {
      this.userInfo.score = (this.userInfo.score || 0) + score
      uni.setStorageSync(config.storageKeys.userInfo, this.userInfo)
    },
    setFavorites(list) {
      this.favorites = list
      uni.setStorageSync(config.storageKeys.favorites, list)
    },
    logout() {
      this.token = ''
      this.userInfo = {}
      this.favorites = []
      uni.removeStorageSync(config.storageKeys.token)
      uni.removeStorageSync(config.storageKeys.userInfo)
    }
  }
})
