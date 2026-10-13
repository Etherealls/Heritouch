"""非遗项目与传承人 ORM 模型（字段与 database/mysql/schema.sql 保持一致）。"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HeritageProject(Base):
    """非遗项目表：核心内容表，存储非遗项目的全部图文与语音资料。"""

    __tablename__ = "heritage_project"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="项目ID")
    name: Mapped[str] = mapped_column(String(100), index=True, comment="项目名称")
    level: Mapped[str] = mapped_column(String(20), default="", comment="非遗级别（国家级/省级/市级/县级）")
    category: Mapped[str] = mapped_column(String(50), index=True, default="", comment="非遗类别")
    region: Mapped[str] = mapped_column(String(50), index=True, default="", comment="申报地区（如 江苏扬州）")
    batch: Mapped[Optional[int]] = mapped_column(Integer, comment="列入名录批次年份")
    intro: Mapped[Optional[str]] = mapped_column(Text, comment="项目简介")
    history: Mapped[Optional[str]] = mapped_column(Text, comment="历史渊源")
    craft: Mapped[Optional[str]] = mapped_column(Text, comment="工艺流程/技艺特点")
    cover_image: Mapped[Optional[str]] = mapped_column(String(255), comment="封面图URL")
    audio_mandarin: Mapped[Optional[str]] = mapped_column(String(255), comment="普通话讲解音频URL")
    audio_dialect: Mapped[Optional[str]] = mapped_column(String(255), comment="方言讲解音频URL")
    qrcode: Mapped[Optional[str]] = mapped_column(String(255), comment="二维码图片URL（扫码导览用）")
    latitude: Mapped[Optional[float]] = mapped_column(comment="纬度")
    longitude: Mapped[Optional[float]] = mapped_column(comment="经度")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间"
    )

    # 一对多：项目 → 传承人
    inheritors: Mapped[List["Inheritor"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Inheritor(Base):
    """传承人表：非遗项目代表性传承人信息。"""

    __tablename__ = "inheritor"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="传承人ID")
    name: Mapped[str] = mapped_column(String(50), index=True, comment="姓名")
    gender: Mapped[Optional[str]] = mapped_column(String(2), comment="性别（男/女）")
    project_id: Mapped[int] = mapped_column(
        ForeignKey("heritage_project.id"), index=True, comment="所属非遗项目ID"
    )
    title: Mapped[Optional[str]] = mapped_column(String(50), comment="传承人称号")
    biography: Mapped[Optional[str]] = mapped_column(Text, comment="人物简介")
    photo: Mapped[Optional[str]] = mapped_column(String(255), comment="照片URL")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    # 多对一：传承人 → 项目
    project: Mapped["HeritageProject"] = relationship(back_populates="inheritors")
