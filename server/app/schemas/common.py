"""统一响应模型。

所有接口成功时返回：{"code": 0, "message": "ok", "data": ...}
错误时由全局异常处理器转换为：{"code": <HTTP状态码>, "message": <错误信息>, "data": null}
"""
from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应体（泛型 data，便于 OpenAPI 文档标注具体结构）。"""

    code: int = 0
    message: str = "ok"
    data: Optional[T] = None


def ok(data: Any = None, message: str = "ok") -> dict[str, Any]:
    """构造成功响应字典（端点直接 return ok(...)）。"""
    return {"code": 0, "message": message, "data": data}


def fail(code: int, message: str) -> dict[str, Any]:
    """构造失败响应字典（一般用于无法抛 HTTPException 的场景）。"""
    return {"code": code, "message": message, "data": None}
