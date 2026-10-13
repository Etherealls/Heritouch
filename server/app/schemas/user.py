"""用户相关模式：登录 / 资料 / 收藏。

说明：收藏接口同时兼容两套字段风格——
- 文档约定：fav_type / fav_id / fav_name
- 前端直传：type / id / name（mobile-app/api/user.js 的 toggleFavorite 直接透传条目）
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LoginIn(BaseModel):
    """登录/注册入参：openid 为空时后端生成设备标识。"""

    openid: str = Field("", max_length=100)
    nickname: str = Field("", max_length=50)
    avatar: str = Field("", max_length=255)


class ProfileIn(BaseModel):
    """更新资料入参（仅更新提供的字段）。"""

    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = Field(None, max_length=255)


class FavoriteIn(BaseModel):
    """收藏入参（兼容 fav_* 与 type/id/name 两种命名）。"""

    model_config = ConfigDict(populate_by_name=True)

    fav_type: Optional[str] = Field(None, max_length=20)
    fav_id: Optional[int] = None
    fav_name: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=20)
    id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=100)

    def resolve(self) -> tuple[str, int, str]:
        """归一化字段，返回 (fav_type, fav_id, fav_name)。"""
        fav_type = (self.fav_type or self.type or "").strip()
        fav_id = self.fav_id if self.fav_id is not None else self.id
        fav_name = (self.fav_name or self.name or "").strip()
        if not fav_type:
            raise ValueError("fav_type 不能为空")
        if fav_id is None:
            raise ValueError("fav_id 不能为空")
        return fav_type, int(fav_id), fav_name
