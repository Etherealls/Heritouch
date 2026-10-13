"""RAG 检索服务：ChromaDB 向量检索 + BGE Embedding。

降级策略：
- chromadb 未安装 / CHROMA_URL 不可达 / 本地持久化目录不可用时，
  自动降级为中文二元组关键词匹配，保证智能问答始终可用；
- LLM 增强问答：配置了 AI 文本服务时由大模型基于检索资料组织答案，
  未配置时直接基于检索结果拼装答案。
"""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

from app.core.config import settings
from app.services.ai_service import ai_service

logger = logging.getLogger("heritouch.rag")


def _bigrams(text: str) -> set[str]:
    """中文二元组切分（无分词依赖，适用于演示规模知识库）。"""
    cleaned = re.sub(r"\s+", "", text or "")
    if not cleaned:
        return set()
    if len(cleaned) == 1:
        return {cleaned}
    return {cleaned[i : i + 2] for i in range(len(cleaned) - 1)}


class RagService:
    """非遗知识库检索与问答服务。"""

    def __init__(self) -> None:
        self.enabled: bool = False
        self.client: Optional[Any] = None
        self.collection: Optional[Any] = None
        # 内存知识库（关键词降级与 Chroma 写入共用的文档源）
        self.docs: list[dict[str, Any]] = []
        self._init_chroma()

    def _init_chroma(self) -> None:
        """初始化 ChromaDB 客户端；失败则保持关键词降级模式。"""
        try:
            import chromadb  # 延迟导入，未安装时不影响其他服务

            if settings.CHROMA_URL:
                from urllib.parse import urlparse

                parsed = urlparse(settings.CHROMA_URL)
                self.client = chromadb.HttpClient(
                    host=parsed.hostname or "localhost", port=parsed.port or 8000
                )
            else:
                self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            self.collection = self.client.get_or_create_collection("heritouch_knowledge")
            self.enabled = True
            logger.info("ChromaDB 初始化成功，RAG 向量检索可用")
        except Exception as exc:  # noqa: BLE001 - 任何失败均降级
            logger.info("ChromaDB 不可用（%s），RAG 降级为关键词匹配", exc)
            self.enabled = False

    # ---------- 知识库加载 ----------
    def sync_knowledge(self, docs: Optional[list[dict[str, Any]]] = None) -> int:
        """从数据库加载非遗知识文档；ChromaDB 可用时同步写入向量库。

        :param docs: 外部传入的文档列表（测试用）；默认从 MySQL 加载
        :return: 加载的文档数量
        """
        if docs is None:
            docs = self._load_docs_from_db()
        self.docs = docs
        if self.enabled and docs:
            try:
                self.collection.upsert(
                    ids=[doc["id"] for doc in docs],
                    documents=[doc["text"] for doc in docs],
                    metadatas=[doc.get("metadata", {}) for doc in docs],
                )
                logger.info("RAG 知识库已写入 ChromaDB：%d 篇文档", len(docs))
            except Exception as exc:  # noqa: BLE001 - 写入失败仅告警
                logger.warning("写入 ChromaDB 失败，继续使用关键词匹配：%s", exc)
        logger.info("RAG 知识库就绪：%d 篇文档（向量检索：%s）", len(self.docs), self.enabled)
        return len(self.docs)

    def _load_docs_from_db(self) -> list[dict[str, Any]]:
        """从 MySQL 加载非遗项目与传承人知识文档。"""
        from sqlalchemy import select

        from app.core.database import SessionLocal
        from app.models.heritage import HeritageProject, Inheritor

        docs: list[dict[str, Any]] = []
        try:
            with SessionLocal() as session:
                projects = session.execute(select(HeritageProject)).scalars().all()
                for project in projects:
                    text = (
                        f"{project.name}。{project.intro or ''}"
                        f"{project.history or ''}{project.craft or ''}"
                    )
                    docs.append(
                        {
                            "id": f"project_{project.id}",
                            "text": text,
                            "metadata": {"type": "project", "ref_id": project.id, "name": project.name},
                            "keywords": [project.name, project.category, project.region],
                        }
                    )
                inheritors = session.execute(select(Inheritor)).scalars().all()
                for person in inheritors:
                    text = f"传承人{person.name}，{person.title or ''}。{person.biography or ''}"
                    docs.append(
                        {
                            "id": f"inheritor_{person.id}",
                            "text": text,
                            "metadata": {
                                "type": "inheritor",
                                "ref_id": person.id,
                                "name": person.name,
                            },
                            "keywords": [person.name, person.title or ""],
                        }
                    )
        except Exception as exc:  # noqa: BLE001 - 数据库异常时返回空知识库
            logger.warning("从数据库加载 RAG 知识库失败：%s", exc)
        return docs

    # ---------- 检索 ----------
    def query(self, question: str, top_k: int = 3) -> list[dict[str, Any]]:
        """检索相关问题相关资料，返回 [{id, text, score, metadata}]。"""
        if self.enabled:
            try:
                result = self.collection.query(query_texts=[question], n_results=top_k)
                hits: list[dict[str, Any]] = []
                ids = (result.get("ids") or [[]])[0]
                documents = (result.get("documents") or [[]])[0]
                metadatas = (result.get("metadatas") or [[]])[0]
                distances = (result.get("distances") or [[]])[0]
                for idx, doc_id in enumerate(ids):
                    hits.append(
                        {
                            "id": doc_id,
                            "text": documents[idx] if idx < len(documents) else "",
                            "score": round(1 - float(distances[idx]), 4)
                            if idx < len(distances)
                            else 0.0,
                            "metadata": metadatas[idx] if idx < len(metadatas) else {},
                        }
                    )
                if hits:
                    return hits
            except Exception as exc:  # noqa: BLE001 - 检索失败降级关键词
                logger.warning("ChromaDB 检索失败，降级关键词匹配：%s", exc)
        return self._keyword_search(question, top_k)

    def _keyword_search(self, question: str, top_k: int) -> list[dict[str, Any]]:
        """关键词匹配降级：二元组重合度 + 关键词命中加权。"""
        question_bigrams = _bigrams(question)
        scored: list[dict[str, Any]] = []
        for doc in self.docs:
            doc_bigrams = _bigrams(doc["text"])
            overlap = len(question_bigrams & doc_bigrams)
            keyword_hits = sum(3 for kw in doc.get("keywords", []) if kw and kw in question)
            name_hit = 5 if (doc.get("metadata", {}).get("name") or "") in question else 0
            score = overlap + keyword_hits + name_hit
            if score > 0:
                scored.append(
                    {
                        "id": doc["id"],
                        "text": doc["text"],
                        "score": float(score),
                        "metadata": doc.get("metadata", {}),
                    }
                )
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    # ---------- 问答 ----------
    def answer(self, question: str) -> dict[str, Any]:
        """RAG + LLM 问答；均不可用/无资料时给出引导性回复。"""
        hits = self.query(question)
        if not hits:
            return {
                "answer": (
                    f"关于「{question}」，扬州非遗知识库中暂未收录完全匹配的条目。"
                    "你可以试着询问扬州剪纸、扬州玉雕、扬州漆器、扬州早茶等主题，"
                    "我会基于知识库为你解答。"
                ),
                "sources": [],
                "rag_used": False,
            }
        context = "\n".join(hit["text"] for hit in hits[:2])
        llm_answer = ai_service.text.chat(
            system_prompt=(
                "你是扬州非遗科普讲解员。请根据给定参考资料回答用户问题，"
                "回答控制在 200 字以内，语气亲切，若资料不足请如实说明。"
            ),
            user_prompt=f"参考资料：\n{context}\n\n用户问题：{question}",
            temperature=0.3,
        )
        if llm_answer:
            answer_text = llm_answer.strip()
        else:
            answer_text = self._compose_answer(question, hits)
        return {
            "answer": answer_text,
            "sources": [
                {"id": hit["id"], "name": hit.get("metadata", {}).get("name", "")}
                for hit in hits
            ],
            "rag_used": True,
        }

    @staticmethod
    def _compose_answer(question: str, hits: list[dict[str, Any]]) -> str:
        """基于检索结果拼装答案（LLM 不可用时的降级）。"""
        best = hits[0]
        name = best.get("metadata", {}).get("name", "该项目")
        text = re.sub(r"\s+", "", best.get("text", ""))
        summary = text[:180] + ("……" if len(text) > 180 else "")
        return f"关于「{name}」：{summary}（以上内容来自非遗知识库检索）"


# 全局单例
rag_service = RagService()
