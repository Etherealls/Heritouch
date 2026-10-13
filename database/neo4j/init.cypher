// =====================================================================
// Heritouch 地方非遗文化AI解码与传承平台 —— Neo4j 知识图谱初始化脚本
// 版本：v1.0（Neo4j 5.x 语法）
//
// 用法（二选一）：
//   方式一（docker-compose 部署）：
//     将本文件挂载到 Neo4j 容器的 /var/lib/neo4j/import 目录后执行：
//       docker compose exec neo4j cypher-shell -u neo4j -p password -f /var/lib/neo4j/import/init.cypher
//   方式二（本地/远程实例）：
//       cypher-shell -a bolt://localhost:7687 -u neo4j -p password -f init.cypher
//
// 数据说明：14 个非遗项目、16 位传承人、7 个类别、3 个朝代、3 类材料、
//           3 个民俗，节点 id 与 MySQL 主键对齐（前端力导图共用同一套 id）。
//           内容为演示数据，名称/类别/级别依据公开非遗名录整理。
//
// 注意：清空语句会删除库中全部节点与关系，仅限初始化使用！
// =====================================================================

// ---------- 0. 清空数据库（仅初始化用，生产环境请谨慎执行） ----------
MATCH (n) DETACH DELETE n;

// ---------- 1. 创建约束与索引（Neo4j 5.x 语法，存在则不重复创建） ----------
CREATE CONSTRAINT heritage_id_unique IF NOT EXISTS FOR (h:Heritage) REQUIRE h.id IS UNIQUE;
CREATE CONSTRAINT inheritor_id_unique IF NOT EXISTS FOR (i:Inheritor) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT category_name_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT dynasty_name_unique IF NOT EXISTS FOR (d:Dynasty) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT material_name_unique IF NOT EXISTS FOR (m:Material) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT folk_custom_name_unique IF NOT EXISTS FOR (f:FolkCustom) REQUIRE f.name IS UNIQUE;

// ---------- 2. 批量创建节点 ----------

// 2.1 非遗项目（:Heritage，id 与 MySQL heritage_project.id 对齐）
UNWIND [
  {id: 1,  name: '扬州剪纸', level: '国家级', category: '传统美术', region: '江苏扬州', batch: 2006},
  {id: 2,  name: '扬州玉雕', level: '国家级', category: '传统美术', region: '江苏扬州', batch: 2006},
  {id: 3,  name: '扬州漆器髹饰技艺', level: '国家级', category: '传统技艺', region: '江苏扬州', batch: 2006},
  {id: 4,  name: '扬州评话', level: '国家级', category: '曲艺', region: '江苏扬州', batch: 2006},
  {id: 5,  name: '扬剧', level: '国家级', category: '传统戏剧', region: '江苏扬州', batch: 2006},
  {id: 6,  name: '扬州清曲', level: '国家级', category: '曲艺', region: '江苏扬州', batch: 2006},
  {id: 7,  name: '古琴艺术（广陵琴派）', level: '国家级', category: '传统音乐', region: '江苏扬州', batch: 2008},
  {id: 8,  name: '扬州刺绣', level: '省级', category: '传统美术', region: '江苏扬州', batch: 2007},
  {id: 9,  name: '蓝印花布印染技艺', level: '省级', category: '传统技艺', region: '江苏扬州', batch: 2007},
  {id: 10, name: '富春茶点制作技艺', level: '国家级', category: '传统技艺', region: '江苏扬州', batch: 2008},
  {id: 11, name: '杖头木偶戏（扬州杖头木偶）', level: '省级', category: '传统戏剧', region: '江苏扬州', batch: 2007},
  {id: 12, name: '高邮民歌', level: '省级', category: '传统音乐', region: '江苏扬州（高邮）', batch: 2007},
  {id: 13, name: '扬州“三把刀”技艺', level: '省级', category: '民俗', region: '江苏扬州', batch: 2007},
  {id: 14, name: '夏氏内科疗法（扬州中医）', level: '省级', category: '传统医药', region: '江苏扬州', batch: 2016}
] AS row
CREATE (h:Heritage {id: row.id, name: row.name, level: row.level, category: row.category, region: row.region, batch: row.batch});

// 2.2 传承人（:Inheritor，id 与 MySQL inheritor.id 对齐，演示数据）
UNWIND [
  {id: 101, name: '张秀芳', project_id: 1,  title: '国家级代表性传承人'},
  {id: 102, name: '熊崇荣', project_id: 1,  title: '市级代表性传承人'},
  {id: 103, name: '江春',   project_id: 2,  title: '国家级代表性传承人'},
  {id: 104, name: '张来喜', project_id: 3,  title: '国家级代表性传承人'},
  {id: 105, name: '池家骏', project_id: 3,  title: '市级代表性传承人'},
  {id: 106, name: '王丽堂', project_id: 4,  title: '国家级代表性传承人'},
  {id: 107, name: '李开敏', project_id: 5,  title: '省级代表性传承人'},
  {id: 108, name: '聂峰',   project_id: 6,  title: '省级代表性传承人'},
  {id: 109, name: '马维衡', project_id: 7,  title: '省级代表性传承人'},
  {id: 110, name: '卫芳',   project_id: 8,  title: '市级代表性传承人'},
  {id: 111, name: '王稳扬', project_id: 9,  title: '市级代表性传承人'},
  {id: 112, name: '徐永珍', project_id: 10, title: '国家级代表性传承人'},
  {id: 113, name: '封春来', project_id: 11, title: '市级代表性传承人'},
  {id: 114, name: '王兰英', project_id: 12, title: '省级代表性传承人'},
  {id: 115, name: '陆琴',   project_id: 13, title: '市级代表性传承人'},
  {id: 116, name: '夏雨生', project_id: 14, title: '市级代表性传承人'}
] AS row
CREATE (i:Inheritor {id: row.id, name: row.name, project_id: row.project_id, title: row.title});

