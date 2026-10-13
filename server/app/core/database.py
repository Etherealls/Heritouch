"""SQLAlchemy 2.0 数据库引擎、会话与依赖。

降级策略：
- 未配置 DATABASE_URL 时直接使用 SQLite（开发默认，零配置可启动）；
- 配置了 MySQL 但连接失败且 SQLITE_FALLBACK=true 时，自动降级为 SQLite 并告警；
- SQLite 场景下关闭跨线程检查，适配 FastAPI 线程池同步端点。
"""
from __future__ import annotations

import logging
from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger("heritouch.database")


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 声明式基类，所有 ORM 模型继承自此。"""


def _mysql_reachable(url: str) -> bool:
    """测试 MySQL 连通性（执行 SELECT 1）。"""
    try:
        test_engine: Engine = create_engine(url, pool_pre_ping=True)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        test_engine.dispose()
        return True
    except Exception as exc:  # noqa: BLE001 - 任何连接异常都触发降级
        logger.warning("MySQL 连接失败（%s）", exc)
        return False


def resolve_database_url() -> str:
    """解析最终使用的数据库连接串，必要时降级为 SQLite。"""
    configured = (settings.DATABASE_URL or "").strip()
    if not configured:
        logger.info("未配置 DATABASE_URL，使用 SQLite：%s", settings.SQLITE_URL)
        return settings.SQLITE_URL
    if configured.startswith("mysql") and settings.SQLITE_FALLBACK:
        if _mysql_reachable(configured):
            return configured
        logger.warning("DATABASE_URL 指向 MySQL 但不可达，已降级为 SQLite：%s", settings.SQLITE_URL)
        return settings.SQLITE_URL
    return configured


DATABASE_URL: str = resolve_database_url()
IS_SQLITE: bool = DATABASE_URL.startswith("sqlite")

# 数据库引擎：开启连接池预 ping（断线重连）；SQLite 关闭同线程检查
engine: Engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
)

# 会话工厂：expire_on_commit=False 避免提交后属性过期需重新查询
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI 依赖：请求级数据库会话，结束后自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
