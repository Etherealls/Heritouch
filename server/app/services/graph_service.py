"""Neo4j 知识图谱服务。

使用官方 neo4j Python 驱动（py2neo 2021.2.4 与 Neo4j 5.26+ 的 Bolt 5
协议不兼容，故迁移到官方驱动）。

降级策略：
- 未配置 Neo4j 或连接失败时，从 MySQL 业务数据构建同构图谱
  （全国非遗数据，数据库为空时回退内置演示数据）；
- Neo4j 可用但库中无 Heritage 节点时，同样回退内存图谱；
- sync_from_mysql 从 MySQL 业务数据构建图谱（MERGE 语义，可重复执行）。
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.heritage import HeritageProject, Inheritor

logger = logging.getLogger("heritouch.graph")

# =====================================================================
# 演示数据约定（与 database/neo4j/init.cypher、前端 mock 完全一致）
# =====================================================================

# 非遗类别固定顺序（id 与前端分类图标映射一致）
CATEGORY_ORDER: list[str] = ["传统技艺", "传统美术", "传统戏剧", "传统音乐", "曲艺", "民俗", "传统医药"]

# 朝代 / 材料 / 民俗固定顺序
DYNASTY_ORDER: list[str] = ["唐宋", "明清", "近现代"]
MATERIAL_ORDER: list[str] = ["宣纸彩纸", "和田玉石", "大漆螺钿"]
FOLK_CUSTOM_ORDER: list[str] = ["扬州早茶", "春节窗花", "澡堂文化"]

# 关系类型 → 前端展示名（中文，与前端 mock 一致）
RELATION_LABELS: dict[str, str] = {
    "INHERITS": "传承",
    "BELONGS_TO_CATEGORY": "归属",
    "PREVAILED_IN": "盛行于",
    "USES_MATERIAL": "使用材料",
    "CREATED": "创作",
    "ASSOCIATED_WITH": "关联民俗",
}

# 14 个非遗项目基础信息（id 与 MySQL 主键对齐）
DEMO_PROJECTS: list[dict[str, Any]] = [
    {"id": 1, "name": "扬州剪纸", "level": "国家级", "category": "传统美术", "region": "江苏扬州"},
    {"id": 2, "name": "扬州玉雕", "level": "国家级", "category": "传统美术", "region": "江苏扬州"},
    {"id": 3, "name": "扬州漆器髹饰技艺", "level": "国家级", "category": "传统技艺", "region": "江苏扬州"},
    {"id": 4, "name": "扬州评话", "level": "国家级", "category": "曲艺", "region": "江苏扬州"},
    {"id": 5, "name": "扬剧", "level": "国家级", "category": "传统戏剧", "region": "江苏扬州"},
    {"id": 6, "name": "扬州清曲", "level": "国家级", "category": "曲艺", "region": "江苏扬州"},
    {"id": 7, "name": "古琴艺术（广陵琴派）", "level": "国家级", "category": "传统音乐", "region": "江苏扬州"},
    {"id": 8, "name": "扬州刺绣", "level": "省级", "category": "传统美术", "region": "江苏扬州"},
    {"id": 9, "name": "蓝印花布印染技艺", "level": "省级", "category": "传统技艺", "region": "江苏扬州"},
    {"id": 10, "name": "富春茶点制作技艺", "level": "国家级", "category": "传统技艺", "region": "江苏扬州"},
    {"id": 11, "name": "杖头木偶戏（扬州杖头木偶）", "level": "省级", "category": "传统戏剧", "region": "江苏扬州"},
    {"id": 12, "name": "高邮民歌", "level": "省级", "category": "传统音乐", "region": "江苏扬州（高邮）"},
    {"id": 13, "name": "扬州“三把刀”技艺", "level": "省级", "category": "民俗", "region": "江苏扬州"},
    {"id": 14, "name": "夏氏内科疗法（扬州中医）", "level": "省级", "category": "传统医药", "region": "江苏扬州"},
]

# 16 位传承人（id 与 MySQL 主键对齐）
DEMO_INHERITORS: list[dict[str, Any]] = [
    {"id": 101, "name": "张秀芳", "project_id": 1, "title": "国家级代表性传承人"},
    {"id": 102, "name": "熊崇荣", "project_id": 1, "title": "市级代表性传承人"},
    {"id": 103, "name": "江春", "project_id": 2, "title": "国家级代表性传承人"},
    {"id": 104, "name": "张来喜", "project_id": 3, "title": "国家级代表性传承人"},
    {"id": 105, "name": "池家骏", "project_id": 3, "title": "市级代表性传承人"},
    {"id": 106, "name": "王丽堂", "project_id": 4, "title": "国家级代表性传承人"},
    {"id": 107, "name": "李开敏", "project_id": 5, "title": "省级代表性传承人"},
    {"id": 108, "name": "聂峰", "project_id": 6, "title": "省级代表性传承人"},
    {"id": 109, "name": "马维衡", "project_id": 7, "title": "省级代表性传承人"},
    {"id": 110, "name": "卫芳", "project_id": 8, "title": "市级代表性传承人"},
    {"id": 111, "name": "王稳扬", "project_id": 9, "title": "市级代表性传承人"},
    {"id": 112, "name": "徐永珍", "project_id": 10, "title": "国家级代表性传承人"},
    {"id": 113, "name": "封春来", "project_id": 11, "title": "市级代表性传承人"},
    {"id": 114, "name": "王兰英", "project_id": 12, "title": "省级代表性传承人"},
    {"id": 115, "name": "陆琴", "project_id": 13, "title": "市级代表性传承人"},
    {"id": 116, "name": "夏雨生", "project_id": 14, "title": "市级代表性传承人"},
]

# 项目演示资料（tags/materials/works/folk_customs，MySQL 无对应列，
# 由非遗内容接口在响应时补充；图谱节点数据来源于此）
DEMO_PROJECT_PROFILES: dict[int, dict[str, Any]] = {
    1: {
        "tags": ["第一批国家级", "传统美术", "示范性流派"],
        "materials": ["宣纸", "彩纸", "剪刀"],
        "works": ["《百鸟朝凤》剪纸屏风", "《扬州八怪》故事剪纸"],
        "folk_customs": ["春节剪窗花", "婚嫁剪喜花"],
    },
    2: {
        "tags": ["第一批国家级", "传统美术", "山子雕"],
        "materials": ["和田玉", "翡翠", "岫岩玉"],
        "works": ["《大禹治水图》玉山", "《聚珍图》碧玉山子"],
        "folk_customs": ["玉器庙会"],
    },
    3: {
        "tags": ["第一批国家级", "传统技艺", "雕漆嵌玉"],
        "materials": ["大漆", "螺钿", "金银箔", "楠木胎"],
        "works": ["《松鹤延年》雕漆地屏", "点螺《锦绣河山》漆器屏风"],
        "folk_customs": ["嫁女陪嫁漆器家具"],
    },
    4: {
        "tags": ["第一批国家级", "曲艺", "书场文化"],
        "materials": ["折扇", "醒木"],
        "works": ["《水浒》评话系列", "《三国》评话系列"],
        "folk_customs": ["茶馆听书"],
    },
    5: {
        "tags": ["第一批国家级", "传统戏剧", "江苏代表剧种"],
        "materials": ["戏曲服饰", "锣鼓弦乐"],
        "works": ["《百岁挂帅》", "《珍珠塔》"],
        "folk_customs": ["庙会戏台演出"],
    },
    6: {
        "tags": ["第一批国家级", "曲艺", "曲牌连缀体"],
        "materials": ["琵琶", "三弦", "瓷碟", "酒杯"],
        "works": ["《扬州月》清曲组歌", "《茉莉花》早期曲调遗存"],
        "folk_customs": ["堂会唱曲"],
    },
    7: {
        "tags": ["第二批国家级", "传统音乐", "人类非遗代表作"],
        "materials": ["桐木面板", "梓木底板", "蚕丝弦"],
        "works": ["《平沙落雁》", "《梅花三弄》"],
        "folk_customs": ["文人雅集"],
    },
    8: {
        "tags": ["江苏省级", "传统美术", "仿古山水绣"],
        "materials": ["绢", "桑蚕丝线", "绷架"],
        "works": ["《韩熙载夜宴图》刺绣长卷", "《富春山居图》仿古绣"],
        "folk_customs": ["嫁女绣帐"],
    },
    9: {
        "tags": ["江苏省级", "传统技艺", "天然植物染"],
        "materials": ["蓝草", "土白布", "豆粉", "石灰"],
        "works": ["《凤穿牡丹》蓝印花布被面", "《五福捧寿》帐檐"],
        "folk_customs": ["婚嫁备蓝印花布嫁妆"],
    },
    10: {
        "tags": ["第二批国家级", "传统技艺", "扬州早茶"],
        "materials": ["面粉", "西湖龙井", "魁针", "珠兰"],
        "works": ["三丁包", "翡翠烧卖", "魁龙珠茶"],
        "folk_customs": ["扬州早茶"],
    },
    11: {
        "tags": ["江苏省级", "传统戏剧", "内扦木偶"],
        "materials": ["樟木", "锦缎", "丝线"],
        "works": ["《嫦娥奔月》", "《火焰山》"],
        "folk_customs": ["节庆木偶戏台"],
    },
    12: {
        "tags": ["江苏省级", "传统音乐", "里下河民歌"],
        "materials": ["民歌曲调", "方言唱词"],
        "works": ["《数鸭蛋》", "《撒趟子撂在外》"],
        "folk_customs": ["秧歌会"],
    },
    13: {
        "tags": ["江苏省级", "民俗", "生活技艺"],
        "materials": ["厨刀", "修脚刀", "剃头刀"],
        "works": ["大煮干丝刀工", "陆三足艺"],
        "folk_customs": ["扬州澡堂文化", "扬州早茶"],
    },
    14: {
        "tags": ["江苏省级", "传统医药", "中医世家"],
        "materials": ["中草药", "汤剂"],
        "works": ["夏氏验方集"],
        "folk_customs": ["冬令进补膏方"],
    },
}

# 图谱关系链接（与 init.cypher 第 3 节一致；作品 [:CREATED] 关系在拥有
# Work 节点数据时可扩展，演示数据不包含 Work 节点）
GRAPH_DYNASTY_LINKS: dict[int, list[str]] = {
    1: ["唐宋"],
    2: ["明清"],
    3: ["明清"],
    4: ["明清"],
    5: ["近现代"],
    7: ["明清"],
    10: ["近现代"],
}
GRAPH_MATERIAL_LINKS: dict[int, list[str]] = {
    1: ["宣纸彩纸"],
    2: ["和田玉石"],
    3: ["大漆螺钿"],
}
GRAPH_CUSTOM_LINKS: dict[int, list[str]] = {
    1: ["春节窗花"],
    10: ["扬州早茶"],
    13: ["扬州早茶", "澡堂文化"],
}


class GraphService:
    """知识图谱服务：Neo4j 优先，失败/无数据时降级内存演示数据。

    使用官方 neo4j 驱动；GraphService.run() 模拟原 py2neo Graph.run 的
    记录迭代行为，内部查询逻辑保持不变。
    """

    def __init__(self) -> None:
        self.driver: Optional[Any] = None
        self._connect()

    # ---------- 连接 ----------
    def _connect(self) -> None:
        """尝试连接 Neo4j；未配置或失败时保持降级模式。"""
        url = settings.neo4j_url
        user, password = settings.neo4j_auth
        if not url or not user or not password:
            logger.info("未配置 Neo4j，知识图谱使用内存演示数据")
            return
        try:
            from neo4j import GraphDatabase  # 延迟导入，未安装驱动时也可启动

            self.driver = GraphDatabase.driver(url, auth=(user, password))
            self.driver.verify_connectivity()
            logger.info("Neo4j 连接成功：%s", url)
        except Exception as exc:  # noqa: BLE001 - 连接失败统一降级
            logger.warning("Neo4j 连接失败，知识图谱降级为内存演示数据：%s", exc)
            self.driver = None

    @property
    def available(self) -> bool:
        """Neo4j 是否可用。"""
        return self.driver is not None

    def run(self, cypher: str, **params: Any) -> list[Any]:
        """执行 Cypher 并返回记录列表（替代原 py2neo Graph.run 的结果迭代）。"""
        if self.driver is None:
            return []
        with self.driver.session() as session:
            return list(session.run(cypher, params))

    # ---------- 图谱查询 ----------
    def get_graph(
        self, category: Optional[str] = None, region: Optional[str] = None, depth: int = 2
    ) -> dict[str, Any]:
        """获取知识图谱：{nodes:[{id,name,type,refId}], edges:[{source,target,label}]}。

        :param category: 按类别名称过滤（空不过滤）
        :param region: 按地区关键字过滤（空不过滤）
        :param depth: 遍历深度（1 = 直接邻居，2 = 两跳邻居）
        """
        if self.available:
            try:
                data = self._query_neo4j(category, region, depth)
                if data["nodes"]:
                    return data
                logger.info("Neo4j 中暂无 Heritage 节点，回退内存演示图谱")
            except Exception as exc:  # noqa: BLE001 - 查询失败降级
                logger.warning("Neo4j 查询失败，回退内存演示图谱：%s", exc)
        return self._build_memory_graph(category, region, depth)

    def get_project_graph(self, project_id: int) -> dict[str, Any]:
        """获取单个非遗项目的子图谱。"""
        if self.available:
            try:
                data = self._query_neo4j_project(project_id)
                if data["nodes"]:
                    return data
            except Exception as exc:  # noqa: BLE001 - 查询失败降级
                logger.warning("Neo4j 项目子图查询失败，回退内存演示图谱：%s", exc)
        return self._build_memory_graph(project_ids=[project_id], depth=2)

    # ---------- Neo4j 实现 ----------
    def _query_neo4j(
        self, category: Optional[str], region: Optional[str], depth: int
    ) -> dict[str, Any]:
        """Cypher 查询全图（按类别/地区过滤）。

        无过滤时仅取 60 个代表项目，有过滤时限 120 个，避免全量
        （8203 节点）返回导致移动端渲染卡死。
        """
        params: dict[str, Any] = {
            "category": category or "",
            "region": region or "",
            "limit": 120 if (category or region) else 60,
        }
        limit_clause = "WITH h LIMIT $limit "
        if depth >= 2:
            cypher = """
                MATCH (h:Heritage)
                WHERE ($category = '' OR h.category = $category)
                  AND ($region = '' OR h.region CONTAINS $region)
                %s
                OPTIONAL MATCH (h)-[r1]-(n1)
                OPTIONAL MATCH (n1)-[r2]-(n2)
                    WHERE NOT n1:Category
                RETURN h AS center,
                       collect(DISTINCT n1) AS nodes1,
                       collect(DISTINCT n2) AS nodes2,
                       collect(DISTINCT r1) AS rels1,
                       collect(DISTINCT r2) AS rels2
            """ % limit_clause
        else:
            cypher = """
                MATCH (h:Heritage)
                WHERE ($category = '' OR h.category = $category)
                  AND ($region = '' OR h.region CONTAINS $region)
                %s
                OPTIONAL MATCH (h)-[r1]-(n1)
                RETURN h AS center,
                       collect(DISTINCT n1) AS nodes1,
                       [] AS nodes2,
                       [] AS rels2,
                       collect(DISTINCT r1) AS rels1
            """ % limit_clause
        result = self.run(cypher, **params)
        return self._assemble(result)

    def _query_neo4j_project(self, project_id: int) -> dict[str, Any]:
        """Cypher 查询单个项目的子图。"""
        cypher = """
            MATCH (h:Heritage {id: $id})
            OPTIONAL MATCH (h)-[r]-(n)
            RETURN h AS center, collect(DISTINCT n) AS nodes1, collect(DISTINCT r) AS rels1
        """
        result = self.run(cypher, id=project_id)
        return self._assemble(result)

    def _assemble(self, result: Any) -> dict[str, Any]:
        """将 Cypher 结果组装为统一节点/边结构。"""
        nodes: dict[int, dict[str, Any]] = {}
        edges: list[dict[str, str]] = []
        seen_edges: set[tuple[int, int, str]] = set()

        def register(node: Any) -> Optional[dict[str, Any]]:
            if node is None:
                return None
            node_dict = self._node_to_dict(node)
            if node_dict:
                nodes[node.element_id] = node_dict
            return node_dict

        for record in result:
            register(record["center"])
            for node in record.get("nodes1") or []:
                register(node)
            for node in record.get("nodes2") or []:
                register(node)
            for rel in list(record.get("rels1") or []) + list(record.get("rels2") or []):
                source = nodes.get(rel.start_node.element_id)
                target = nodes.get(rel.end_node.element_id)
                if not source or not target:
                    continue
                rel_type = rel.type
                key = (rel.start_node.element_id, rel.end_node.element_id, rel_type)
                if key in seen_edges:
                    continue
                seen_edges.add(key)
                edges.append(
                    {
                        "source": source["id"],
                        "target": target["id"],
                        "label": RELATION_LABELS.get(rel_type, rel_type),
                    }
                )
        return {"nodes": list(nodes.values()), "edges": edges}

    @staticmethod
    def _node_to_dict(node: Any) -> Optional[dict[str, Any]]:
        """neo4j 驱动 Node → 前端节点结构（id 前缀与前端约定一致）。"""
        labels = set(node.labels)
        if not labels:
            return None
        node_type = sorted(labels)[0].lower()
        props = dict(node)
        name = str(props.get("name", ""))
        ref_id: Optional[int] = None
        if node_type == "heritage":
            ref_id = props.get("id")
            node_id = f"h{ref_id}"
        elif node_type == "inheritor":
            ref_id = props.get("id")
            node_id = f"i{ref_id}"
        elif node_type == "category":
            node_id = (
                f"c{CATEGORY_ORDER.index(name) + 1}" if name in CATEGORY_ORDER else f"c_{name}"
            )
        elif node_type == "dynasty":
            node_id = (
                f"d{DYNASTY_ORDER.index(name) + 1}" if name in DYNASTY_ORDER else f"d_{name}"
            )
        elif node_type == "material":
            node_id = (
                f"m{MATERIAL_ORDER.index(name) + 1}" if name in MATERIAL_ORDER else f"m_{name}"
            )
        elif node_type == "folkcustom":
            node_id = (
                f"f{FOLK_CUSTOM_ORDER.index(name) + 1}"
                if name in FOLK_CUSTOM_ORDER
                else f"f_{name}"
            )
        else:  # work 等其他类型
            node_id = f"w_{name}"
        return {"id": node_id, "name": name, "type": node_type, "refId": ref_id}

    # ---------- 内存降级图谱 ----------
    def _build_memory_graph(
        self,
        category: Optional[str] = None,
        region: Optional[str] = None,
        depth: int = 2,
        project_ids: Optional[list[int]] = None,
    ) -> dict[str, Any]:
        """从 MySQL 业务数据构建图谱（Neo4j 不可用时的降级数据源）。

        优先读取数据库中的全国非遗数据；数据库为空时回退到内置演示数据。
        全国数据量大，前端全量渲染会卡死，故此处也按 category/region 过滤，
        且无过滤时限制返回数量（避免单次返回数千节点）。
        """
        projects, inheritors = self._load_memory_projects()

        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, str]] = []
        seen_edges: set[tuple[str, str, str]] = set()

        def add_node(node_id: str, name: str, node_type: str, ref_id: Optional[int] = None) -> None:
            if node_id not in nodes:
                nodes[node_id] = {"id": node_id, "name": name, "type": node_type, "refId": ref_id}

        def add_edge(source: str, target: str, label: str) -> None:
            key = (source, target, label)
            if key not in seen_edges:
                seen_edges.add(key)
                edges.append({"source": source, "target": target, "label": label})

        # 项目过滤
        if project_ids is not None:
            projects = [p for p in projects if p["id"] in project_ids]
        if category:
            projects = [p for p in projects if p["category"] == category]
        if region:
            projects = [p for p in projects if region in (p["region"] or "")]

        # 无过滤时限制数量：每类别取代表项目，避免全量返回导致前端卡死
        if not category and not region and project_ids is None:
            per_cat: dict[str, list[dict]] = {}
            for p in projects:
                per_cat.setdefault(p["category"], []).append(p)
            projects = []
            for items in per_cat.values():
                projects.extend(items[:5])
        # 指定类别/项目时也限流，避免单类别数百项目节点渲染卡顿
        elif len(projects) > 120:
            projects = projects[:120]

        # 类别节点（仅保留被选中项目涉及的类别）
        for category_name in sorted({p["category"] for p in projects}):
            add_node("c_" + category_name, category_name, "category")

        for project in projects:
            pid = project["id"]
            heritage_id = f"h{pid}"
            add_node(heritage_id, project["name"], "heritage", ref_id=pid)
            add_edge(heritage_id, "c_" + project["category"], RELATION_LABELS["BELONGS_TO_CATEGORY"])

            # 传承人 → 项目（每项目最多 5 位，控制节点规模）
            person_count = 0
            for person in inheritors:
                if person["project_id"] == pid:
                    if person_count >= 5:
                        break
                    inheritor_id = f"i{person['id']}"
                    add_node(inheritor_id, person["name"], "inheritor", ref_id=person["id"])
                    add_edge(inheritor_id, heritage_id, RELATION_LABELS["INHERITS"])
                    person_count += 1

        return {"nodes": list(nodes.values()), "edges": edges}

    def _load_memory_projects(self) -> "tuple[list[dict], list[dict]]":
        """加载内存图谱的项目/传承人数据：优先 MySQL，空则回退演示数据。"""
        try:
            session = SessionLocal()
            try:
                db_projects = session.execute(select(HeritageProject)).scalars().all()
                if db_projects:
                    projects = [
                        {
                            "id": p.id,
                            "name": p.name,
                            "category": p.category,
                            "region": p.region or "",
                        }
                        for p in db_projects
                    ]
                    db_inheritors = session.execute(select(Inheritor)).scalars().all()
                    inheritors = [
                        {
                            "id": i.id,
                            "name": i.name,
                            "project_id": i.project_id,
                            "title": i.title or "",
                        }
                        for i in db_inheritors
                    ]
                    return projects, inheritors
            finally:
                session.close()
        except Exception as exc:  # noqa: BLE001 - 数据库不可用则回退演示数据
            logger.warning("内存图谱读取数据库失败，回退演示数据：%s", exc)
        # 回退内置演示数据
        demo_inheritors = [
            {"id": i["id"], "name": i["name"], "project_id": i["project_id"], "title": i["title"]}
            for i in DEMO_INHERITORS
        ]
        return DEMO_PROJECTS, demo_inheritors

    # ---------- MySQL → Neo4j 同步 ----------
    def sync_from_mysql(self, session: Optional[Session] = None) -> bool:
        """从 MySQL 数据构建图谱（MERGE 语义，可重复执行）。

        Neo4j 不可用时直接跳过（返回 False），不影响其他服务。
        """
        if not self.available:
            logger.info("Neo4j 不可用，跳过图谱同步（接口使用内存演示数据）")
            return False
        owns_session = session is None
        if session is None:
            session = SessionLocal()
        try:
            projects = session.execute(select(HeritageProject)).scalars().all()
            for project in projects:
                self._merge_project(project)
            inheritors = session.execute(select(Inheritor)).scalars().all()
            for person in inheritors:
                self._merge_inheritor(person)
            logger.info(
                "Neo4j 图谱同步完成：%d 个项目 / %d 位传承人", len(projects), len(inheritors)
            )
            return True
        except Exception as exc:  # noqa: BLE001 - 同步失败仅告警
            logger.warning("Neo4j 图谱同步失败：%s", exc)
            return False
        finally:
            if owns_session:
                session.close()

    def _merge_project(self, project: HeritageProject) -> None:
        """MERGE 项目节点及其类别/朝代/材料/民俗关系。"""
        self.run(
            """
            MERGE (h:Heritage {id: $id})
            SET h.name = $name, h.level = $level, h.category = $category, h.region = $region
            MERGE (c:Category {name: $category})
            MERGE (h)-[:BELONGS_TO_CATEGORY]->(c)
            FOREACH (d IN $dynasties |
                MERGE (dn:Dynasty {name: d})
                MERGE (h)-[:PREVAILED_IN]->(dn))
            FOREACH (m IN $materials |
                MERGE (mt:Material {name: m})
                MERGE (h)-[:USES_MATERIAL]->(mt))
            FOREACH (f IN $customs |
                MERGE (fc:FolkCustom {name: f})
                MERGE (h)-[:ASSOCIATED_WITH]->(fc))
            """,
            id=project.id,
            name=project.name,
            level=project.level,
            category=project.category,
            region=project.region,
            dynasties=GRAPH_DYNASTY_LINKS.get(project.id, []),
            materials=GRAPH_MATERIAL_LINKS.get(project.id, []),
            customs=GRAPH_CUSTOM_LINKS.get(project.id, []),
        )

    def _merge_inheritor(self, person: Inheritor) -> None:
        """MERGE 传承人节点与 [:INHERITS] 关系。"""
        self.run(
            """
            MERGE (i:Inheritor {id: $id})
            SET i.name = $name, i.title = $title
            WITH i
            MATCH (h:Heritage {id: $project_id})
            MERGE (i)-[:INHERITS]->(h)
            """,
            id=person.id,
            name=person.name,
            title=person.title or "",
            project_id=person.project_id,
        )


# 全局单例
graph_service = GraphService()