// 2.3 非遗类别（:Category，7 类）
UNWIND ['传统技艺', '传统美术', '传统戏剧', '传统音乐', '曲艺', '民俗', '传统医药'] AS name
CREATE (c:Category {name: name});

// 2.4 朝代（:Dynasty，带起止年份）
UNWIND [
  {name: '唐宋',   start_year: 618,  end_year: 1279},
  {name: '明清',   start_year: 1368, end_year: 1912},
  {name: '近现代', start_year: 1912, end_year: 2025}
] AS row
CREATE (d:Dynasty {name: row.name, start_year: row.start_year, end_year: row.end_year});

// 2.5 材料（:Material）
UNWIND ['宣纸彩纸', '和田玉石', '大漆螺钿'] AS name
CREATE (m:Material {name: name});

// 2.6 民俗（:FolkCustom）
UNWIND ['扬州早茶', '春节窗花', '澡堂文化'] AS name
CREATE (f:FolkCustom {name: name});

// ---------- 3. 批量创建关系 ----------

// 3.1 [:INHERITS] 传承人 → 项目（传承人传承某项目）
UNWIND [
  {inheritor_id: 101, project_id: 1},
  {inheritor_id: 102, project_id: 1},
  {inheritor_id: 103, project_id: 2},
  {inheritor_id: 104, project_id: 3},
  {inheritor_id: 105, project_id: 3},
  {inheritor_id: 106, project_id: 4},
  {inheritor_id: 107, project_id: 5},
  {inheritor_id: 108, project_id: 6},
  {inheritor_id: 109, project_id: 7},
  {inheritor_id: 110, project_id: 8},
  {inheritor_id: 111, project_id: 9},
  {inheritor_id: 112, project_id: 10},
  {inheritor_id: 113, project_id: 11},
  {inheritor_id: 114, project_id: 12},
  {inheritor_id: 115, project_id: 13},
  {inheritor_id: 116, project_id: 14}
] AS row
MATCH (i:Inheritor {id: row.inheritor_id}), (h:Heritage {id: row.project_id})
CREATE (i)-[:INHERITS]->(h);

// 3.2 [:BELONGS_TO_CATEGORY] 项目 → 类别
UNWIND [
  {project_id: 1,  category: '传统美术'},
  {project_id: 2,  category: '传统美术'},
  {project_id: 3,  category: '传统技艺'},
  {project_id: 4,  category: '曲艺'},
  {project_id: 5,  category: '传统戏剧'},
  {project_id: 6,  category: '曲艺'},
  {project_id: 7,  category: '传统音乐'},
  {project_id: 8,  category: '传统美术'},
  {project_id: 9,  category: '传统技艺'},
  {project_id: 10, category: '传统技艺'},
  {project_id: 11, category: '传统戏剧'},
  {project_id: 12, category: '传统音乐'},
  {project_id: 13, category: '民俗'},
  {project_id: 14, category: '传统医药'}
] AS row
MATCH (h:Heritage {id: row.project_id}), (c:Category {name: row.category})
CREATE (h)-[:BELONGS_TO_CATEGORY]->(c);

// 3.3 [:PREVAILED_IN] 项目 → 朝代（盛行/形成时期）
UNWIND [
  {project_id: 1,  dynasty: '唐宋'},
  {project_id: 2,  dynasty: '明清'},
  {project_id: 3,  dynasty: '明清'},
  {project_id: 4,  dynasty: '明清'},
  {project_id: 5,  dynasty: '近现代'},
  {project_id: 7,  dynasty: '明清'},
  {project_id: 10, dynasty: '近现代'}
] AS row
MATCH (h:Heritage {id: row.project_id}), (d:Dynasty {name: row.dynasty})
CREATE (h)-[:PREVAILED_IN]->(d);

// 3.4 [:USES_MATERIAL] 项目 → 材料
UNWIND [
  {project_id: 1,  material: '宣纸彩纸'},
  {project_id: 2,  material: '和田玉石'},
  {project_id: 3,  material: '大漆螺钿'}
] AS row
MATCH (h:Heritage {id: row.project_id}), (m:Material {name: row.material})
CREATE (h)-[:USES_MATERIAL]->(m);

// 3.5 [:ASSOCIATED_WITH] 项目 → 民俗（如 扬州剪纸-春节窗花、富春茶点-扬州早茶、三把刀-扬州早茶/澡堂文化）
UNWIND [
  {project_id: 1,  folk_custom: '春节窗花'},
  {project_id: 10, folk_custom: '扬州早茶'},
  {project_id: 13, folk_custom: '扬州早茶'},
  {project_id: 13, folk_custom: '澡堂文化'}
] AS row
MATCH (h:Heritage {id: row.project_id}), (f:FolkCustom {name: row.folk_custom})
CREATE (h)-[:ASSOCIATED_WITH]->(f);

// ---------- 4. 初始化完成，可执行以下语句抽查 ----------
// MATCH (n) RETURN count(n) AS 节点总数;                       -- 预期 46
// MATCH ()-[r]->() RETURN count(r) AS 关系总数;                -- 预期 42
