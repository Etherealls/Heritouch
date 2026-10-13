"""科普闯关接口：关卡 / 题目 / 判分 / 排行 / 错题。

约定（与前端 mobile-app/api/game.js 对齐）：
- 题目列表接口必须剔除 answer/analysis，防止答案下发前端；
- 答对得分按难度：1 → 10 分，2 → 15 分，3 → 20 分；
- 关卡解锁按用户累计积分 >= need_score；过关按单关正确率 >= 60%。
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_optional_user
from app.models.game import GameLevel, GameQuestion, GameRecord
from app.models.user import SysUser, WrongQuestion
from app.schemas.common import ok
from app.schemas.game import SubmitIn

logger = logging.getLogger("heritouch.api.game")

router = APIRouter()

# 难度 → 积分（与前端规则一致）
DIFFICULTY_SCORES: dict[int, int] = {1: 10, 2: 15, 3: 20}
# 单关过关正确率阈值
PASS_RATIO: float = 0.6


def _question_dict(question: GameQuestion) -> dict[str, Any]:
    """题目 → 响应字典（不含答案与解析，供题目列表与错题本共用）。"""
    return {
        "id": question.id,
        "level_id": question.level_id,
        "question_type": question.question_type,
        "question_text": question.question_text,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "image": question.image,
        "difficulty": question.difficulty,
    }


@router.get("/levels", summary="关卡列表")
def get_levels(
    db: Session = Depends(get_db),
    user: SysUser | None = Depends(get_optional_user),
) -> dict[str, Any]:
    """关卡列表，含 unlocked/bestScore/passed（按当前用户积分与成绩计算）。"""
    levels = (
        db.execute(select(GameLevel).order_by(GameLevel.sort, GameLevel.id)).scalars().all()
    )
    user_score = user.score if user is not None else 0
    data: list[dict[str, Any]] = []
    for level in levels:
        best_score = 0
        passed = False
        if user is not None:
            records = (
                db.execute(
                    select(GameRecord).where(
                        GameRecord.user_id == user.id, GameRecord.level_id == level.id
                    )
                )
                .scalars()
                .all()
            )
            if records:
                best_score = max(record.score for record in records)
                passed = any(
                    record.correct_count >= record.total * PASS_RATIO for record in records
                )
        data.append(
            {
                "id": level.id,
                "name": level.name,
                "subtitle": level.subtitle,
                "rank": level.rank,
                "need_score": level.need_score,
                "theme": level.theme,
                "question_count": level.question_count,
                "icon": level.icon,
                "sort": level.sort,
                "unlocked": user_score >= level.need_score,
                "bestScore": best_score,
                "passed": passed,
            }
        )
    return ok(data)


@router.get("/questions/{level_id}", summary="关卡题目（不含答案）")
def get_questions(
    level_id: int,
    count: int = Query(10, ge=1, le=50, description="题目数量"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """获取关卡题目；**答案与解析字段已剔除**。"""
    level = db.get(GameLevel, level_id)
    if level is None:
        raise HTTPException(status_code=404, detail="关卡不存在")
    questions = (
        db.execute(
            select(GameQuestion)
            .where(GameQuestion.level_id == level_id)
            .order_by(GameQuestion.id)
            .limit(count)
        )
        .scalars()
        .all()
    )
    return ok([_question_dict(question) for question in questions])


@router.post("/submit", summary="提交单题答案")
def submit_answer(
    body: SubmitIn,
    db: Session = Depends(get_db),
    user: SysUser | None = Depends(get_optional_user),
) -> dict[str, Any]:
    """判分并返回 {correct, answer, analysis, score, difficulty}；登录用户累计积分并记录错题。"""
    question = db.get(GameQuestion, body.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="题目不存在")
    correct = body.answer.strip().upper() == (question.answer or "").strip().upper()
    gained = DIFFICULTY_SCORES.get(question.difficulty, 10) if correct else 0
    if user is not None:
        # 累计本关成绩（按用户+关卡 upsert）
        record = (
            db.execute(
                select(GameRecord).where(
                    GameRecord.user_id == user.id, GameRecord.level_id == question.level_id
                )
            )
            .scalars()
            .first()
        )
        if record is None:
            record = GameRecord(
                user_id=user.id, level_id=question.level_id, score=0, total=0, correct_count=0
            )
            db.add(record)
        record.score += gained
        record.total += 1
        if correct:
            record.correct_count += 1
        # 累计用户积分
        user.score += gained
        # 错题本（答错才记录，重复答错累计次数）
        if not correct:
            wrong = (
                db.execute(
                    select(WrongQuestion).where(
                        WrongQuestion.user_id == user.id,
                        WrongQuestion.question_id == question.id,
                    )
                )
                .scalars()
                .first()
            )
            if wrong is None:
                db.add(
                    WrongQuestion(
                        user_id=user.id,
                        question_id=question.id,
                        wrong_count=1,
                        last_wrong_time=datetime.now(),
                    )
                )
            else:
                wrong.wrong_count += 1
                wrong.last_wrong_time = datetime.now()
        db.commit()
        db.refresh(user)
    return ok(
        {
            "correct": correct,
            "answer": question.answer,
            "analysis": question.analysis or "",
            "score": gained,
            "difficulty": question.difficulty,
            "totalScore": user.score if user is not None else 0,
        }
    )


@router.get("/rank", summary="积分排行榜")
def get_rank(
    db: Session = Depends(get_db),
    user: SysUser | None = Depends(get_optional_user),
) -> dict[str, Any]:
    """排行榜 Top10；当前用户不在榜内时追加"我"的条目（me=true）。"""
    top_users = (
        db.execute(select(SysUser).order_by(SysUser.score.desc(), SysUser.id).limit(10))
        .scalars()
        .all()
    )
    data: list[dict[str, Any]] = []
    my_included = False
    for index, top_user in enumerate(top_users, start=1):
        is_me = user is not None and top_user.id == user.id
        my_included = my_included or is_me
        data.append(
            {
                "rank": index,
                "userId": top_user.id,
                "nickname": top_user.nickname or "非遗爱好者",
                "avatar": top_user.avatar or "",
                "score": top_user.score,
                "me": is_me,
            }
        )
    if user is not None and not my_included:
        higher = (
            db.execute(
                select(func.count()).select_from(SysUser).where(SysUser.score > user.score)
            )
            .scalar()
            .one()
        )
        data.append(
            {
                "rank": int(higher) + 1,
                "userId": user.id,
                "nickname": user.nickname or "我",
                "avatar": user.avatar or "",
                "score": user.score,
                "me": True,
            }
        )
    return ok(data)


@router.get("/wrong", summary="我的错题本")
def get_wrong_questions(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """错题列表（需登录）：题目字段 + 错误次数 + 最近错误时间。"""
    rows = (
        db.execute(
            select(WrongQuestion, GameQuestion)
            .join(GameQuestion, WrongQuestion.question_id == GameQuestion.id)
            .where(WrongQuestion.user_id == user.id)
            .order_by(WrongQuestion.last_wrong_time.desc())
        )
        .all()
    )
    data: list[dict[str, Any]] = []
    for wrong, question in rows:
        item = _question_dict(question)
        wrong_ms = int(wrong.last_wrong_time.timestamp() * 1000) if wrong.last_wrong_time else None
        item.update(
            {
                "answer": question.answer,
                "analysis": question.analysis or "",
                "wrong_count": wrong.wrong_count,
                "wrongId": wrong.id,
                "last_wrong_time": wrong_ms,
                "lastWrongTime": wrong_ms,
            }
        )
        data.append(item)
    return ok(data)


@router.delete("/wrong/{wrong_id}", summary="移除错题")
def remove_wrong(
    wrong_id: int,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """移除错题（需登录）；{wrong_id} 兼容错题记录 ID 与题目 ID 两种传参。"""
    wrong = db.get(WrongQuestion, wrong_id)
    if wrong is None or wrong.user_id != user.id:
        wrong = (
            db.execute(
                select(WrongQuestion).where(
                    WrongQuestion.user_id == user.id, WrongQuestion.question_id == wrong_id
                )
            )
            .scalars()
            .first()
        )
    if wrong is None:
        raise HTTPException(status_code=404, detail="错题不存在")
    db.delete(wrong)
    db.commit()
    return ok({"id": wrong_id})
