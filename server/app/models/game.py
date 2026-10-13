"""科普闯关 ORM 模型（字段与 database/mysql/schema.sql 保持一致）。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GameLevel(Base):
    """闯关关卡表：科普闯关关卡配置。"""

    __tablename__ = "game_level"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="关卡ID")
    name: Mapped[str] = mapped_column(String(50), comment="关卡名称（如 入门学徒）")
    subtitle: Mapped[Optional[str]] = mapped_column(String(100), comment="关卡副标题")
    rank: Mapped[Optional[str]] = mapped_column(String(20), comment="对应段位（学徒/弟子/匠人/大师）")
    need_score: Mapped[int] = mapped_column(Integer, default=0, comment="解锁所需累计积分")
    theme: Mapped[Optional[str]] = mapped_column(String(50), comment="关卡主题")
    question_count: Mapped[int] = mapped_column(Integer, default=10, comment="每关题量")
    icon: Mapped[Optional[str]] = mapped_column(String(20), comment="关卡图标（emoji）")
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序（升序）")


class GameQuestion(Base):
    """闯关题目表：单选/判断/识图三类题型，answer 不下发前端。"""

    __tablename__ = "game_question"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="题目ID")
    level_id: Mapped[int] = mapped_column(
        ForeignKey("game_level.id"), index=True, comment="所属关卡ID"
    )
    question_type: Mapped[str] = mapped_column(String(20), default="single", comment="题型")
    question_text: Mapped[Optional[str]] = mapped_column(Text, comment="题干")
    option_a: Mapped[Optional[str]] = mapped_column(String(255), comment="选项A")
    option_b: Mapped[Optional[str]] = mapped_column(String(255), comment="选项B")
    option_c: Mapped[Optional[str]] = mapped_column(String(255), comment="选项C")
    option_d: Mapped[Optional[str]] = mapped_column(String(255), comment="选项D")
    answer: Mapped[str] = mapped_column(String(2), comment="正确答案（A/B/C/D）")
    analysis: Mapped[Optional[str]] = mapped_column(Text, comment="答案解析")
    image: Mapped[Optional[str]] = mapped_column(String(255), comment="识图题图片URL")
    difficulty: Mapped[int] = mapped_column(Integer, default=1, comment="难度（1 易/2 中/3 难）")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")


class GameRecord(Base):
    """闯关记录表：每关累计成绩（按用户+关卡维度 upsert）。"""

    __tablename__ = "game_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="记录ID")
    user_id: Mapped[int] = mapped_column(Integer, index=True, comment="用户ID")
    level_id: Mapped[int] = mapped_column(Integer, index=True, comment="关卡ID")
    score: Mapped[int] = mapped_column(Integer, default=0, comment="本关累计得分")
    total: Mapped[int] = mapped_column(Integer, default=0, comment="本关累计答题数")
    correct_count: Mapped[int] = mapped_column(Integer, default=0, comment="本关累计答对题数")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="答题时间")
