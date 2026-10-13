"""科普闯关相关模式：关卡 / 题目 / 判分 / 排行 / 错题。"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SubmitIn(BaseModel):
    """单题提交入参。"""

    question_id: int = Field(..., alias="questionId")
    answer: str = Field(..., min_length=1, max_length=10)

    model_config = ConfigDict(populate_by_name=True)  # 同时接受 question_id / questionId
