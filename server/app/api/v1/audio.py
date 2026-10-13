"""多模态智能导览接口：语音讲解 / 智能问答 / 扫码解析 / 离线包。

注意：本文件包含两个路由器——
- router：/audio/*（讲解音频、智能问答）
- guide_router：/guide/*（扫码解析、离线包）
"""
from __future__ import annotations

import logging
import re
import time
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.heritage import HeritageProject
from app.models.user import SysUser
from app.schemas.common import ok
from app.services.rag_service import rag_service
from app.services.tts_service import tts_service

logger = logging.getLogger("heritouch.api.audio")

router = APIRouter()
guide_router = APIRouter()


class QuestionIn(BaseModel):
    """智能问答入参。"""

    question: str = Field(..., min_length=1, max_length=200, description="用户问题")


class ScanResolveIn(BaseModel):
    """扫码解析入参。"""

    code: str = Field(..., min_length=1, max_length=500, description="二维码内容")


def _parse_project_id(code: str) -> Optional[int]:
    """解析二维码内容中的项目 ID。

    支持格式：heritouch://project?id=3 / https://host/p?id=3 / ?id=3 / /project/3 / 纯数字 3
    """
    if not code:
        return None
    matched = re.search(r"[?&]id=(\d+)", code)
    if matched:
        return int(matched.group(1))
    matched = re.match(r"^\s*(\d+)\s*$", code)
    if matched:
        return int(matched.group(1))
    matched = re.search(r"/project/(\d+)", code)
    if matched:
        return int(matched.group(1))
    return None


@router.get("/guide/{project_id}", summary="导览音频与讲解词")
def get_guide_audio(
    project_id: int,
    lang: str = Query("mandarin", pattern="^(mandarin|dialect)$", description="讲解语言"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """获取项目导览：{url, text, duration}；预置音频缺失时尝试 TTS 合成。"""
    project = db.get(HeritageProject, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="非遗项目不存在")
    return ok(tts_service.guide_audio(project, lang))


@router.post("/qa", summary="智能问答（RAG + LLM）")
def audio_qa(body: QuestionIn) -> dict[str, Any]:
    """基于非遗知识库的智能问答，返回 {answer, audio, question, sources}。

    RAG 与 LLM 均不可用时可降级为关键词匹配答案，audio 为空字符串。
    """
    result = rag_service.answer(body.question)
    tts = tts_service.synthesize(result["answer"])
    result["audio"] = tts["url"]
    result["question"] = body.question
    return ok(result)


@guide_router.post("/scan-resolve", summary="扫码内容解析")
def scan_resolve(body: ScanResolveIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    """解析非遗二维码，返回 {projectId, name}。"""
    project_id = _parse_project_id(body.code)
    if project_id is None:
        raise HTTPException(status_code=400, detail="无效的非遗二维码")
    project = db.get(HeritageProject, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="未找到对应非遗项目")
    return ok({"projectId": project.id, "name": project.name})


@guide_router.post("/offline-pack", summary="离线数据包")
def download_offline_pack(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """下载核心讲解音频与基础数据（需登录），返回 {version, download_time, projects, size}。"""
    rows = db.execute(
        select(
            HeritageProject.id,
            HeritageProject.name,
            HeritageProject.intro,
            HeritageProject.audio_mandarin,
        )
    ).all()
    projects = [
        {"id": project_id, "name": name, "intro": intro or "", "audio": audio or ""}
        for project_id, name, intro, audio in rows
    ]
    return ok(
        {
            "version": settings.APP_VERSION,
            "download_time": int(time.time() * 1000),
            "projects": projects,
            "size": f"{len(projects) * 0.9:.1f}MB",
        }
    )
