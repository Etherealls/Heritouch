/**
 * 非遗内容 / 知识图谱 API
 */
import config from '@/utils/config'
import { http, mockDelay } from '@/utils/request'
import mock from '@/api/mock/data'

/* 获取非遗分类列表：GET /heritage/categories */
export async function getCategories() {
  if (config.useMock) {
    await mockDelay()
    return mock.categories
  }
  return http.get('/heritage/categories')
}

/* 非遗项目检索列表：GET /heritage?category&level&region&keyword&page&size */
export async function getProjectList(params = {}) {
  const { category = '', level = '', region = '', keyword = '', page = 1, size = 20 } = params
  if (config.useMock) {
    await mockDelay()
    let list = mock.projects.slice()
    if (category) list = list.filter((p) => p.category === category)
    if (level) list = list.filter((p) => p.level === level)
    if (region) list = list.filter((p) => p.region.includes(region))
    if (keyword) list = list.filter((p) => p.name.includes(keyword) || p.intro.includes(keyword) || p.tags.some((t) => t.includes(keyword)))
    const start = (page - 1) * size
    return { total: list.length, list: list.slice(start, start + size) }
  }
  return http.get('/heritage', { category, level, region, keyword, page, size })
}

/* 获取非遗项目详情：GET /heritage/{id} */
export async function getProjectDetail(id) {
  if (config.useMock) {
    await mockDelay()
    const project = mock.projects.find((p) => p.id === Number(id))
    if (!project) throw new Error('项目不存在')
    const inheritors = mock.inheritors.filter((i) => project.inheritors.includes(i.id))
    return Object.assign({}, project, { inheritor_list: inheritors })
  }
  return http.get('/heritage/' + id)
}

/* 获取知识图谱数据：GET /knowledge-graph?category&region&depth */
export async function getKnowledgeGraph(params = {}) {
  const { category = '', region = '', depth = 2 } = params
  if (config.useMock) {
    await mockDelay(500)
    let nodes = mock.graphData.nodes.slice()
    let edges = mock.graphData.edges.slice()
    if (category) {
      const keep = new Set()
      edges = edges.filter((e) => {
        if (e.label === '归属' && nodes.find((n) => n.id === e.source && n.name === category)) {
          keep.add(e.source); keep.add(e.target); return true
        }
        return keep.has(e.source) || keep.has(e.target)
      })
      const ids = new Set(edges.flatMap((e) => [e.source, e.target]))
      nodes = nodes.filter((n) => ids.has(n.id))
    }
    return { nodes, edges }
  }
  return http.get('/knowledge-graph', { category, region, depth })
}

/* 获取传承人详情：GET /heritage/inheritor/{id} */
export async function getInheritorDetail(id) {
  if (config.useMock) {
    await mockDelay()
    const person = mock.inheritors.find((i) => i.id === Number(id))
    if (!person) throw new Error('传承人不存在')
    const project = mock.projects.find((p) => p.id === person.project_id)
    return Object.assign({}, person, { project_name: project ? project.name : '' })
  }
  return http.get('/heritage/inheritor/' + id)
}

/* 智能关联推荐：GET /heritage/{id}/recommendations */
export async function getRecommendations(id) {
  if (config.useMock) {
    await mockDelay(200)
    const project = mock.projects.find((p) => p.id === Number(id))
    if (!project) return { similar: [], sameRegion: [], sameCategory: [] }
    const similar = mock.projects.filter((p) => p.id !== project.id && p.materials.some((m) => project.materials.includes(m))).slice(0, 4)
    const sameCategory = mock.projects.filter((p) => p.id !== project.id && p.category === project.category).slice(0, 4)
    const sameRegion = mock.projects.filter((p) => p.id !== project.id && p.region === project.region).slice(0, 4)
    return { similar, sameCategory, sameRegion }
  }
  return http.get('/heritage/' + id + '/recommendations')
}

export default { getCategories, getProjectList, getProjectDetail, getKnowledgeGraph, getInheritorDetail, getRecommendations }
