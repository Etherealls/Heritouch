"""用户相关 ORM 模型（字段与 database/mysql/schema.sql 保持一致）。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SysUser(Base):
    """系统用户表：用户名 + 密码注册登录，score 为闯关累计积分。"""

    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(100), unique=True, comment="用户名（唯一标识）")
    password_hash: Mapped[str] = mapped_column(String(255), comment="密码哈希（PBKDF2）")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像URL")
    score: Mapped[int] = mapped_column(Integer, default=0, comment="累计积分")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="注册时间")


class UserFavorite(Base):
    """用户收藏表：收藏项目/传承人/作品，同一用户同类同目标唯一。"""

    __tablename__ = "user_favorite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id: Mapped[int] = mapped_column(Integer, index=True, comment="用户ID")
    fav_type: Mapped[str] = mapped_column(String(20), default="project", comment="收藏类型")
    fav_id: Mapped[int] = mapped_column(Integer, comment="收藏目标ID")
    fav_name: Mapped[Optional[str]] = mapped_column(String(100), comment="收藏目标名称（冗余存储）")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="收藏时间")


class WrongQuestion(Base):
    """错题本表：闯关答错题目，wrong_count 累计错误次数。"""

    __tablename__ = "wrong_question"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="错题记录ID")
    user_id: Mapped[int] = mapped_column(Integer, index=True, comment="用户ID")
    question_id: Mapped[int] = mapped_column(Integer, index=True, comment="题目ID")
    wrong_count: Mapped[int] = mapped_column(Integer, default=1, comment="累计答错次数")
    last_wrong_time: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="最近答错时间")


class UserWork(Base):
    """用户作品表：AI 互动创作产出的纹样/剧本/画作。"""

    __tablename__ = "user_work"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="作品ID")
    user_id: Mapped[int] = mapped_column(Integer, index=True, comment="作者用户ID")
    work_type: Mapped[str] = mapped_column(String(20), default="pattern", comment="作品类型")
    title: Mapped[Optional[str]] = mapped_column(String(200), comment="作品标题")
    content: Mapped[Optional[str]] = mapped_column(Text, comment="作品内容（图片URL或剧本文本）")
    style: Mapped[Optional[str]] = mapped_column(String(50), comment="创作风格")
    prompt: Mapped[Optional[str]] = mapped_column(Text, comment="用户输入提示词")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创作时间")
