"""AI 创作接口：纹样 / 剧本 / 画作生成 + 作品管理。"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import SysUser, UserWork
from app.schemas.ai import GeneratePaintingIn, GeneratePatternIn, GenerateScriptIn, SaveWorkIn
from app.schemas.common import ok
from app.services.ai_service import ai_service

logger = logging.getLogger("heritouch.api.ai")

router = APIRouter()


def _work_dict(work: UserWork) -> dict[str, Any]:
    """作品 ORM → 响应字典（同时提供下划线与驼峰字段，兼容前端两种风格）。"""
    create_ms = int(work.create_time.timestamp() * 1000) if work.create_time else None
    return {
        "id": work.id,
        "user_id": work.user_id,
        "work_type": work.work_type,
        "workType": work.work_type,
        "title": work.title or "",
        "content": work.content or "",
        "style": work.style or "",
        "prompt": work.prompt or "",
        "create_time": work.create_time.strftime("%Y-%m-%d %H:%M:%S") if work.create_time else None,
        "createTime": create_ms,
        "ai_created": True,
    }


@router.post("/generate-pattern", summary="生成非遗纹样")
def generate_pattern(body: GeneratePatternIn) -> dict[str, Any]:
    """根据主题与非遗风格生成纹样（AI 不可用时返回占位图，ai_created 恒为 true）。"""
    return ok(ai_service.generate_pattern(body.prompt, body.style, body.size))


@router.post("/generate-script", summary="生成科普剧本")
def generate_script(body: GenerateScriptIn) -> dict[str, Any]:
    """根据主题/时长/方言/角色数生成多场景科普剧本。"""
    return ok(
        ai_service.generate_script(body.theme, body.duration, body.dialect, body.role_count)
    )


@router.post("/generate-painting", summary="生成非遗风格画作")
def generate_painting(body: GeneratePaintingIn) -> dict[str, Any]:
    """文生图 / 图生图生成非遗风格画作。"""
    return ok(ai_service.generate_painting(body.mode, body.prompt, body.style, body.image))


@router.post("/works", summary="保存作品")
def create_work(
    body: SaveWorkIn,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """保存 AI 作品到我的作品（需登录）。"""
    work = UserWork(
        user_id=user.id,
        work_type=body.work_type,
        title=body.title,
        content=body.content,
        style=body.style,
        prompt=body.prompt,
    )
    db.add(work)
    db.commit()
    db.refresh(work)
    return ok(_work_dict(work))


@router.get("/works", summary="我的作品")
def list_works(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """我的作品列表（需登录，按创作时间倒序）。"""
    works = (
        db.execute(
            select(UserWork)
            .where(UserWork.user_id == user.id)
            .order_by(UserWork.create_time.desc(), UserWork.id.desc())
        )
        .scalars()
        .all()
    )
    return ok([_work_dict(work) for work in works])


@router.delete("/works/{work_id}", summary="删除作品")
def delete_work(
    work_id: int,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """删除我的作品（需登录，仅能删除本人作品）。"""
    work = db.get(UserWork, work_id)
    if work is None or work.user_id != user.id:
        raise HTTPException(status_code=404, detail="作品不存在")
    db.delete(work)
    db.commit()
    return ok({"id": work_id})
