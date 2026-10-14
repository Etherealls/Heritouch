# -*- coding: utf-8 -*-
"""从 data/seed_national.json 统一生成全部全国数据文件。

一次性产出：
1. mobile-app/api/mock/national-data.js   —— 前端 Mock 全国数据（精简字段，控制体积）
2. database/mysql/seed_national.sql       —— MySQL 全国种子数据
3. database/neo4j/init_national.cypher    —— Neo4j 全国知识图谱

数据源：data/seed_national.json（由 build_seed_national.py 生成，4234 项目 + 3959 传承人）。

设计要点：
- 全国数据缺 history/craft/works/folk_customs 等演示富字段，统一置空；
  tags 由 level/category/batch 派生，materials 留空数组（推荐算法退化为同类/同地区）。
- 前端 mock 体积控制：项目 intro 截断为 120 字、传承人 biography 截断 100 字，
  完整文本保留在后端 MySQL（详情页走真实服务器时拿到全文）。
- 图谱数据量大（8000+ 节点），前端全量渲染会卡死，故前端 graphData 只保留
  「类别 → 代表项目」的稀疏概览图，分类子图由 getKnowledgeGraph 动态裁剪。

用法：python scripts/build_all_data.py
"""
from __future__ import annotations

import io
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")
SRC = os.path.join(DATA, "seed_national.json")

# 前端 mock 截断长度
INTRO_LIMIT = 120
BIO_LIMIT = 100

# 类别固定顺序与图标（非遗十大门类）
CATEGORY_META = [
    ("传统技艺", "🔨"),
    ("传统美术", "🎨"),
    ("传统戏剧", "🎭"),
    ("传统音乐", "🎵"),
    ("曲艺", "📢"),
    ("传统舞蹈", "💃"),
    ("民间文学", "📖"),
    ("民俗", "🏮"),
    ("传统医药", "🌿"),
    ("传统体育、游艺与杂技", "🤸"),
    ("其他", "🏷️"),
]


def load():
    with io.open(SRC, encoding="utf-8") as f:
        return json.load(f)


def truncate(text, limit):
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit] + "…"


def sql_escape(text):
    return (text or "").replace("\\", "\\\\").replace("'", "''")


def cypher_escape(text):
    return (text or "").replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")


# =====================================================================
# 1. 前端 Mock 数据
# =====================================================================
def build_frontend(projects, inheritors):
    """生成 national-data.js（前端 Mock，精简字段）。"""
    # 类别聚合
    cat_count = {}
    for p in projects:
        cat_count[p["category"]] = cat_count.get(p["category"], 0) + 1

    categories = []
    for name, icon in CATEGORY_META:
        if name in cat_count:
            categories.append({"id": len(categories) + 1, "name": name, "icon": icon, "count": cat_count[name]})

    # 项目精简字段（保留前端必需字段）
    fe_projects = []
    for p in projects:
        fe_projects.append(
            {
                "id": p["id"],
                "name": p["name"],
                "level": p["level"],
                "category": p["category"],
                "region": p["region"],
                "batch": p.get("batch"),
                "intro": truncate(p.get("intro"), INTRO_LIMIT),
                "history": "",
                "craft": "",
                "tags": [t for t in [p["level"], p["category"], f'{p.get("batch") or ""}年' if p.get("batch") else ""] if t],
                "materials": [],
                "works": [],
                "folk_customs": [],
                "inheritors": [],
            }
        )

    # 传承人（id 沿用 project_id 关联；前端需独立 id，这里按 10000+ 序生成）
    fe_inheritors = []
    project_inheritor_map = {}
    for i, it in enumerate(inheritors, start=1):
        iid = 10000 + i
        fe_inheritors.append(
            {
                "id": iid,
                "name": it["name"],
                "project_id": it["project_id"],
                "title": it.get("title", "国家级代表性传承人"),
                "gender": it.get("gender") or "",
                "biography": truncate(it.get("biography"), BIO_LIMIT),
                "photo": "",
            }
        )
        project_inheritor_map.setdefault(it["project_id"], []).append(iid)

    for p in fe_projects:
        p["inheritors"] = project_inheritor_map.get(p["id"], [])

    # 图谱稀疏概览：类别节点 + 每类取前 3 个代表项目
    graph_nodes = []
    graph_edges = []
    cat_name_to_id = {}
    for c in categories:
        cid = "c" + str(c["id"])
        cat_name_to_id[c["name"]] = cid
        graph_nodes.append({"id": cid, "name": c["name"], "type": "category"})
    per_cat = {}
    for p in projects:
        per_cat.setdefault(p["category"], []).append(p)
    for cname, cid in cat_name_to_id.items():
        for p in per_cat.get(cname, [])[:3]:
            hid = "h" + str(p["id"])
            graph_nodes.append({"id": hid, "name": p["name"], "type": "heritage", "refId": p["id"]})
            graph_edges.append({"source": hid, "target": cid, "label": "归属"})

    body = {
        "categories": categories,
        "projects": fe_projects,
        "inheritors": fe_inheritors,
        "graphData": {"nodes": graph_nodes, "edges": graph_edges},
    }

    lines = [
        "/**",
        " * 全国非遗数据（Mock 数据源，由 scripts/build_all_data.py 自动生成，勿手改）",
        " * 数据来源：中国非物质文化遗产网（ihchina.cn）公开名录",
        f" * 规模：{len(fe_projects)} 个项目 / {len(fe_inheritors)} 位传承人 / {len(categories)} 个类别",
        " */",
        "/* eslint-disable */",
    ]
    for key in ["categories", "projects", "inheritors", "graphData"]:
        lines.append(f"export const {key} = {json.dumps(body[key], ensure_ascii=False, separators=(',', ':'))}")
    lines.append("export default { categories, projects, inheritors, graphData }")
    return "\n".join(lines) + "\n", len(fe_projects), len(fe_inheritors), len(categories)


