# -*- coding: utf-8 -*-
"""把 ihchina 抓取的全国数据（data/*.csv）转换成后端可灌数的 JSON。

输出：data/seed_national.json
结构：
{
  "projects":   [{name, level, category, region, batch, intro, num, project_num}],
  "inheritors": [{name, gender, project_num, title, biography}]
}

说明：
- 项目按抓取顺序重新编号（1..N），传承人通过 project_num 关联到项目；
- batch 从 "2006年（第一批）" 清洗为整数年份；
- 缺 category 的扩展项目（如刺绣类）用 project_num 前缀 / 名称兜底，
  仍无法判断时归入 "其他"；
- level 统一为 "国家级"（数据来源为国家级名录）。

用法：python scripts/build_seed_national.py
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "..", "data")

BATCH_YEAR_RE = re.compile(r"(\d{4})")
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

# project_num 前缀 → 类别兜底（应对列表接口缺失 category 的扩展项目）
NUM_CATEGORY_HINT = {
    "Ⅰ": "民间文学",
    "Ⅱ": "传统音乐",
    "Ⅲ": "传统舞蹈",
    "Ⅳ": "传统戏剧",
    "Ⅴ": "曲艺",
    "Ⅵ": "传统体育、游艺与杂技",
    "Ⅶ": "传统美术",
    "Ⅷ": "传统技艺",
    "Ⅸ": "传统医药",
    "Ⅹ": "民俗",
}


def read_csv(path):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clean_batch(text):
    """'2006年（第一批）' / '()' → 2006 或 None。"""
    m = BATCH_YEAR_RE.search(str(text or ""))
    return int(m.group(1)) if m else None


def clean_html(text):
    """去除 HTML 标签与多余空白。"""
    text = str(text or "")
    text = text.replace("<br />", " ").replace("<br/>", " ").replace("</p>", " ")
    text = TAG_RE.sub("", text)
    text = WS_RE.sub(" ", text).strip()
    return text


def clean_region(text, limit=50):
    """region 截断到数据库字段长度（String(50)）。"""
    text = clean_html(text)
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return text


def infer_category(project):
    """category 缺失时兜底：先按名称关键词，再按编号前缀。"""
    if project.get("category"):
        return project["category"].strip()
    name = project.get("name") or ""
    num = project.get("num") or project.get("project_num") or ""
    # 扩展项目（FRZX）多为刺绣类，且名称含"绣"字 → 传统美术
    if "FRZX" in num and ("绣" in name or "锦" in name):
        return "传统美术"
    for prefix, cat in NUM_CATEGORY_HINT.items():
        if num.startswith(prefix):
            return cat
    return "其他"


def norm_name(s):
    """归一化名称用于模糊匹配：去括号/空格，全角转半角。"""
    s = str(s or "")
    s = s.replace("（", "(").replace("）", ")")
    s = re.sub(r"[（）()\s]", "", s)
    return s.lower()


def main():
    projects = read_csv(os.path.join(DATA, "ihchina_projects.csv"))
    inheritors = read_csv(os.path.join(DATA, "ihchina_inheritors.csv"))

    # 建立映射：项目名称（含归一化）→ 新 id；project_num 名称 → 新 id
    name_to_id = {}
    norm_to_id = {}
    num_to_id = {}
    out_projects = []
    for idx, p in enumerate(projects, start=1):
        pnum = (p.get("project_num") or "").strip()
        name = (p.get("name") or "").strip()
        num_to_id.setdefault(pnum, idx)
        name_to_id.setdefault(name, idx)
        norm_to_id.setdefault(norm_name(name), idx)
        out_projects.append(
            {
                "id": idx,
                "name": name,
                "level": "国家级",
                "category": infer_category(p),
                "region": clean_region(p.get("province")),
                "batch": clean_batch(p.get("batch")),
                "intro": clean_html(p.get("intro")),
                "num": (p.get("num") or "").strip(),
                "project_num": pnum,
            }
        )

    # 传承人关联项目：优先精确名称 → 归一化名称 → project_num
    out_inheritors = []
    skipped = 0
    for i in inheritors:
        proj_name = (i.get("project") or "").strip()
        pid = (
            name_to_id.get(proj_name)
            or norm_to_id.get(norm_name(proj_name))
            or num_to_id.get((i.get("project_num") or "").strip())
        )
        if pid is None:
            skipped += 1
            continue
        out_inheritors.append(
            {
                "name": (i.get("name") or "").strip(),
                "gender": (i.get("sex") or "").strip()[:1],
                "project_id": pid,
                "project_num": (i.get("project_num") or "").strip(),
                "title": "国家级代表性传承人",
                "biography": (i.get("biography") or "").strip(),
            }
        )

    result = {"projects": out_projects, "inheritors": out_inheritors}
    out_path = os.path.join(DATA, "seed_national.json")
    with io.open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"项目 {len(out_projects)} 条 | 传承人 {len(out_inheritors)} 条 | 未匹配舍弃 {skipped} 条")
    print(f"输出：{out_path}")


if __name__ == "__main__":
    main()
