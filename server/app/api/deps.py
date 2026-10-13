"""API 通用依赖：数据库会话 / 登录用户解析。

- get_db：请求级 SQLAlchemy 会话；
- get_current_user：解析 Authorization: Bearer <token>，无效抛 401；
- get_optional_user：可选登录用户（游客模式接口使用，无 token 返回 None）。
"""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import SysUser


def _resolve_user(authorization: Optional[str], db: Session) -> Optional[SysUser]:
    """从 Authorization 头解析用户；无效/缺失返回 None。"""
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    user_id = decode_token(token)
    if user_id is None:
        return None
    return db.get(SysUser, user_id)


def get_current_user(
    authorization: Optional[str] = Header(None, description="Bearer <token>"),
    db: Session = Depends(get_db),
) -> SysUser:
    """必须登录的依赖：解析失败统一抛 401。"""
    user = _resolve_user(authorization, db)
    if user is None:
        raise HTTPException(status_code=401, detail="未登录或登录已过期，请重新登录")
    return user


def get_optional_user(
    authorization: Optional[str] = Header(None, description="Bearer <token>（可选）"),
    db: Session = Depends(get_db),
) -> Optional[SysUser]:
    """可选登录依赖：游客可访问，登录后返回对应用户（如闯关答题）。"""
    return _resolve_user(authorization, db)