# =====================================================================
# 2. MySQL seed_national.sql
# =====================================================================
def build_mysql(projects, inheritors):
    lines = [
        "-- =====================================================================",
        "-- Heritouch —— MySQL 全国非遗种子数据（由 build_all_data.py 自动生成）",
        "-- 数据来源：中国非物质文化遗产网（ihchina.cn）公开名录",
        f"-- 规模：{len(projects)} 个项目 / {len(inheritors)} 位传承人",
        "-- 用法：mysql -u root -p heritouch < seed_national.sql",
        "-- =====================================================================",
        "",
        "USE `heritouch`;",
        "",
        "-- 一、非遗项目",
        "INSERT INTO `heritage_project`",
        "  (`id`, `name`, `level`, `category`, `region`, `batch`, `intro`, `history`, `craft`,",
        "   `cover_image`, `audio_mandarin`, `audio_dialect`, `qrcode`, `latitude`, `longitude`) VALUES",
    ]
    rows = []
    for p in projects:
        rows.append(
            "({}, '{}', '{}', '{}', '{}', {}, '{}', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)".format(
                p["id"],
                sql_escape(p["name"]),
                sql_escape(p["level"]),
                sql_escape(p["category"]),
                sql_escape(p["region"]),
                p.get("batch") if p.get("batch") else "NULL",
                sql_escape(p.get("intro")),
            )
        )
    lines.append(",\n".join(rows) + ";")
    lines.append("")
    lines.append("-- 二、传承人")
    lines.append("INSERT INTO `inheritor` (`name`, `gender`, `project_id`, `title`, `biography`, `photo`) VALUES")
    irows = []
    for it in inheritors:
        irows.append(
            "('{}', '{}', {}, '{}', '{}', NULL)".format(
                sql_escape(it["name"]),
                sql_escape(it.get("gender") or ""),
                it["project_id"],
                sql_escape(it.get("title", "国家级代表性传承人")),
                sql_escape(it.get("biography")),
            )
        )
    lines.append(",\n".join(irows) + ";")
    return "\n".join(lines) + "\n"


