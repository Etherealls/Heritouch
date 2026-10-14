/**
 * 前端 Mock 数据统一出口。
 *
 * 名录数据（categories / projects / inheritors）来自全国非遗真实数据
 * （mobile-app/api/mock/national-data.js，由 scripts/build_all_data.py 生成，
 *   数据源：中国非物质文化遗产网 ihchina.cn 公开名录）。
 *
 * 闯关题目 / 关卡 / 智能问答为演示内容，与名录数据解耦。
 */
import { categories, projects, inheritors } from './national-data'

/* ---------------- 知识图谱（动态构建，避免全量渲染卡死） ---------------- */
/* 关系类型（文档 4.1.3）：
   INHERITS 传承人→项目 / BELONGS_TO_CATEGORY 项目→类别 / PREVAILED_IN 项目→朝代
   USES_MATERIAL 项目→材料 / CREATED 传承人→作品 / ASSOCIATED_WITH 项目→民俗 */
const MAX_GRAPH_PROJECTS = 100      // 单类别图谱最多渲染的项目节点数
const MAX_GRAPH_INHERITORS = 200    // 单类别图谱最多渲染的传承人节点数

/* 按类别（与地区）动态构建图谱子图。category 为空时返回类别概览图。 */
export function buildGraph(category = '', region = '') {
  // 1. 无类别：返回「类别 + 每类代表项目」的稀疏概览
  if (!category) {
    const nodes = categories.map((c) => ({ id: 'c' + c.id, name: c.name, type: 'category' }))
    const edges = []
    const perCat = {}
    projects.forEach((p) => {
      ;(perCat[p.category] = perCat[p.category] || []).push(p)
    })
    categories.forEach((c) => {
      const reps = (perCat[c.name] || []).slice(0, 5)
      reps.forEach((p) => {
        const hid = 'h' + p.id
        nodes.push({ id: hid, name: p.name, type: 'heritage', refId: p.id })
        edges.push({ source: hid, target: 'c' + c.id, label: '归属' })
      })
    })
    return { nodes, edges }
  }

  // 2. 指定类别：该类全部项目（限量）+ 传承人 + 类别节点
  const cat = categories.find((c) => c.name === category)
  const catId = cat ? 'c' + cat.id : 'c_' + category
  const nodes = [{ id: catId, name: category, type: 'category' }]
  const edges = []
  const nodeIds = new Set([catId])

  const list = projects.filter(
    (p) => p.category === category && (!region || (p.region || '').includes(region))
  )
  const shown = list.slice(0, MAX_GRAPH_PROJECTS)

  shown.forEach((p) => {
    const hid = 'h' + p.id
    nodes.push({ id: hid, name: p.name, type: 'heritage', refId: p.id })
    nodeIds.add(hid)
    edges.push({ source: hid, target: catId, label: '归属' })
    // 传承人（限量）
    let cnt = 0
    ;(p.inheritors || []).forEach((iid) => {
      if (cnt >= 5) return
      const per = inheritors.find((i) => i.id === iid)
      if (!per) return
      const nid = 'i' + per.id
      if (!nodeIds.has(nid) && nodes.filter((n) => n.type === 'inheritor').length < MAX_GRAPH_INHERITORS) {
        nodes.push({ id: nid, name: per.name, type: 'inheritor', refId: per.id })
        nodeIds.add(nid)
        cnt++
      }
      edges.push({ source: nid, target: hid, label: '传承' })
    })
  })

  return { nodes, edges }
}

