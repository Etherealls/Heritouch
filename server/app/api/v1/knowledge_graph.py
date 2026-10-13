"""知识图谱接口。"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Query

from app.schemas.common import ok
from app.services.graph_service import graph_service

logger = logging.getLogger("heritouch.api.knowledge_graph")

router = APIRouter()


@router.get("", summary="知识图谱数据")
def get_knowledge_graph(
    category: str = Query("", description="类别名称，空为全图"),
    region: str = Query("", description="地区关键字，空为不限"),
    depth: int = Query(2, ge=1, le=3, description="遍历深度（1 直接邻居 / 2 两跳）"),
) -> dict[str, Any]:
    """返回 {nodes:[{id,name,type,refId}], edges:[{source,target,label}]}。

    Neo4j 不可用或无数据时自动使用内存演示图谱（见 graph_service）。
    """
    return ok(graph_service.get_graph(category=category, region=region, depth=depth))
