/**
 * 非遗科普闯关 API（关卡 / 题目 / 判分 / 排行 / 错题）
 */
import config from '@/utils/config'
import { http, mockDelay } from '@/utils/request'
import { shuffle } from '@/utils/util'
import mock from '@/api/mock/data'

/* 获取关卡列表（含解锁状态）：GET /game/levels */
export async function getLevels() {
  if (config.useMock) {
    await mockDelay(200)
    const progress = uni.getStorageSync(config.storageKeys.gameProgress) || {}
    const totalScore = Object.values(progress).reduce((sum, p) => sum + (p.bestScore || 0), 0)
    return mock.gameLevels.map((lv) => ({
      ...lv,
      unlocked: totalScore >= lv.need_score,
      bestScore: progress[lv.id]?.bestScore || 0,
      passed: (progress[lv.id]?.bestScore || 0) >= 60
    }))
  }
  return http.get('/game/levels')
}

/* 获取关卡题目（不含答案）：GET /game/questions/{levelId}?count=10 */
export async function getQuestions(levelId, count = 10) {
  if (config.useMock) {
    await mockDelay(400)
    const list = shuffle(mock.questions.filter((q) => q.level_id === Number(levelId))).slice(0, count)
    return list.map((q) => {
      const { answer, analysis, ...rest } = q
      return rest // 不将答案下发到前端
    })
  }
  return http.get(`/game/questions/${levelId}`, { count })
}

/* 提交单题答案：POST /game/submit */
export async function submitAnswer({ questionId, answer, levelId = 1 }) {
  if (config.useMock) {
    await mockDelay(150)
    const q = mock.questions.find((item) => item.id === Number(questionId))
    const correct = q && q.answer === answer
    const score = correct ? (q.difficulty === 1 ? 10 : q.difficulty === 2 ? 15 : 20) : 0
    // 本地记录错题
    const wrongBook = uni.getStorageSync(config.storageKeys.wrongBook) || []
    if (!correct && q) {
      const idx = wrongBook.findIndex((w) => w.id === q.id)
      if (idx === -1) {
        const { answer: ans, ...rest } = q
        wrongBook.unshift({ ...rest, answer: ans, wrong_count: 1, last_wrong_time: Date.now() })
      } else {
        wrongBook[idx].wrong_count += 1
        wrongBook[idx].last_wrong_time = Date.now()
      }
      uni.setStorageSync(config.storageKeys.wrongBook, wrongBook)
    }
    return {
      correct: !!correct,
      answer: q ? q.answer : '',
      analysis: q ? q.analysis : '',
      score,
      difficulty: q ? q.difficulty : 1
    }
  }
  return http.post('/game/submit', { questionId, answer })
}

/* 通关结算（本地累计）：记录本关成绩 */
export function recordLevelResult(levelId, score, total) {
  const progress = uni.getStorageSync(config.storageKeys.gameProgress) || {}
  const prev = progress[levelId] || { bestScore: 0, passCount: 0 }
  progress[levelId] = {
    bestScore: Math.max(prev.bestScore, score),
    passCount: score >= 60 ? prev.passCount + 1 : prev.passCount,
    lastScore: score,
    lastTotal: total,
    lastTime: Date.now()
  }
  uni.setStorageSync(config.storageKeys.gameProgress, progress)
  return progress[levelId]
}

/* 排行榜：GET /game/rank */
export async function getRankList() {
  if (config.useMock) {
    await mockDelay(300)
    const progress = uni.getStorageSync(config.storageKeys.gameProgress) || {}
    const myScore = Object.values(progress).reduce((sum, p) => sum + (p.bestScore || 0), 0)
    const others = [
      { rank: 1, nickname: '非遗小达人', avatar: '/static/images/avatar-1.jpg', score: 980 },
      { rank: 2, nickname: '扬州小秀才', avatar: '/static/images/avatar-2.jpg', score: 860 },
      { rank: 3, nickname: '剪纸小传人', avatar: '/static/images/avatar-3.jpg', score: 720 },
      { rank: 4, nickname: '玉雕学徒', avatar: '/static/images/avatar-4.jpg', score: 610 },
      { rank: 5, nickname: '早茶常客', avatar: '/static/images/avatar-5.jpg', score: 480 }
    ]
    const list = others.concat([{ rank: 0, nickname: '我', avatar: '', score: myScore, me: true }])
    list.sort((a, b) => b.score - a.score)
    return list.map((item, i) => ({ ...item, rank: i + 1 }))
  }
  return http.get('/game/rank')
}

/* 错题本：GET /game/wrong */
export async function getWrongBook() {
  if (config.useMock) {
    await mockDelay(150)
    return uni.getStorageSync(config.storageKeys.wrongBook) || []
  }
  return http.get('/game/wrong')
}

/* 移除错题（已掌握）：DELETE /game/wrong/{id} */
export async function removeWrong(id) {
  if (config.useMock) {
    await mockDelay(150)
    const wrongBook = (uni.getStorageSync(config.storageKeys.wrongBook) || []).filter((w) => w.id !== id)
    uni.setStorageSync(config.storageKeys.wrongBook, wrongBook)
    return { id }
  }
  return http.del('/game/wrong/' + id)
}

export default { getLevels, getQuestions, submitAnswer, recordLevelResult, getRankList, getWrongBook, removeWrong }
