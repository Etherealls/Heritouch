"""Token 生成与解析。

采用类 JWT 的 HMAC-SHA256 签名实现（header.payload.signature），
不依赖第三方 JWT 库；签名密钥取自配置 SECRET_KEY，支持过期时间。
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
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


# ---------------------------------------------------------------------
# 密码哈希（用户名 + 密码体系）
# ---------------------------------------------------------------------
# 采用 PBKDF2-HMAC-SHA256 加盐哈希（标准库实现，无第三方依赖），
# 存储格式：pbkdf2_sha256$<迭代次数>$<盐(hex)>$<哈希(hex)>
_PBKDF2_ITERATIONS = 200_000
_SALT_BYTES = 16


def hash_password(password: str) -> str:
    """对明文密码做加盐哈希，返回可存储的字符串。"""
    salt = os.urandom(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    )
    return (
        f"pbkdf2_sha256${_PBKDF2_ITERATIONS}$"
        f"{salt.hex()}${digest.hex()}"
    )


def verify_password(password: str, stored: str) -> bool:
    """校验明文密码与存储的哈希是否匹配；格式异常返回 False。"""
    try:
        algo, iterations, salt_hex, digest_hex = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, int(iterations)
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False
