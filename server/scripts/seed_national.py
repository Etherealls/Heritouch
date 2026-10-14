# -*- coding: utf-8 -*-
"""全国非遗数据灌数脚本（可选，区别于默认的扬州演示数据）。

数据来源：中国非物质文化遗产网（ihchina.cn）公开名录，经
scripts/crawl_ihchina.py 抓取 + scripts/build_seed_national.py 转换，
存于 data/seed_national.json（4234 个项目 + 3959 位传承人）。

用法：
    # 在 server/ 目录下执行
    python -m scripts.seed_national          # 灌入全国数据
    python -m scripts.seed_national --force  # 已存在数据时清空重灌（慎用）

注意：
- 默认 seed_data.py 只灌 14 个扬州演示项目；本脚本灌全国全量数据，
  两者二选一（同表冲突）。若之前已运行 seed_data.py，请用 --force 清空后重灌。
"""
from __future__ import annotations

import argparse
import io
import json
import logging
import os
import sys

# 允许以 `python -m scripts.seed_national` 运行时正确导入 app 包
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models.heritage import HeritageProject, Inheritor  # noqa: E402

logger = logging.getLogger("heritouch.seed_national")

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "seed_national.json",
)


def load_data():
    with io.open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def _clip(text, limit):
    """截断到字段长度限制（防御脏数据）。"""
    if text is None:
        return None
    text = str(text)
    return text[: limit - 1] + "…" if len(text) > limit else text


def seed(force: bool = False) -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        existing = session.query(HeritageProject).count()
        if existing > 0 and not force:
            logger.warning(
                "数据库已存在 %d 个非遗项目。如需灌入全国数据，请加 --force（将清空现有项目与传承人）",
                existing,
            )
            return

        if force and existing > 0:
            logger.warning("--force：清空现有 %d 个项目及关联传承人", existing)
            session.query(Inheritor).delete()
            session.query(HeritageProject).delete()
            session.flush()

        data = load_data()
        projects = data["projects"]
        inheritors = data["inheritors"]

        # 1. 项目
        for p in projects:
            session.add(
                HeritageProject(
                    id=p["id"],
                    name=_clip(p["name"], 100),
                    level=_clip(p["level"], 20),
                    category=_clip(p["category"], 50),
                    region=_clip(p["region"], 50),
                    batch=p.get("batch"),
                    intro=p.get("intro") or None,
                )
            )
        session.flush()

        # 2. 传承人
        for it in inheritors:
            session.add(
                Inheritor(
                    name=_clip(it["name"], 50),
                    gender=(_clip(it.get("gender"), 2) or None),
                    project_id=it["project_id"],
                    title=_clip(it.get("title"), 50),
                    biography=it.get("biography") or None,
                )
            )

        session.commit()
        logger.info("全国数据灌入完成：%d 个项目 / %d 位传承人", len(projects), len(inheritors))
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="灌入全国非遗数据")
    parser.add_argument("--force", action="store_true", help="清空现有项目/传承人后重灌")
    args = parser.parse_args()

    if not os.path.exists(DATA_FILE):
        logger.error("数据文件不存在：%s。请先运行 scripts/build_seed_national.py", DATA_FILE)
        sys.exit(1)

    seed(force=args.force)


if __name__ == "__main__":
    main()
