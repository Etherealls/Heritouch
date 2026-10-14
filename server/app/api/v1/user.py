"""用户接口：注册 / 登录 / 信息 / 资料 / 密码 / 收藏。"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_token, hash_password, verify_password
from app.models.game import GameRecord
from app.models.user import SysUser, UserFavorite, UserWork, WrongQuestion
from app.schemas.common import ok
from app.schemas.user import FavoriteIn, LoginIn, PasswordIn, ProfileIn, RegisterIn

logger = logging.getLogger("heritouch.api.user")

router = APIRouter()

# 支持的收藏类型
FAVORITE_TYPES = ("project", "inheritor", "work")


def _user_dict(user: SysUser) -> dict[str, Any]:
    """用户 ORM → 响应字典（不含密码哈希）。"""
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname or user.username,
        "avatar": user.avatar or "",
        "score": user.score,
        "create_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S")
        if user.create_time
        else None,
    }


@router.post("/register", summary="用户注册")
def register(body: RegisterIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    """用户名 + 密码注册；用户名唯一，注册成功后直接返回登录态（token）。"""
    username = body.username.strip()
    # 用户名唯一校验
    exists = (
        db.execute(select(SysUser).where(SysUser.username == username)).scalars().first()
    )
    if exists is not None:
        raise HTTPException(status_code=409, detail="用户名已存在，请更换")
    user = SysUser(
        username=username,
        password_hash=hash_password(body.password),
        nickname=body.nickname.strip() or username,
        avatar=body.avatar or "",
        score=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    data = _user_dict(user)
    data["token"] = create_token(user.id)
    return ok(data)


@router.post("/login", summary="用户登录")
def login(body: LoginIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    """用户名 + 密码登录；校验通过返回用户信息 + token。"""
    username = body.username.strip()
    user = (
        db.execute(select(SysUser).where(SysUser.username == username)).scalars().first()
    )
    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    data = _user_dict(user)
    data["token"] = create_token(user.id)
    return ok(data)


@router.get("/info", summary="用户信息与统计")
def get_user_info(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """用户积分 / 收藏数 / 错题数 / 作品数 / 累计答题数（需登录）。"""
    favorite_count = (
        db.execute(
            select(func.count()).select_from(UserFavorite).where(UserFavorite.user_id == user.id)
        )
        .scalar()
        .one()
    )
    wrong_count = (
        db.execute(
            select(func.count()).select_from(WrongQuestion).where(WrongQuestion.user_id == user.id)
        )
        .scalar()
        .one()
    )
    work_count = (
        db.execute(
            select(func.count()).select_from(UserWork).where(UserWork.user_id == user.id)
        )
        .scalar()
        .one()
    )
    answered_count = (
        db.execute(
            select(func.coalesce(func.sum(GameRecord.total), 0)).where(
                GameRecord.user_id == user.id
            )
        )
        .scalar()
        .one()
    )
    data = _user_dict(user)
    data.update(
        {
            "favoriteCount": int(favorite_count),
            "wrongCount": int(wrong_count),
            "workCount": int(work_count),
            "answeredCount": int(answered_count),
        }
    )
    return ok(data)


@router.put("/profile", summary="更新个人资料")
def update_profile(
    body: ProfileIn,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """更新昵称/头像（需登录，仅更新提供的字段）。"""
    if body.nickname is not None:
        user.nickname = body.nickname
    if body.avatar is not None:
        user.avatar = body.avatar
    db.commit()
    db.refresh(user)
    return ok(_user_dict(user))


@router.put("/password", summary="修改密码")
def update_password(
    body: PasswordIn,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """修改密码（需登录，验证旧密码后更新为新密码）。"""
    if not verify_password(body.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码不正确")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return ok({"updated": True})


@router.post("/favorite", summary="添加收藏")
def add_favorite(
    body: FavoriteIn,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """收藏项目/传承人/作品（需登录）；重复收藏返回已存在记录。"""
    try:
        fav_type, fav_id, fav_name = body.resolve()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if fav_type not in FAVORITE_TYPES:
        raise HTTPException(status_code=400, detail="fav_type 仅支持 project/inheritor/work")
    exists = (
        db.execute(
            select(UserFavorite).where(
                UserFavorite.user_id == user.id,
                UserFavorite.fav_type == fav_type,
                UserFavorite.fav_id == fav_id,
            )
        )
        .scalars()
        .first()
    )
    if exists is not None:
        return ok({"id": exists.id, "favorited": True, "existed": True})
    favorite = UserFavorite(
        user_id=user.id, fav_type=fav_type, fav_id=fav_id, fav_name=fav_name
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return ok({"id": favorite.id, "favorited": True, "existed": False})


@router.delete("/favorite/{favorite_id}", summary="取消收藏")
def remove_favorite(
    favorite_id: int,
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """取消收藏（需登录）。

    {favorite_id} 优先按收藏记录 ID 匹配；未匹配到时按收藏目标 ID
    （fav_id）兜底匹配，兼容前端直接传入项目/传承人 ID 的调用方式。
    """
    favorite = db.get(UserFavorite, favorite_id)
    if favorite is None or favorite.user_id != user.id:
        favorite = (
            db.execute(
                select(UserFavorite).where(
                    UserFavorite.user_id == user.id, UserFavorite.fav_id == favorite_id
                )
            )
            .scalars()
            .first()
        )
    if favorite is None:
        raise HTTPException(status_code=404, detail="收藏不存在")
    db.delete(favorite)
    db.commit()
    return ok({"id": favorite_id, "favorited": False})


@router.get("/favorites", summary="我的收藏")
def list_favorites(
    db: Session = Depends(get_db),
    user: SysUser = Depends(get_current_user),
) -> dict[str, Any]:
    """我的收藏列表（需登录）；同时提供 fav_* 与 type/favId/favName 两套字段。"""
    favorites = (
        db.execute(
            select(UserFavorite)
            .where(UserFavorite.user_id == user.id)
            .order_by(UserFavorite.create_time.desc(), UserFavorite.id.desc())
        )
        .scalars()
        .all()
    )
    data: list[dict[str, Any]] = []
    for favorite in favorites:
        create_ms = (
            int(favorite.create_time.timestamp() * 1000) if favorite.create_time else None
        )
        data.append(
            {
                "id": favorite.id,
                "fav_type": favorite.fav_type,
                "fav_id": favorite.fav_id,
                "fav_name": favorite.fav_name or "",
                "create_time": favorite.create_time.strftime("%Y-%m-%d %H:%M:%S")
                if favorite.create_time
                else None,
                # 前端兼容字段（与 mock 收藏结构对齐）
                "type": favorite.fav_type,
                "favId": favorite.fav_id,
                "favName": favorite.fav_name or "",
                "fav_time": create_ms,
            }
        )
    return ok(data)
