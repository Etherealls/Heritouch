"""Heritouch 后端应用入口。

职责：
- FastAPI 实例与 CORS 配置；
- 统一异常处理（HTTPException / 参数校验 / 未处理异常 → 统一 JSON）；
- 路由注册（统一前缀 /api/v1）；
- 健康检查与根路径欢迎信息；
- 启动事件：建表 → 条件种子数据 → Neo4j 图谱同步 → RAG 知识库加载
  （每一步均 try 包裹，失败仅告警不阻断启动，保证无配置可运行）。
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.services import ai_service, graph_service, rag_service, tts_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("heritouch")


def _startup() -> None:
    """启动初始化：任何一步失败都只告警，不阻断服务启动。"""
    # 1. 建表（MySQL 已由 schema.sql 建表时自动跳过）
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表结构就绪：%s", engine.url)
    except Exception as exc:  # noqa: BLE001 - 启动不阻断
        logger.error("数据库表创建失败：%s", exc)
        return

    # 2. 条件种子数据（数据库为空时写入扬州非遗演示数据）
    try:
        import sys
        from pathlib import Path

        # 保证 scripts 包可导入（无论 uvicorn 从哪个目录启动）
        server_root = str(Path(__file__).resolve().parent.parent)
        if server_root not in sys.path:
            sys.path.insert(0, server_root)
        from scripts.seed_data import seed_if_empty

        seed_if_empty()
    except Exception as exc:  # noqa: BLE001 - 启动不阻断
        logger.warning("种子数据初始化失败（不影响启动）：%s", exc)

    # 3. Neo4j 图谱同步（不可用时跳过，接口降级内存演示图谱）
    try:
        graph_service.sync_from_mysql()
    except Exception as exc:  # noqa: BLE001 - 启动不阻断
        logger.warning("知识图谱同步失败（不影响启动）：%s", exc)

    # 4. RAG 知识库加载（ChromaDB 不可用时降级关键词匹配）
    try:
        rag_service.sync_knowledge()
    except Exception as exc:  # noqa: BLE001 - 启动不阻断
        logger.warning("RAG 知识库加载失败（不影响启动）：%s", exc)

    logger.info(
        "服务状态：数据库=%s | Neo4j=%s | ChromaDB=%s | AI文本=%s | AI图像=%s | TTS=%s",
        "sqlite" if engine.url.get_backend_name() == "sqlite" else engine.url.get_backend_name(),
        graph_service.available,
        rag_service.enabled,
        ai_service.text.enabled,
        ai_service.image.enabled,
        tts_service.available,
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用生命周期：启动时执行初始化。"""
    _startup()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="地方非遗文化AI解码与传承平台 REST API（统一前缀 /api/v1）",
    lifespan=lifespan,
)

# ---------- CORS：多端（H5 / 小程序 / App）全开 ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- 静态资源（占位图 / TTS 音频等，目录缺失也不影响启动） ----------
try:
    from fastapi.staticfiles import StaticFiles

    app.mount("/static", StaticFiles(directory="static", check_dir=False), name="static")
except Exception as exc:  # noqa: BLE001 - 静态资源挂载失败不影响 API
    logger.warning("静态资源目录挂载失败：%s", exc)

# ---------- 路由注册 ----------
app.include_router(api_router, prefix="/api/v1")


# ---------- 统一异常处理 ----------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTPException → {"code": <状态码>, "message": <详情>, "data": null}。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": str(exc.detail), "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """请求参数校验失败 → 422 统一格式。"""
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": f"请求参数错误：{exc.errors()}", "data": None},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """未处理异常 → 500 统一格式（记录堆栈，不向前端泄露细节）。"""
    logger.exception("未处理异常：%s", exc)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误，请稍后重试", "data": None},
    )


# ---------- 健康检查与根路径 ----------
@app.get("/api/v1/health", summary="健康检查")
def health() -> dict:
    """返回服务与各外部依赖的运行状态。"""
    db_ok = False
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:  # noqa: BLE001 - 健康检查不抛异常
        pass
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "status": "ok",
            "version": settings.APP_VERSION,
            "services": {
                "database": db_ok,
                "neo4j": graph_service.available,
                "chromadb": rag_service.enabled,
                "ai_text": ai_service.text.enabled,
                "ai_image": ai_service.image.enabled,
                "tts": tts_service.available,
            },
        },
    }


@app.get("/", summary="根路径欢迎信息")
def root() -> dict:
    """服务欢迎信息与文档入口。"""
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "api_prefix": "/api/v1",
            "docs": "/docs",
            "health": "/api/v1/health",
        },
    }
