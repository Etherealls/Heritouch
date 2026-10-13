/**
 * 多模态智能导览 API（语音讲解 / 智能问答 / 扫码解析）
 */
import config from '@/utils/config'
import { http, mockDelay } from '@/utils/request'
import mock from '@/api/mock/data'

/* 获取讲解音频：GET /audio/guide/{projectId}?lang=mandarin|dialect */
export async function getGuideAudio(projectId, lang = 'mandarin') {
  if (config.useMock) {
    await mockDelay(200)
    const project = mock.projects.find((p) => p.id === Number(projectId))
    const url = lang === 'dialect' ? project?.audio_dialect : project?.audio_mandarin
    return {
      url: url || '',
      text: project ? project.intro : '',
      duration: project ? 60 + (project.id % 5) * 10 : 60
    }
  }
  return http.get(`/audio/guide/${projectId}`, { lang })
}

/* 智能问答：POST /audio/qa（RAG 检索 + 大模型组织答案 + TTS） */
export async function askQuestion(question) {
  if (config.useMock) {
    await mockDelay(1500)
    const hit = mock.qaAnswers.find((item) => item.keywords.some((k) => question.includes(k)))
    if (hit) {
      return { answer: hit.answer, audio: hit.audio, question }
    }
    return {
      answer: `关于「${question}」，扬州非遗知识库中暂未收录完全匹配的条目。你可以试着询问扬州剪纸、扬州玉雕、扬州漆器、扬州早茶等主题，我会基于知识库为你解答。`,
      audio: '',
      question
    }
  }
  return http.post('/audio/qa', { question })
}

/* 扫码内容解析：POST /guide/scan-resolve
   二维码格式约定：heritouch://project?id=1 或 https://host/p?id=1 */
export async function scanResolve(code) {
  if (config.useMock) {
    await mockDelay(300)
    const m = code.match(/[?&]id=(\d+)/)
    if (!m) throw new Error('无效的非遗二维码')
    const project = mock.projects.find((p) => p.id === Number(m[1]))
    if (!project) throw new Error('未找到对应非遗项目')
    return { projectId: project.id, name: project.name }
  }
  return http.post('/guide/scan-resolve', { code })
}

/* 离线缓存：下载核心讲解音频与基础数据 */
export async function downloadOfflinePack() {
  if (config.useMock) {
    await mockDelay(2000)
    const pack = {
      version: '1.0.0',
      download_time: Date.now(),
      projects: mock.projects.map((p) => ({ id: p.id, name: p.name, intro: p.intro, audio: p.audio_mandarin })),
      size: '12.6MB'
    }
    uni.setStorageSync(config.storageKeys.offlineCache, pack)
    return pack
  }
  return http.post('/guide/offline-pack')
}

export async function getOfflinePack() {
  return uni.getStorageSync(config.storageKeys.offlineCache) || null
}

export default { getGuideAudio, askQuestion, scanResolve, downloadOfflinePack, getOfflinePack }