/* ---------------- 科普闯关：关卡与段位（演示内容） ---------------- */
export const gameLevels = [
  {
    id: 1,
    name: '入门学徒',
    subtitle: '初识非遗',
    rank: '学徒',
    need_score: 0,
    theme: '基础认知',
    question_count: 10,
    icon: '🌱'
  },
  {
    id: 2,
    name: '匠人弟子',
    subtitle: '技艺门类辨一辨',
    rank: '弟子',
    need_score: 100,
    theme: '传统技艺',
    question_count: 10,
    icon: '🔨'
  },
  {
    id: 3,
    name: '曲苑知音',
    subtitle: '戏曲曲艺听门道',
    rank: '弟子',
    need_score: 250,
    theme: '戏剧曲艺',
    question_count: 10,
    icon: '🎭'
  },
  {
    id: 4,
    name: '丹青圣手',
    subtitle: '美术与图案的世界',
    rank: '匠人',
    need_score: 450,
    theme: '传统美术',
    question_count: 10,
    icon: '🖌️'
  },
  {
    id: 5,
    name: '非遗大师',
    subtitle: '综合大闯关',
    rank: '大师',
    need_score: 700,
    theme: '综合进阶',
    question_count: 10,
    icon: '🏆'
  }
]

/* ---------------- 题库（单选 / 判断 / 识图，通用非遗常识） ---------------- */
export const questions = [
  // 第一关：入门学徒
  { id: 1, level_id: 1, question_type: 'single', question_text: '中国剪纸属于下列哪一类非遗？', option_a: '传统美术', option_b: '传统戏剧', option_c: '传统医药', option_d: '民俗', answer: 'A', analysis: '剪纸是国家级传统美术类非遗，以细秀雅活著称。', difficulty: 1 },
  { id: 2, level_id: 1, question_type: 'judge', question_text: '中国玉雕以大型山子雕见长，被誉为玉雕“南派”代表。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '玉雕讲究因料施艺，山子雕是其标志性品类。', difficulty: 1 },
  { id: 3, level_id: 1, question_type: 'single', question_text: '非物质文化遗产保护的十六字方针是？', option_a: '保护为主、抢救第一、合理利用、传承发展', option_b: '开发为主、市场导向、规模经营、盈利优先', option_c: '原样封存、禁止展示、只存不用', option_d: '全部数字化、禁止线下传承', answer: 'A', analysis: '我国非遗保护坚持“保护为主、抢救第一、合理利用、传承发展”的工作方针。', difficulty: 1 },
  { id: 4, level_id: 1, question_type: 'single', question_text: '国家级非物质文化遗产项目由哪个机构公布？', option_a: '国务院', option_b: '文化和旅游部', option_c: '中国文联', option_d: '国家文物局', answer: 'A', analysis: '国家级非遗代表性项目名录由国务院批准公布。', difficulty: 1 },
  { id: 5, level_id: 1, question_type: 'judge', question_text: '非遗的“活态传承”强调技艺随时代发展而演变，而非僵化保存。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '活态传承是非遗保护核心理念，强调在传承中创新。', difficulty: 1 },
  { id: 6, level_id: 1, question_type: 'single', question_text: '下列哪一项属于“传统技艺”类非遗？', option_a: '雕漆髹饰', option_b: '京剧', option_c: '古琴', option_d: '剪纸', answer: 'A', analysis: '雕漆髹饰属传统技艺，京剧属传统戏剧，古琴属传统音乐，剪纸属传统美术。', difficulty: 1 },
  { id: 7, level_id: 1, question_type: 'image', question_text: '下图所示作品最可能属于哪种非遗技艺？', option_a: '漆器髹饰', option_b: '蓝印花布', option_c: '剪纸', option_d: '玉雕', answer: 'A', analysis: '图中作品为雕漆嵌玉风格，是漆器的典型样式。', image: '/static/images/quiz-lacquer.jpg', difficulty: 1 },
  { id: 8, level_id: 1, question_type: 'single', question_text: '评话表演时常用的道具组合是？', option_a: '折扇与醒木', option_b: '三弦与鼓板', option_c: '二胡与琵琶', option_d: '锣鼓与唢呐', answer: 'A', analysis: '评话以折扇、醒木为道具，讲究口手眼身步五功。', difficulty: 1 },
  { id: 9, level_id: 1, question_type: 'judge', question_text: '民歌是流传于水乡、田间的一种民间音乐形式。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '民歌属传统音乐类非遗，各地风格浓郁。', difficulty: 1 },
  { id: 10, level_id: 1, question_type: 'single', question_text: '刺绣最负盛名的品类是？', option_a: '仿古绣', option_b: '苏绣双面绣', option_c: '湘绣狮虎', option_d: '粤绣金线', answer: 'A', analysis: '仿古绣和水墨绣擅长表现书画笔墨意趣。', difficulty: 1 },
  // 第二关：匠人弟子
  { id: 11, level_id: 2, question_type: 'single', question_text: '蓝印花布印染中起防染作用的材料是？', option_a: '黄豆粉加石灰', option_b: '蜂蜡', option_c: '松香', option_d: '面粉糊', answer: 'A', analysis: '黄豆粉加石灰刮浆形成防染层，靛缸浸染后呈蓝白花纹。', difficulty: 2 },
  { id: 12, level_id: 2, question_type: 'judge', question_text: '一件雕漆作品往往需要髹涂数十至数百道大漆。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '雕漆需层层髹涂、道道阴干，耗时可达数年。', difficulty: 2 },
  { id: 13, level_id: 2, question_type: 'single', question_text: '“三丁包”的“三丁”不包括下列哪一项？', option_a: '笋丁', option_b: '鸡丁', option_c: '肉丁', option_d: '虾丁', answer: 'D', analysis: '三丁指鸡丁、肉丁、笋丁，讲究鸡丁大、笋丁脆、肉丁香。', difficulty: 2 },
  { id: 14, level_id: 2, question_type: 'single', question_text: '中国古琴重要流派广陵琴派的艺术风格被概括为？', option_a: '跌宕多变、刚柔相济', option_b: '苍古雄健', option_c: '细腻婉约如吴语', option_d: '高亢激越', answer: 'A', analysis: '广陵琴派风格跌宕多变、刚柔相济，指法细腻。', difficulty: 2 },
  { id: 15, level_id: 2, question_type: 'single', question_text: '“三把刀”技艺（厨刀、修脚刀、剃头刀）属于哪类生活技艺？', option_a: '传统技艺/民俗', option_b: '传统美术', option_c: '传统医药', option_d: '传统戏剧', answer: 'A', analysis: '三把刀集中体现生活服务业技艺的精巧，属传统技艺或民俗类。', difficulty: 2 },
  { id: 16, level_id: 2, question_type: 'image', question_text: '下图所示图案最可能是哪种非遗？', option_a: '蓝印花布', option_b: '玉雕', option_c: '漆器', option_d: '木偶', answer: 'A', analysis: '图中为蓝印花布经典图案，蓝白相映。', image: '/static/images/quiz-calico.jpg', difficulty: 2 },
  { id: 17, level_id: 2, question_type: 'judge', question_text: '剪纸的“点色剪纸”采用“一手剪、一手染”技法。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '点色剪纸染色自然灵动，是剪纸特色技法。', difficulty: 2 },
  { id: 18, level_id: 2, question_type: 'single', question_text: '杖头木偶的结构特点是？', option_a: '内扦', option_b: '外扦', option_c: '提线', option_d: '布袋', answer: 'A', analysis: '杖头木偶以内扦结构为特色，可眼转口开。', difficulty: 2 },
  { id: 19, level_id: 2, question_type: 'single', question_text: '下列哪种材料不是漆器髹饰的常用材料？', option_a: '景德镇瓷土', option_b: '大漆', option_c: '螺钿', option_d: '金银箔', answer: 'A', analysis: '漆器以大漆、螺钿、金银箔等为材，与瓷土无关。', difficulty: 2 },
  { id: 20, level_id: 2, question_type: 'judge', question_text: '玉雕讲究“因料施艺、量材取形”。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '因料施艺是玉雕的核心创作原则。', difficulty: 2 },
  // 第三关：曲苑知音
  { id: 21, level_id: 3, question_type: 'single', question_text: '评话说表时讲究“五功”，指的是？', option_a: '口、手、眼、身、步', option_b: '说、学、逗、唱、演', option_c: '唱、念、做、打、翻', option_d: '吹、拉、弹、打、舞', answer: 'A', analysis: '评话五功为口手眼身步。', difficulty: 2 },
  { id: 22, level_id: 3, question_type: 'single', question_text: '京剧的两大主要声腔是？', option_a: '西皮与二黄', option_b: '高腔与昆腔', option_c: '大开口与小开口', option_d: '评弹与宣卷', answer: 'A', analysis: '京剧以西皮、二黄为主要声腔，故又称皮黄戏。', difficulty: 2 },
  { id: 23, level_id: 3, question_type: 'single', question_text: '苏州评弹的伴奏乐器主要是？', option_a: '琵琶与三弦', option_b: '二胡与笛子', option_c: '古筝与扬琴', option_d: '锣鼓与唢呐', answer: 'A', analysis: '评弹以琵琶、三弦为主要伴奏乐器。', difficulty: 2 },
  { id: 24, level_id: 3, question_type: 'judge', question_text: '昆曲被联合国教科文组织列入“人类非物质文化遗产代表作名录”。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '2001年昆曲成为我国首个入选人类非遗代表作名录的项目。', difficulty: 2 },
  { id: 25, level_id: 3, question_type: 'single', question_text: '下列哪部是京剧经典剧目？', option_a: '《霸王别姬》', option_b: '《牡丹亭》', option_c: '《天仙配》', option_d: '《花木兰》', answer: 'A', analysis: '《霸王别姬》是京剧梅派经典，《牡丹亭》是昆曲。', difficulty: 2 },
  { id: 26, level_id: 3, question_type: 'single', question_text: '说书人表演《水浒》评话系列，其说表被誉为什么？', option_a: '武水浒', option_b: '活关公', option_c: '俏西施', option_d: '金嗓子', answer: 'A', analysis: '以《水浒》享誉书坛者常被誉为“武水浒”。', difficulty: 3 },
  { id: 27, level_id: 3, question_type: 'image', question_text: '下图展示的是哪项非遗的演出场景？', option_a: '杖头木偶戏', option_b: '评话', option_c: '京剧', option_d: '清曲坐唱', answer: 'A', analysis: '杖头木偶以内扦操控，演员与木偶同台表演。', image: '/static/images/quiz-puppet.jpg', difficulty: 3 },
  { id: 28, level_id: 3, question_type: 'judge', question_text: '古琴艺术已被列入人类非物质文化遗产代表作名录。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '2003年古琴艺术入选人类非遗代表作名录。', difficulty: 2 },
  { id: 29, level_id: 3, question_type: 'single', question_text: '评话中用于开场镇场、提示听众的道具是？', option_a: '醒木', option_b: '铜锣', option_c: '鼓板', option_d: '铃铛', answer: 'A', analysis: '醒木是评话表演的重要道具。', difficulty: 2 },
  { id: 30, level_id: 3, question_type: 'single', question_text: '昆曲的代表性经典剧目是？', option_a: '《牡丹亭》', option_b: '《二泉映月》', option_c: '《茉莉花》', option_d: '《梁祝》', answer: 'A', analysis: '《牡丹亭》是汤显祖代表作，昆曲经典。', difficulty: 3 },
  // 第四关：丹青圣手
  { id: 31, level_id: 4, question_type: 'single', question_text: '中国剪纸的艺术特色常被概括为？', option_a: '细、秀、雅、活', option_b: '粗、犷、朴、拙', option_c: '艳、丽、繁、密', option_d: '简、淡、空、灵', answer: 'A', analysis: '“细秀雅活”是中国剪纸的公认风格。', difficulty: 2 },
  { id: 32, level_id: 4, question_type: 'single', question_text: '点螺是漆器的哪类工艺？', option_a: '镶嵌装饰', option_b: '髹涂打磨', option_c: '雕刻成型', option_d: '编织收边', answer: 'A', analysis: '点螺以螺钿镶嵌成纹，是漆器装饰工艺。', difficulty: 3 },
  { id: 33, level_id: 4, question_type: 'judge', question_text: '中国玉雕在明清时期达到鼎盛。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '明清时期玉器业繁荣，玉雕工艺达到鼎盛。', difficulty: 2 },
  { id: 34, level_id: 4, question_type: 'single', question_text: '中国刺绣擅长表现的画种风格是？', option_a: '水墨山水', option_b: '油画肖像', option_c: '版画插图', option_d: '壁画飞天', answer: 'A', analysis: '刺绣以针代笔表现水墨画的浓淡干湿。', difficulty: 3 },
  { id: 35, level_id: 4, question_type: 'image', question_text: '下图所示场景是哪项非遗的创作？', option_a: '剪纸', option_b: '玉雕抛光', option_c: '漆器髹涂', option_d: '木偶制作', answer: 'A', analysis: '图中为剪纸创作场景，一剪一染见功夫。', image: '/static/images/quiz-papercut.jpg', difficulty: 2 },
  { id: 36, level_id: 4, question_type: 'single', question_text: '“剪纸绣样”的主要用途是？', option_a: '为刺绣提供底样', option_b: '建筑彩绘打底', option_c: '漆器纹样拓印', option_d: '木雕图样复制', answer: 'A', analysis: '剪纸常用于刺绣底样，是剪纸最早的功能之一。', difficulty: 3 },
  { id: 37, level_id: 4, question_type: 'judge', question_text: '漆器的“平磨螺钿”属于镶嵌类工艺。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '平磨螺钿以螺钿打磨拼嵌成图。', difficulty: 3 },
  { id: 38, level_id: 4, question_type: 'single', question_text: '剪纸从用途上最早多用于？', option_a: '刺绣样稿', option_b: '门窗装饰', option_c: '礼品包装', option_d: '书籍插图', answer: 'A', analysis: '早期剪纸多为刺绣样稿与喜庆装饰。', difficulty: 3 },
  { id: 39, level_id: 4, question_type: 'single', question_text: '下列哪种色彩体系是蓝印花布的典型特征？', option_a: '蓝白两色', option_b: '五彩斑斓', option_c: '金碧辉煌', option_d: '朱红黛绿', answer: 'A', analysis: '蓝印花布以靛蓝染于白布，蓝白相映。', difficulty: 1 },
  { id: 40, level_id: 4, question_type: 'judge', question_text: '“中国剪纸”整体项目已列入人类非物质文化遗产代表作名录。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '2009年“中国剪纸”入选人类非遗代表作名录。', difficulty: 3 },
  // 第五关：非遗大师
  { id: 41, level_id: 5, question_type: 'single', question_text: '下列哪一组非遗项目同属“传统美术”类？', option_a: '剪纸、玉雕', option_b: '京剧、评话', option_c: '茶点、蓝印花布', option_d: '民歌、古琴', answer: 'A', analysis: '剪纸与玉雕均为传统美术类。', difficulty: 3 },
  { id: 42, level_id: 5, question_type: 'single', question_text: '漆器“雕漆嵌玉”融合了哪两种工艺？', option_a: '雕漆与玉石镶嵌', option_b: '点螺与戗金', option_c: '平磨与描金', option_d: '剔红与剔犀', answer: 'A', analysis: '雕漆嵌玉以雕漆为地、镶嵌玉石为饰。', difficulty: 3 },
  { id: 43, level_id: 5, question_type: 'judge', question_text: '非遗知识图谱中，“传承人”与“非遗项目”之间的关系类型是传承（INHERITS）。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '图谱中 [:INHERITS] 表示传承人对项目的传承关系。', difficulty: 3 },
  { id: 44, level_id: 5, question_type: 'single', question_text: '“魁龙珠”茶的窨制原料是？', option_a: '龙井、魁针、珠兰', option_b: '毛尖、茉莉、桂花', option_c: '普洱、玫瑰、陈皮', option_d: '铁观音、菊花、冰糖', answer: 'A', analysis: '魁龙珠取龙井之味、魁针之色、珠兰之香。', difficulty: 3 },
  { id: 45, level_id: 5, question_type: 'single', question_text: '下列哪项属于“传统医药”类非遗？', option_a: '中医诊法', option_b: '太极拳', option_c: '京剧', option_d: '剪纸', answer: 'A', analysis: '中医诊法属传统医药，太极拳属传统体育游艺杂技。', difficulty: 3 },
  { id: 46, level_id: 5, question_type: 'image', question_text: '下图所示作品最可能是？', option_a: '玉雕山子', option_b: '剪纸', option_c: '漆器', option_d: '刺绣', answer: 'A', analysis: '图中为玉雕山子，玉雕擅长大型山子雕。', image: '/static/images/quiz-jade.jpg', difficulty: 3 },
  { id: 47, level_id: 5, question_type: 'judge', question_text: 'AI 生成的非遗风格作品在平台中会标注“AI创作”标识。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '按平台合规要求，AI 生成内容均标注“AI创作”。', difficulty: 1 },
  { id: 48, level_id: 5, question_type: 'single', question_text: '扫码导览功能中，二维码解析出的关键参数是？', option_a: '项目ID', option_b: '用户ID', option_c: '音频时长', option_d: '地图坐标', answer: 'A', analysis: '二维码内含项目ID，扫码后跳转对应详情与讲解。', difficulty: 2 },
  { id: 49, level_id: 5, question_type: 'single', question_text: '评话表演中“一人摹拟百样角色”的表现手法称为？', option_a: '演口', option_b: '噱功', option_c: '方口', option_d: '圆口', answer: 'A', analysis: '“演口”指演员以声口、神态摹拟各类角色。', difficulty: 3 },
  { id: 50, level_id: 5, question_type: 'judge', question_text: '平台的知识图谱数据存储于 Neo4j 图数据库中。', option_a: '正确', option_b: '错误', answer: 'A', analysis: '非遗实体与关系存储于 Neo4j，业务数据存储于 MySQL。', difficulty: 2 }
]

/* ---------------- 智能问答 Mock 回复（演示内容） ---------------- */
export const qaAnswers = [
  {
    keywords: ['剪纸', '历史', '多少年'],
    answer: '中国剪纸源于民间，历史悠久，早期多用作刺绣底样，故称“剪纸绣样”。2009年“中国剪纸”整体项目列入人类非物质文化遗产代表作名录。',
    audio: '/static/audio/qa-jianzhi.mp3'
  },
  {
    keywords: ['漆器', '工艺', '多久'],
    answer: '漆器髹饰综合雕漆、点螺、平磨螺钿等工艺。一件雕漆作品需髹涂数十至数百道大漆，每道漆都要阴干，制作周期常达数月甚至数年。',
    audio: '/static/audio/qa-qiqi.mp3'
  },
  {
    keywords: ['玉雕', '山子'],
    answer: '中国玉雕讲究“因料施艺、量材取形”，尤其擅长大型山子雕，将山水人物凝于一玉。明清时期玉雕工艺达到鼎盛。',
    audio: '/static/audio/qa-yudiao.mp3'
  },
  {
    keywords: ['早茶', '三丁包', '富春'],
    answer: '早茶以“早上皮包水”为习俗代表，三丁包以鸡丁、肉丁、笋丁为馅，讲究鸡丁大、笋丁脆、肉丁香；佐茶以“魁龙珠”最为经典。',
    audio: '/static/audio/qa-fuchun.mp3'
  }
]

export default { categories, projects, inheritors, buildGraph, gameLevels, questions, qaAnswers }
