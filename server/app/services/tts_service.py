"""语音合成服务（TTS）：Edge-TTS / 占位降级。

降级策略：
- TTS_PROVIDER=edge 且 edge-tts 可用时，合成 MP3 到 static/audio 并返回 URL；
- 其他情况（未安装 / 网络不可达 / 合成失败）返回占位信息（url 为空 + 估算时长），
  导览接口优先使用项目预置音频，保证功能可用。
"""
from __future__ import annotations

import logging
import math
import re
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger("heritouch.tts")

# 普通话讲解音色（Edge-TTS）
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
# 估算语速：约 240 字/分钟
CHARS_PER_MINUTE = 240


class TTSService:
    """语音合成服务。"""

    def __init__(self) -> None:
        self.provider = (settings.TTS_PROVIDER or "").strip().lower()
        self._edge: Optional[Any] = None
        if self.provider == "edge":
            try:
                import edge_tts  # noqa: F401 - 探测是否安装

                self._edge = edge_tts
                logger.info("Edge-TTS 可用")
            except Exception as exc:  # noqa: BLE001 - 未安装则占位降级
                logger.info("edge-tts 未安装（%s），TTS 使用占位降级", exc)

    @property
    def available(self) -> bool:
        """TTS 是否真实可用。"""
        return self._edge is not None

    @staticmethod
    def estimate_duration(text: str) -> int:
        """按语速估算朗读时长（秒）。"""
        cleaned = re.sub(r"\s+", "", text or "")
        return max(3, math.ceil(len(cleaned) / CHARS_PER_MINUTE * 60))

    def synthesize(self, text: str, voice: str = DEFAULT_VOICE) -> dict[str, Any]:
        """合成语音，返回 {url, duration, provider}；不可用时 url 为空。"""
        duration = self.estimate_duration(text)
        if self._edge is None:
            return {"url": "", "duration": duration, "provider": "placeholder"}
        try:
            import asyncio
            import os
            import uuid

            out_dir = "static/audio"
            os.makedirs(out_dir, exist_ok=True)
            filename = f"tts_{uuid.uuid4().hex[:12]}.mp3"
            file_path = os.path.join(out_dir, filename)

            async def _run() -> None:
                communicate = self._edge.Communicate(text, voice)
                await communicate.save(file_path)

            asyncio.run(_run())  # 同步端点内运行协程
            return {
                "url": f"/static/audio/{filename}",
                "duration": duration,
                "provider": "edge-tts",
            }
        except Exception as exc:  # noqa: BLE001 - 合成失败占位降级
            logger.warning("Edge-TTS 合成失败，返回占位音频信息：%s", exc)
            return {"url": "", "duration": duration, "provider": "placeholder"}

    def guide_audio(self, project: Any, lang: str = "mandarin") -> dict[str, Any]:
        """项目导览音频：优先预置音频，缺失时尝试 TTS 合成。

        :param project: HeritageProject ORM 对象
        :param lang: mandarin（普通话）/ dialect（方言）
        :return: {url, text, duration, source}
        """
        is_dialect = lang == "dialect"
        url = project.audio_dialect if is_dialect else project.audio_mandarin
        text = self._build_narration(project, is_dialect)
        if url:
            return {
                "url": url,
                "text": text,
                "duration": self.estimate_duration(text),
                "source": "preset",
            }
        tts = self.synthesize(text)
        return {
            "url": tts["url"],
            "text": text,
            "duration": tts["duration"],
            "source": tts["provider"],
        }

    @staticmethod
    def _build_narration(project: Any, is_dialect: bool) -> str:
        """根据项目资料构建讲解词。"""
        parts = [
            f"欢迎了解{project.name}。",
            project.intro or "",
            project.history or "",
            project.craft or "",
        ]
        narration = "".join(part for part in parts if part)
        if is_dialect:
            narration = f"【扬州方言导览】{narration}"
        return narration


# 全局单例
tts_service = TTSService()
