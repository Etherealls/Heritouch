"""应用配置：基于 pydantic-settings 从 .env / 环境变量读取配置。

所有外部依赖配置均可缺失：
- MySQL / Neo4j / ChromaDB / AI API Key 未配置时，各服务层自动降级；
- 保证服务在零配置（纯 SQLite + Mock）下可完整启动。
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置项（字段名与 .env 中的环境变量一一对应）。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- 应用基础 ----------
    APP_NAME: str = "Heritouch 地方非遗文化AI解码与传承平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ---------- 数据库 ----------
    # MySQL 连接串；留空时使用 SQLite（开发默认）
    DATABASE_URL: str = ""
    # MySQL 不可达时是否自动降级为 SQLite
    SQLITE_FALLBACK: bool = True
    SQLITE_URL: str = "sqlite:///./heritouch.db"

    # ---------- Neo4j 知识图谱 ----------
    NEO4J_URL: str = ""
    NEO4J_BOLT_URL: str = "bolt://localhost:7687"
    # 支持 "user/password" 合并写法（docker-compose 的 NEO4J_AUTH）与拆分写法
    NEO4J_AUTH: str = ""
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""

    # ---------- AI 文本服务（OpenAI 兼容接口：豆包 / 通义千问等） ----------
    AI_API_KEY: str = ""
    AI_BASE_URL: str = ""
    AI_MODEL: str = "doubao-pro-32k"
    AI_TIMEOUT_SECONDS: float = 30.0

    # ---------- AI 图像服务（Stable Diffusion API） ----------
    IMAGE_API_URL: str = ""
    IMAGE_API_KEY: str = ""
    IMAGE_TIMEOUT_SECONDS: float = 60.0

    # ---------- RAG 向量库（ChromaDB） ----------
    # CHROMA_URL 形如 http://localhost:8000；留空则使用本地持久化目录
    CHROMA_URL: str = ""
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    EMBEDDING_MODEL: str = "BAAI/bge-large-zh-v1.5"

    # ---------- 语音合成 ----------
    # edge = Edge-TTS；留空 = 占位降级
    TTS_PROVIDER: str = ""

    # ---------- 安全 ----------
    SECRET_KEY: str = "heritouch-dev-secret-please-change-in-production"
    TOKEN_EXPIRE_HOURS: int = 72

    # ---------- Mock 行为 ----------
    MOCK_DELAY: bool = True
    STATIC_URL_PREFIX: str = "/static"

    @property
    def neo4j_url(self) -> str:
        """Neo4j 连接地址：优先 NEO4J_URL，其次 NEO4J_BOLT_URL。"""
        return (self.NEO4J_URL or self.NEO4J_BOLT_URL or "").strip()

    @property
    def neo4j_auth(self) -> tuple[str, str]:
        """Neo4j 认证：优先 NEO4J_AUTH（user/password 合并写法），其次拆分字段。"""
        auth = (self.NEO4J_AUTH or "").strip()
        if auth and "/" in auth:
            user, _, password = auth.partition("/")
            return user, password
        return self.NEO4J_USER, self.NEO4J_PASSWORD


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例。"""
    return Settings()


settings: Settings = get_settings()
