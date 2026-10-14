"""sys_user 表结构迁移：openid 体系 → 用户名 + 密码体系。

背景：用户登录方式从「微信 openid / 设备标识」改为「用户名 + 密码」，
sys_user 表字段由 (openid) 变为 (username, password_hash)。
SQLite 的 create_all 不会修改已存在的表，需手动迁移。

迁移策略（不丢失非遗/关卡等其他表数据）：
- SQLite：检测 sys_user 是否存在旧列 openid，存在则重建该表（旧演示用户数据
  会被丢弃，之后由 seed 重新灌入演示账号）；
- MySQL：提示用户手动执行 schema 变更（通常开发阶段用 SQLite，此分支仅告警）。

用法（在 server/ 目录下）：
    python scripts/migrate_user_table.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect, text  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.database import SessionLocal, engine, IS_SQLITE  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("migrate_user_table")


def _columns(table: str) -> set[str]:
    inspector = inspect(engine)
    return {col["name"] for col in inspector.get_columns(table)}


def main() -> int:
    tables = inspect(engine).get_table_names()
    if "sys_user" not in tables:
        logger.info("sys_user 表不存在，无需迁移（启动时 create_all 会自动按新结构建表）")
        return 0

    cols = _columns("sys_user")
    if "username" in cols and "password_hash" in cols:
        logger.info("sys_user 已是新结构（username/password_hash），无需迁移")
        return 0

    logger.info("检测到旧结构 sys_user（含 openid），开始迁移…")
    if not IS_SQLITE:
        logger.warning(
            "当前为 MySQL，请手动执行：ALTER TABLE sys_user "
            "DROP COLUMN openid, ADD COLUMN username VARCHAR(100), "
            "ADD COLUMN password_hash VARCHAR(255); "
            "并将 username 设为唯一键。本脚本不自动改 MySQL。"
        )
        return 1

    # SQLite：重建 sys_user 表（旧演示用户数据随旧表丢弃，由 seed 重新灌入）
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS sys_user"))
    logger.info("已删除旧 sys_user 表")

    # 重建（用 ORM 新结构）
    from app.models.user import SysUser  # noqa: E402
    from app.core.database import Base  # noqa: E402

    Base.metadata.create_all(bind=engine)
    logger.info("已按新结构重建 sys_user 表（username/password_hash）")

    # 重新灌入演示用户
    try:
        from app.core.security import hash_password
        from app.models.user import SysUser as SU

        demo_pwd = "123456"
        demo_users = [
            {"username": "admin", "nickname": "非遗管理员", "score": 0},
            {"username": "user1", "nickname": "非遗小达人", "score": 980},
            {"username": "user2", "nickname": "扬州小秀才", "score": 860},
            {"username": "user3", "nickname": "剪纸小传人", "score": 720},
            {"username": "user4", "nickname": "玉雕学徒", "score": 610},
            {"username": "user5", "nickname": "早茶常客", "score": 480},
        ]
        with SessionLocal() as session:
            for u in demo_users:
                session.add(
                    SU(
                        username=u["username"],
                        password_hash=hash_password(demo_pwd),
                        nickname=u["nickname"],
                        avatar="/static/images/avatar-placeholder.svg",
                        score=u["score"],
                    )
                )
            session.commit()
        logger.info("已重新灌入 6 个演示账号（用户名 admin/user1~user5，密码均为 123456）")
    except Exception as exc:  # noqa: BLE001
        logger.warning("灌入演示用户失败（可稍后运行 seed 脚本）：%s", exc)

    logger.info("✅ 迁移完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
