"""用户相关模式：登录 / 资料 / 收藏。

说明：收藏接口同时兼容两套字段风格——
- 文档约定：fav_type / fav_id / fav_name
- 前端直传：type / id / name（mobile-app/api/user.js 的 toggleFavorite 直接透传条目）
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RegisterIn(BaseModel):
    """注册入参：用户名 + 密码（用户名唯一）。"""

    username: str = Field(..., min_length=2, max_length=30, description="用户名（唯一标识）")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    nickname: str = Field("", max_length=50, description="昵称（可选）")
    avatar: str = Field("", max_length=255, description="头像URL（可选）")


class LoginIn(BaseModel):
    """登录入参：用户名 + 密码。"""

    username: str = Field(..., min_length=1, max_length=30, description="用户名")
    password: str = Field(..., min_length=1, max_length=50, description="密码")


class ProfileIn(BaseModel):
    """更新资料入参（仅更新提供的字段）。"""

    nickname: Optional[str] = Field(None, max_length=50)
    avatar: Optional[str] = Field(None, max_length=255)


class PasswordIn(BaseModel):
    """修改密码入参：需验证旧密码。"""

    old_password: str = Field(..., min_length=1, max_length=50, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


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
