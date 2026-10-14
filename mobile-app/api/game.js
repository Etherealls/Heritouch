/**
 * 非遗科普闯关 API（关卡 / 题目 / 判分 / 排行 / 错题，全部走真实后端）
 */
import { http } from '@/utils/request'

/* 获取关卡列表（含解锁状态）：GET /game/levels */
export async function getLevels() {
  return http.get('/game/levels')
}

/* 获取关卡题目（不含答案）：GET /game/questions/{levelId}?count=10 */
export async function getQuestions(levelId, count = 10) {
  return http.get(`/game/questions/${levelId}`, { count })
}

/* 提交单题答案：POST /game/submit */
export async function submitAnswer({ questionId, answer, levelId = 1 }) {
  return http.post('/game/submit', { questionId, answer })
}

/* 排行榜：GET /game/rank */
export async function getRankList() {
  return http.get('/game/rank')
}

/* 错题本：GET /game/wrong */
export async function getWrongBook() {
  return http.get('/game/wrong')
}

/* 移除错题（已掌握）：DELETE /game/wrong/{id} */
export async function removeWrong(id) {
  return http.del('/game/wrong/' + id)
}

export default { getLevels, getQuestions, submitAnswer, getRankList, getWrongBook, removeWrong }
