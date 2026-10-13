"""服务层包：AI 创作 / 知识图谱 / RAG 检索 / 语音合成。

各服务在导入时即实例化单例，外部依赖不可用自动降级（见各模块文档字符串）。
"""
from app.services.ai_service import AIService, ai_service
from app.services.graph_service import GraphService, graph_service
from app.services.rag_service import RagService, rag_service
from app.services.tts_service import TTSService, tts_service

__all__ = [
    "AIService",
    "ai_service",
    "GraphService",
    "graph_service",
    "RagService",
    "rag_service",
    "TTSService",
    "tts_service",
]
