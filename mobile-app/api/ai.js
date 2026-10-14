/**
 * AI 互动创作 API（纹样 / 剧本 / 画作 + 作品管理，全部走真实后端）
 */
import { http } from '@/utils/request'

/* 生成非遗纹样：POST /ai/generate-pattern */
export async function generatePattern({ prompt, style, size = '1024x1024' }) {
  return http.post('/ai/generate-pattern', { prompt, style, size })
}

/* 生成科普剧本：POST /ai/generate-script */
export async function generateScript({ theme, duration = 60, dialect = false, roleCount = 3 }) {
  return http.post('/ai/generate-script', { theme, duration, dialect, roleCount })
}

/* 生成非遗风格画作：POST /ai/generate-painting（文生图 / 图生图） */
export async function generatePainting({ mode = 'text', prompt, style = '漆画', image = '' }) {
  return http.post('/ai/generate-painting', { mode, prompt, style, image })
}

/* 保存作品到“我的作品”：POST /ai/works */
export async function saveWork(work) {
  return http.post('/ai/works', work)
}

/* 获取我的作品：GET /ai/works */
export async function getWorks() {
  return http.get('/ai/works')
}

/* 删除作品：DELETE /ai/works/{id} */
export async function deleteWork(id) {
  return http.del('/ai/works/' + id)
}

export default { generatePattern, generateScript, generatePainting, saveWork, getWorks, deleteWork }
