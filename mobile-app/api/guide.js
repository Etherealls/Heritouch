/**
 * 多模态智能导览 API（语音讲解 / 智能问答 / 扫码解析，全部走真实后端）
 */
import { http } from '@/utils/request'

/* 获取讲解音频：GET /audio/guide/{projectId}?lang=mandarin|dialect */
export async function getGuideAudio(projectId, lang = 'mandarin') {
  return http.get(`/audio/guide/${projectId}`, { lang })
}

/* 智能问答：POST /audio/qa（RAG 检索 + 大模型组织答案 + TTS） */
export async function askQuestion(question) {
  return http.post('/audio/qa', { question })
}

/* 扫码内容解析：POST /guide/scan-resolve
   二维码格式约定：heritouch://project?id=1 或 https://host/p?id=1 */
export async function scanResolve(code) {
  return http.post('/guide/scan-resolve', { code })
}

/* 离线缓存：下载核心讲解音频与基础数据 */
export async function downloadOfflinePack() {
  return http.post('/guide/offline-pack')
}

export async function getOfflinePack() {
  return uni.getStorageSync('heritouch_offline_cache') || null
}

export default { getGuideAudio, askQuestion, scanResolve, downloadOfflinePack, getOfflinePack }
