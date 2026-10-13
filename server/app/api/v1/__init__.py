"""API v1 路由汇总：统一前缀 /api/v1。"""
from fastapi import APIRouter

from app.api.v1 import ai, audio, game, heritage, knowledge_graph, user

api_router = APIRouter()

# 非遗内容
api_router.include_router(heritage.router, prefix="/heritage", tags=["非遗内容"])
# 知识图谱
api_router.include_router(knowledge_graph.router, prefix="/knowledge-graph", tags=["知识图谱"])
# AI 创作
api_router.include_router(ai.router, prefix="/ai", tags=["AI创作"])
# 语音导览（/audio/*）与扫码导览（/guide/*）
api_router.include_router(audio.router, prefix="/audio", tags=["语音导览"])
api_router.include_router(audio.guide_router, prefix="/guide", tags=["扫码导览"])
# 科普闯关
api_router.include_router(game.router, prefix="/game", tags=["科普闯关"])
# 用户中心
api_router.include_router(user.router, prefix="/user", tags=["用户中心"])
