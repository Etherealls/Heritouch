/**
 * AI 互动创作 API（纹样 / 剧本 / 画作 + 作品管理）
 * 说明：真实模式下由后端调用 AI 模型服务（见 server/app/services/ai_service.py）；
 *       Mock 模式下本地生成演示结果，保证无后端可完整体验。
 */
import config from '@/utils/config'
import { http, mockDelay } from '@/utils/request'
import { uid } from '@/utils/util'

/* 生成非遗纹样：POST /ai/generate-pattern */
export async function generatePattern({ prompt, style, size = '1024x1024' }) {
  if (config.useMock) {
    await mockDelay(2000)
    return {
      task_id: 'task_' + Date.now(),
      image_url: '/static/images/gen-pattern-' + ((Date.now() % 3) + 1) + '.jpg',
      style,
      prompt,
      ai_created: true
    }
  }
  return http.post('/ai/generate-pattern', { prompt, style, size })
}

/* 生成科普剧本：POST /ai/generate-script */
export async function generateScript({ theme, duration = 60, dialect = false, roleCount = 3 }) {
  if (config.useMock) {
    await mockDelay(2500)
    const script = {
      theme,
      duration,
      dialect,
      scenes: [
        { scene: 1, title: '开场·溯源', content: `【旁白】扬州非遗，千年文脉。今天我们要讲的是「${theme}」的故事。${dialect ? '（本幕使用扬州方言演绎）' : ''}`, roles: ['旁白'] },
        { scene: 2, title: '传承·技艺', content: `【老师傅】这门手艺讲究的是心到、眼到、手到，一板一眼都马虎不得。\n【徒弟】师父，这第一步该从哪里下手？\n【老师傅】莫急，先把心静下来。`, roles: ['老师傅', '徒弟'] },
        { scene: 3, title: '焕新·传承', content: `【青年】老手艺也能有新玩法，我们用短视频让更多年轻人看见它。\n【老师傅】好啊，传承不守旧，创新不忘本。`, roles: ['青年', '老师傅'] }
      ],
      roles: ['旁白', '老师傅', '徒弟', '青年'].slice(0, roleCount),
      ai_created: true
    }
    return script
  }
  return http.post('/ai/generate-script', { theme, duration, dialect, roleCount })
}

/* 生成非遗风格画作：POST /ai/generate-painting（文生图 / 图生图） */
export async function generatePainting({ mode = 'text', prompt, style = '漆画', image = '' }) {
  if (config.useMock) {
    await mockDelay(3000)
    return {
      task_id: 'task_' + Date.now(),
      image_url: '/static/images/gen-painting-' + ((Date.now() % 3) + 1) + '.jpg',
      style,
      prompt,
      mode,
      ai_created: true
    }
  }
  return http.post('/ai/generate-painting', { mode, prompt, style, image })
}

/* 保存作品到“我的作品”：POST /ai/works（Mock 模式存本地） */
export async function saveWork(work) {
  const record = Object.assign({ id: uid(), create_time: Date.now(), ai_created: true }, work)
  if (config.useMock) {
    await mockDelay(150)
    const works = uni.getStorageSync(config.storageKeys.works) || []
    works.unshift(record)
    uni.setStorageSync(config.storageKeys.works, works)
    return record
  }
  return http.post('/ai/works', record)
}

/* 获取我的作品：GET /ai/works */
export async function getWorks() {
  if (config.useMock) {
    await mockDelay(150)
    return uni.getStorageSync(config.storageKeys.works) || []
  }
  return http.get('/ai/works')
}

/* 删除作品：DELETE /ai/works/{id} */
export async function deleteWork(id) {
  if (config.useMock) {
    await mockDelay(150)
    const works = (uni.getStorageSync(config.storageKeys.works) || []).filter((w) => w.id !== id)
    uni.setStorageSync(config.storageKeys.works, works)
    return { id }
  }
  return http.del('/ai/works/' + id)
}

export default { generatePattern, generateScript, generatePainting, saveWork, getWorks, deleteWork }
