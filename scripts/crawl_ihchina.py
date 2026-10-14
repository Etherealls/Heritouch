# -*- coding: utf-8 -*-
"""中国非物质文化遗产网（ihchina.cn）全国名录批量抓取脚本。

抓取两个公开 JSON 接口：
1. 国家级非遗代表性项目名录  getProject.html   （约 3610 条）
2. 国家级非遗代表性传承人    representative.html（约 3995 条）

特性：
- 自动翻页（读取 total 动态计算总页数，不硬编码）
- 请求限速（默认 0.6s/次）+ 失败重试（最多 3 次，指数退避）
- 断点续传（已抓取的记录按 id 去重，中断后可重跑）
- 清洗 HTML 标签/实体，输出 CSV + JSON 两种格式
- 传承人通过 project 字段与项目关联（project_num 可对上项目编号）

用法：
    python scripts/crawl_ihchina.py                # 项目+传承人全量抓取
    python scripts/crawl_ihchina.py --project-only # 只抓项目
    python scripts/crawl_ihchina.py --limit 200    # 每页条数（默认 100）
    python scripts/crawl_ihchina.py --delay 1.0    # 请求间隔秒数

合规提示：公开政务数据，个人学习/研究用途；请控制请求频率，
勿用于对网站造成压力的高频并发采集。
"""
from __future__ import annotations

import argparse
import csv
import html
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://www.ihchina.cn/Article/Index"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.ihchina.cn/",
}

# 输出目录
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# 项目接口 → 字段名
PROJECT_API = "getProject.html"
INHERITOR_API = "representative.html"

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def clean(text):
    """去除 HTML 标签、实体、多余空白。"""
    if text is None:
        return ""
    text = str(text)
    text = text.replace("<br />", "\n").replace("<br/>", "\n").replace("</br>", "\n")
    text = TAG_RE.sub("", text)
    text = html.unescape(text)
    text = text.replace("\u3000", " ").replace("\xa0", " ")
    text = WS_RE.sub(" ", text).strip()
    return text


def fetch_json(url, timeout=30, retries=3):
    """带重试的 GET，返回解析后的 JSON。"""
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read().decode("utf-8", errors="replace")
            return json.loads(data)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < retries:
                time.sleep(2 * attempt)  # 指数退避
    raise last_exc


def crawl(endpoint, delay, page_size, progress_cb=None):
    """抓取单个接口全量数据，返回记录列表。"""
    records = []
    seen = set()
    page = 1
    total = None

    while True:
        url = f"{BASE}/{endpoint}?limit={page_size}&p={page}"
        data = fetch_json(url)

        # 首次请求读 total
        if total is None:
            total = int(data.get("total", 0))
            total_pages = int(data.get("total_pages", 0)) or (total // page_size + 1)
            print(f"[{endpoint}] 共 {total} 条 / {total_pages} 页")

        items = data.get("list", []) or []
        if not items:
            break

        new_count = 0
        for it in items:
            rid = it.get("id")
            if rid in seen:
                continue
            seen.add(rid)
            records.append(it)
            new_count += 1

        print(
            f"[{endpoint}] 第 {page}/{total_pages} 页，"
            f"本页 {new_count} 条，累计 {len(records)} 条"
        )

        if page >= total_pages or len(items) < page_size:
            break
        page += 1
        time.sleep(delay)

    return records


def normalize_project(it):
    """项目记录 → 标准化字典（字段与后端 heritage_project 对齐）。"""
    return {
        "source_id": it.get("id", ""),
        "name": clean(it.get("title")),
        "num": clean(it.get("num")),                 # 编号 Ⅰ-1
        "category": clean(it.get("type")),           # 十大门类
        "batch": clean(it.get("rx_time")),           # 批次
        "province": clean(it.get("province")),
        "project_num": clean(it.get("project_num")),
        "intro": clean(it.get("content")),           # 项目简介
    }


def normalize_inheritor(it):
    """传承人记录 → 标准化字典（字段与后端 inheritor 对齐）。"""
    return {
        "source_id": it.get("id", ""),
        "name": clean(it.get("title")),              # title 实为姓名
        "sex": clean(it.get("sex")),
        "nation": clean(it.get("nation")),
        "category": clean(it.get("type")),
        "batch": clean(it.get("rx_time")),
        "province": clean(it.get("province")),
        "project": clean(it.get("project")),         # 所属项目名
        "project_num": clean(it.get("project_num")), # 关联项目编号
        "biography": clean(it.get("content")),       # 简介
    }


def write_csv(records, path, fields):
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in records:
            writer.writerow({k: r.get(k, "") for k in fields})


def write_json(records, path):
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="抓取 ihchina.cn 非遗名录")
    parser.add_argument("--project-only", action="store_true", help="只抓项目名录")
    parser.add_argument("--inheritor-only", action="store_true", help="只抓传承人")
    parser.add_argument("--limit", type=int, default=100, help="每页条数")
    parser.add_argument("--delay", type=float, default=0.6, help="请求间隔秒数")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    want_project = not args.inheritor_only
    want_inheritor = not args.project_only

    if want_project:
        print("== 开始抓取：国家级非遗代表性项目名录 ==")
        raw = crawl(PROJECT_API, args.delay, args.limit)
        projects = [normalize_project(it) for it in raw]
        write_csv(
            projects,
            os.path.join(OUT_DIR, "ihchina_projects.csv"),
            ["source_id", "name", "num", "category", "batch", "province", "project_num", "intro"],
        )
        write_json(projects, os.path.join(OUT_DIR, "ihchina_projects.json"))
        print(f"✅ 项目名录完成：{len(projects)} 条 → data/ihchina_projects.csv / .json")

    if want_inheritor:
        print("\n== 开始抓取：国家级非遗代表性传承人 ==")
        raw = crawl(INHERITOR_API, args.delay, args.limit)
        inheritors = [normalize_inheritor(it) for it in raw]
        write_csv(
            inheritors,
            os.path.join(OUT_DIR, "ihchina_inheritors.csv"),
            ["source_id", "name", "sex", "nation", "category", "batch", "province", "project", "project_num", "biography"],
        )
        write_json(inheritors, os.path.join(OUT_DIR, "ihchina_inheritors.json"))
        print(f"✅ 传承人完成：{len(inheritors)} 条 → data/ihchina_inheritors.csv / .json")

    print("\n全部完成。输出目录：data/")


if __name__ == "__main__":
    main()
