/**
 * 全局 App 配置 Store：Mock 开关、服务器地址、扫码导览待处理项目
 */
import { defineStore } from 'pinia'
import config from '@/utils/config'

export const useAppStore = defineStore('app', {
  state: () => ({
    useMock: config.useMock,
    baseUrl: config.baseUrl,
    // 扫码解析成功后待跳转的项目 ID（扫码页 → 详情页）
    pendingScanProjectId: null
  }),
  actions: {
    setMock(val) {
      this.useMock = val
      uni.setStorageSync('heritouch_server_config', JSON.stringify({ useMock: val, baseUrl: this.baseUrl }))
    },
    setBaseUrl(url) {
      this.baseUrl = url
      config.baseUrl = url
      uni.setStorageSync('heritouch_server_config', JSON.stringify({ useMock: this.useMock, baseUrl: url }))
    },
    setPendingScan(id) {
      this.pendingScanProjectId = id
    }
  }
})
