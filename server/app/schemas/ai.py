"""AI 创作相关模式：纹样 / 剧本 / 画作生成与作品管理。

字段风格兼容前端驼峰命名（roleCount / workType 等，见 mobile-app/api/ai.js）。
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class _CamelAliasBase(BaseModel):
    """允许同时使用下划线与驼峰字段名。"""

    model_config = ConfigDict(populate_by_name=True)


class GeneratePatternIn(_CamelAliasBase):
    """非遗纹样生成入参。"""

    prompt: str = Field(..., min_length=1, max_length=500, description="纹样主题描述")
    style: str = Field("yangzhou_papercut", max_length=50, description="非遗风格")
    size: str = Field("1024x1024", max_length=20, description="图片尺寸")


class GenerateScriptIn(_CamelAliasBase):
    """科普剧本生成入参。"""

    theme: str = Field(..., min_length=1, max_length=200, description="剧本主题")
    duration: int = Field(5, ge=1, le=120, description="时长（分钟）")
    dialect: bool = Field(False, description="是否使用方言演绎")
    role_count: int = Field(3, ge=1, le=8, alias="roleCount", description="角色数量")


class GeneratePaintingIn(_CamelAliasBase):
    """非遗风格画作生成入参（文生图 / 图生图）。"""

    mode: str = Field("text", pattern="^(text|image)$", description="text 文生图 / image 图生图")
    prompt: str = Field(..., min_length=1, max_length=500)
    style: str = Field("lacquer_painting", max_length=50)
    image: Optional[str] = Field(None, description="base64 图片（图生图模式）")


class SaveWorkIn(_CamelAliasBase):
    """保存作品入参。"""

    work_type: str = Field("pattern", alias="workType", description="pattern/script/painting")
    title: str = Field("", max_length=200)
    content: str = Field("", description="图片URL或剧本文本")
    style: str = Field("", max_length=50)
    prompt: str = Field("", description="用户输入提示词")
