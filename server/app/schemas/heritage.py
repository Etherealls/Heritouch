"""非遗内容相关模式：项目 / 传承人 / 分类 / 推荐。

字段命名与前端 mobile-app/api/mock/data.js 保持一致（snake_case），
tags / materials / works / folk_customs 由演示数据集补充（见 graph_service.DEMO_PROJECT_PROFILES）。
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class OrmBase(BaseModel):
    """允许从 ORM 对象直接校验（from_attributes）。"""

    model_config = ConfigDict(from_attributes=True)


class InheritorOut(OrmBase):
    """传承人详情（含所属项目名称）。"""

    id: int
    name: str
    gender: Optional[str] = None
    project_id: int
    project_name: Optional[str] = None
    title: Optional[str] = None
    biography: Optional[str] = None
    photo: Optional[str] = None


class ProjectOut(OrmBase):
    """非遗项目公开字段（列表/详情共用）。"""

    id: int
    name: str
    level: str = ""
    category: str = ""
    region: str = ""
    batch: Optional[int] = None
    intro: Optional[str] = None
    history: Optional[str] = None
    craft: Optional[str] = None
    cover_image: Optional[str] = None
    audio_mandarin: Optional[str] = None
    audio_dialect: Optional[str] = None
    qrcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tags: List[str] = []
    materials: List[str] = []
    works: List[str] = []
    folk_customs: List[str] = []


class CategoryOut(BaseModel):
    """非遗分类（id 为固定序号，与前端分类图标映射一致）。"""

    id: int
    name: str
    icon: str
    count: int


class HeritageListOut(BaseModel):
    """非遗项目分页列表。"""

    total: int
    list: List[ProjectOut]
    page: int = 1
    size: int = 10


class RecommendationsOut(BaseModel):
    """智能关联推荐。"""

    similar: List[ProjectOut] = []
    sameCategory: List[ProjectOut] = []
    sameRegion: List[ProjectOut] = []


class GraphNode(BaseModel):
    """知识图谱节点（id 形如 h1/i101/c1，refId 为 MySQL 主键）。"""

    id: str
    name: str
    type: str
    refId: Optional[int] = None


class GraphEdge(BaseModel):
    """知识图谱关系（label 为中文展示名）。"""

    source: str
    target: str
    label: str


class GraphOut(BaseModel):
    """知识图谱数据。"""

    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
