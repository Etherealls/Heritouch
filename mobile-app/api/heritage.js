/**
 * 非遗内容 / 知识图谱 API（全部走真实后端）
 */
import { http } from '@/utils/request'

/* 获取非遗分类列表：GET /heritage/categories */
export async function getCategories() {
  return http.get('/heritage/categories')
}

/* 非遗项目检索列表：GET /heritage?category&level&region&keyword&page&size */
export async function getProjectList(params = {}) {
  const { category = '', level = '', region = '', keyword = '', page = 1, size = 20 } = params
  return http.get('/heritage', { category, level, region, keyword, page, size })
}

/* 获取非遗项目详情：GET /heritage/{id} */
export async function getProjectDetail(id) {
  return http.get('/heritage/' + id)
}

/* 获取知识图谱数据：GET /knowledge-graph?category&region&depth */
export async function getKnowledgeGraph(params = {}) {
  const { category = '', region = '', depth = 2 } = params
  return http.get('/knowledge-graph', { category, region, depth })
}

/* 获取传承人详情：GET /heritage/inheritor/{id} */
export async function getInheritorDetail(id) {
  return http.get('/heritage/inheritor/' + id)
}

/* 智能关联推荐：GET /heritage/{id}/recommendations */
export async function getRecommendations(id) {
  return http.get('/heritage/' + id + '/recommendations')
}

export default { getCategories, getProjectList, getProjectDetail, getKnowledgeGraph, getInheritorDetail, getRecommendations }