# =====================================================================
# 3. Neo4j init_national.cypher
# =====================================================================
def build_cypher(projects, inheritors):
    lines = [
        "// =====================================================================",
        "// Heritouch —— Neo4j 全国知识图谱初始化（由 build_all_data.py 自动生成）",
        f"// 规模：{len(projects)} 个项目 / {len(inheritors)} 位传承人",
        "// 用法：cypher-shell -a bolt://localhost:7687 -u neo4j -p password -f init_national.cypher",
        "// =====================================================================",
        "",
        "MATCH (n) DETACH DELETE n;",
        "",
        "CREATE CONSTRAINT heritage_id_unique IF NOT EXISTS FOR (h:Heritage) REQUIRE h.id IS UNIQUE;",
        "CREATE CONSTRAINT inheritor_id_unique IF NOT EXISTS FOR (i:Inheritor) REQUIRE i.id IS UNIQUE;",
        "CREATE CONSTRAINT category_name_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE;",
        "",
        "// ---- 类别 ----",
    ]
    cat_names = sorted({p["category"] for p in projects})
    lines.append("UNWIND " + json.dumps(cat_names, ensure_ascii=False) + " AS name")
    lines.append("CREATE (c:Category {name: name});")
    lines.append("")
    lines.append("// ---- 项目 ----")
    lines.append("UNWIND [")
    prows = []
    for p in projects:
        prows.append(
            "  {{id: {}, name: '{}', level: '{}', category: '{}', region: '{}', batch: {}}}".format(
                p["id"],
                cypher_escape(p["name"]),
                cypher_escape(p["level"]),
                cypher_escape(p["category"]),
                cypher_escape(p["region"]),
                p.get("batch") if p.get("batch") else "null",
            )
        )
    lines.append(",\n".join(prows))
    lines.append("] AS row")
    lines.append("CREATE (h:Heritage {id: row.id, name: row.name, level: row.level, category: row.category, region: row.region, batch: row.batch});")
    lines.append("")
    lines.append("// ---- 传承人 ----")
    lines.append("UNWIND [")
    irows = []
    for i, it in enumerate(inheritors, start=1):
        irows.append(
            "  {{id: {}, name: '{}', project_id: {}, title: '{}'}}".format(
                i, cypher_escape(it["name"]), it["project_id"], cypher_escape(it.get("title", "国家级代表性传承人"))
            )
        )
    lines.append(",\n".join(irows))
    lines.append("] AS row")
    lines.append("CREATE (i:Inheritor {id: row.id, name: row.name, project_id: row.project_id, title: row.title});")
    lines.append("")
    lines.append("// ---- 关系：项目 → 类别 ----")
    lines.append("MATCH (h:Heritage), (c:Category)")
    lines.append("WHERE h.category = c.name")
    lines.append("CREATE (h)-[:BELONGS_TO_CATEGORY]->(c);")
    lines.append("")
    lines.append("// ---- 关系：传承人 → 项目 ----")
    lines.append("MATCH (i:Inheritor), (h:Heritage)")
    lines.append("WHERE i.project_id = h.id")
    lines.append("CREATE (i)-[:INHERITS]->(h);")
    return "\n".join(lines) + "\n"


def main():
    if not os.path.exists(SRC):
        raise SystemExit(f"数据源不存在：{SRC}\n请先运行 scripts/crawl_ihchina.py 与 scripts/build_seed_national.py")
    data = load()
    projects = data["projects"]
    inheritors = data["inheritors"]
    print(f"数据源：{len(projects)} 项目 / {len(inheritors)} 传承人")

    # 1. 前端
    fe, np, ni, nc = build_frontend(projects, inheritors)
    fe_path = os.path.join(ROOT, "..", "mobile-app", "api", "mock", "national-data.js")
    with io.open(fe_path, "w", encoding="utf-8") as f:
        f.write(fe)
    print(f"✅ 前端 mock：{fe_path}（{np} 项目 / {ni} 传承人 / {nc} 类别）")

    # 2. MySQL
    sql = build_mysql(projects, inheritors)
    sql_path = os.path.join(ROOT, "..", "database", "mysql", "seed_national.sql")
    with io.open(sql_path, "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"✅ MySQL：{sql_path}")

    # 3. Neo4j
    cyp = build_cypher(projects, inheritors)
    cyp_path = os.path.join(ROOT, "..", "database", "neo4j", "init_national.cypher")
    with io.open(cyp_path, "w", encoding="utf-8") as f:
        f.write(cyp)
    print(f"✅ Neo4j：{cyp_path}")

    # 体积统计
    for path in (fe_path, sql_path, cyp_path):
        size = os.path.getsize(path)
        print(f"   {os.path.basename(path)}: {size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
