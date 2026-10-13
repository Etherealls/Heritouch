"""非遗内容接口：分类 / 列表 / 详情 / 传承人 / 智能推荐。"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.heritage import HeritageProject, Inheritor
from app.schemas.common import ok
from app.schemas.heritage import InheritorOut, ProjectOut
from app.services.graph_service import CATEGORY_ORDER, DEMO_PROJECT_PROFILES

logger = logging.getLogger("heritouch.api.heritage")

router = APIRouter()

# 非遗类别图标（与前端分类展示一致）
CATEGORY_ICONS: dict[str, str] = {
    "传统技艺": "🔨",
    "传统美术": "🎨",
    "传统戏剧": "🎭",
    "传统音乐": "🎵",
    "曲艺": "📢",
    "民俗": "🏮",
    "传统医药": "🌿",
}
DEFAULT_CATEGORY_ICON = "🏛️"


def _enrich_project(project: HeritageProject) -> dict[str, Any]:
    """ORM → 响应字典，并补充演示资料（tags/materials/works/folk_customs/inheritors）。

    说明：tags 等字段在 MySQL 中无对应列（与 database/mysql/schema.sql 对齐），
    由内置演示数据集按项目 ID 补充；非演示数据将返回空列表。
    """
    data = ProjectOut.model_validate(project).model_dump()
    profile = DEMO_PROJECT_PROFILES.get(project.id, {})
    data["tags"] = profile.get("tags", [])
    data["materials"] = profile.get("materials", [])
    data["works"] = profile.get("works", [])
    data["folk_customs"] = profile.get("folk_customs", [])
    data["inheritors"] = [person.id for person in project.inheritors]
    return data


def _inheritor_dict(person: Inheritor) -> dict[str, Any]:
    """传承人 ORM → 响应字典（附带所属项目名称）。"""
    data = InheritorOut.model_validate(person).model_dump()
    data["project_name"] = person.project.name if person.project else None
    return data


@router.get("/categories", summary="非遗分类列表")
def get_categories(db: Session = Depends(get_db)) -> dict[str, Any]:
    """返回 [{id, name, icon, count}]，按固定顺序保证分类图标映射稳定。"""
    rows = db.execute(
        select(HeritageProject.category, func.count(HeritageProject.id)).group_by(
            HeritageProject.category
        )
    ).all()
    counts = {category: count for category, count in rows}
    data = [
        {
            "id": index,
            "name": category,
            "icon": CATEGORY_ICONS.get(category, DEFAULT_CATEGORY_ICON),
            "count": counts.get(category, 0),
        }
        for index, category in enumerate(CATEGORY_ORDER, start=1)
    ]
    return ok(data)


@router.get("", summary="非遗项目列表")
def list_projects(
    category: str = Query("", description="类别名称，如 传统美术"),
    level: str = Query("", description="级别，如 国家级/省级"),
    region: str = Query("", description="地区关键字，如 扬州"),
    keyword: str = Query("", description="关键词（项目名称/简介模糊匹配）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """分页检索非遗项目，返回 {total, list, page, size}。"""
    stmt = select(HeritageProject)
    if category:
        stmt = stmt.where(HeritageProject.category == category)
    if level:
        stmt = stmt.where(HeritageProject.level == level)
    if region:
        stmt = stmt.where(HeritageProject.region.like(f"%{region}%"))
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(HeritageProject.name.like(like), HeritageProject.intro.like(like)))
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    projects = (
        db.execute(
            stmt.order_by(HeritageProject.id).offset((page - 1) * size).limit(size)
        )
        .scalars()
        .all()
    )
    return ok(
        {
            "total": total,
            "list": [_enrich_project(project) for project in projects],
            "page": page,
            "size": size,
        }
    )


@router.get("/inheritor/{inheritor_id}", summary="传承人详情")
def get_inheritor(inheritor_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """传承人详情 + 所属项目名称。"""
    person = db.get(Inheritor, inheritor_id)
    if person is None:
        raise HTTPException(status_code=404, detail="传承人不存在")
    return ok(_inheritor_dict(person))


@router.get("/{project_id}", summary="非遗项目详情")
def get_project(project_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """项目详情 + 传承人列表（inheritor_list）。"""
    project = db.get(HeritageProject, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="非遗项目不存在")
    data = _enrich_project(project)
    data["inheritor_list"] = [_inheritor_dict(person) for person in project.inheritors]
    return ok(data)


@router.get("/{project_id}/recommendations", summary="智能关联推荐")
def get_recommendations(project_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """推荐：similar（材料相关）/ sameCategory（同类）/ sameRegion（同地区）。"""
    project = db.get(HeritageProject, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="非遗项目不存在")
    materials = set(DEMO_PROJECT_PROFILES.get(project.id, {}).get("materials", []))
    others = (
        db.execute(select(HeritageProject).where(HeritageProject.id != project.id))
        .scalars()
        .all()
    )
    similar = [
        other
        for other in others
        if materials & set(DEMO_PROJECT_PROFILES.get(other.id, {}).get("materials", []))
    ]
    same_category = [other for other in others if other.category == project.category]
    same_region = [other for other in others if other.region == project.region]
    return ok(
        {
            "similar": [_enrich_project(other) for other in similar[:4]],
            "sameCategory": [_enrich_project(other) for other in same_category[:4]],
            "sameRegion": [_enrich_project(other) for other in same_region[:4]],
        }
    )
