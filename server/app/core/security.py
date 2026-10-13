"""Token 生成与解析。

采用类 JWT 的 HMAC-SHA256 签名实现（header.payload.signature），
不依赖第三方 JWT 库；签名密钥取自配置 SECRET_KEY，支持过期时间。
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid

from app.core.config import settings

_ALGORITHM = "HS256"


def _b64url_encode(raw: bytes) -> str:
    """Base64URL 编码（去掉填充等号）。"""
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    """Base64URL 解码（自动补足填充）。"""
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(signing_input: str) -> str:
    """使用 SECRET_KEY 对签名输入做 HMAC-SHA256。"""
    digest = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _b64url_encode(digest)


def create_token(user_id: int, expires_hours: int | None = None) -> str:
    """为用户生成登录 token。

    :param user_id: 用户主键
    :param expires_hours: 有效期（小时），默认取配置 TOKEN_EXPIRE_HOURS
    :return: 形如 <header>.<payload>.<signature> 的 token 字符串
    """
    hours = expires_hours if expires_hours is not None else settings.TOKEN_EXPIRE_HOURS
    now = int(time.time())
    header = {"alg": _ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + hours * 3600,
        "jti": uuid.uuid4().hex,
    }
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}"
    return f"{signing_input}.{_sign(signing_input)}"


def decode_token(token: str) -> int | None:
    """解析并校验 token，返回用户 ID；签名不符、格式错误或已过期返回 None。"""
    try:
        header_b64, payload_b64, signature = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}"
        # 常量时间比较，防时序攻击
        if not hmac.compare_digest(signature, _sign(signing_input)):
            return None
        payload = json.loads(_b64url_decode(payload_b64))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return int(payload["sub"])
    except Exception:  # noqa: BLE001 - 任何解析失败均视为无效 token
        return None


def generate_device_openid() -> str:
    """前端未提供 openid 时，生成设备唯一标识（与前端 dev_ 前缀风格一致）。"""
    return f"dev_{uuid.uuid4().hex[:12]}"
