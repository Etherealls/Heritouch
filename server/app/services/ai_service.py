"""AI 创作服务：文本（剧本/问答）与图像（纹样/画作）生成。

设计要点：
- 统一 AIProvider 抽象：TextProvider（OpenAI 兼容接口，豆包/通义千问等）与
  ImageProvider（Stable Diffusion API）；
- 未配置 API Key / BaseURL 时自动降级为本地 Mock（含风格化 Prompt 模板与
  合理延迟模拟），保证无外部依赖可完整体验；
- 每种非遗风格内置专属 Prompt 模板，融入工艺特点、色彩特征与构图规则
  （开发文档 4.2.3）；
- 所有生成结果 ai_created=True，并附加风格来源标注字段。
"""
from __future__ import annotations

import json
import logging
import random
import re
import time
import uuid
from typing import Any, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("heritouch.ai")


# =====================================================================
# 非遗风格 Prompt 模板（开发文档 4.2.3：工艺特点 + 色彩特征 + 构图规则）
# =====================================================================
STYLE_PROMPTS: dict[str, dict[str, str]] = {
    "yangzhou_papercut": {
        "name": "扬州剪纸",
        "prompt": (
            "扬州剪纸，中国剪纸南派代表，艺术特色为“细、秀、雅、活”。"
            "工艺特点：以尖口小剪在宣纸或彩纸上运剪，线条细如发丝、婉转流畅，"
            "讲究“千刻不落、万剪不断”的镂空连通技法，点色剪纸采用一手剪、一手染。"
            "色彩特征：以大红为主色，辅以金、黑、绿点缀，喜庆热烈。"
            "构图规则：对称饱满、均衡灵动，常见团花、花鸟虫鱼、戏曲人物与吉祥纹样，"
            "适合方形或圆形适合纹样构图。"
        ),
    },
    "lacquer_pattern": {
        "name": "漆器纹样",
        "prompt": (
            "扬州漆器纹样，源自两千四百年髹饰传统。"
            "工艺特点：与雕漆、点螺、平磨螺钿、骨石镶嵌等工艺相配，纹样深峻富丽。"
            "色彩特征：以朱红、藏黑、鎏金为主色调，螺钿呈现青、紫、绿等幻彩。"
            "构图规则：多层环绕、中心对称，常见云纹、卷草、宝相花与山水人物纹，"
            "适合器皿展开图或屏风连续纹样构图。"
        ),
    },
    "jade_carving": {
        "name": "玉雕图案",
        "prompt": (
            "扬州玉雕图案，体现“浑厚圆润、儒雅灵秀”的扬州工风格。"
            "工艺特点：因材施艺、因色取巧，圆雕、浮雕、镂空雕层叠推进，山子雕大气磅礴。"
            "色彩特征：保留和田玉青白、碧玉翠绿、黄玉暖黄的天然玉质与皮色。"
            "构图规则：随形就势、虚实相生，人物山水寄于玉石轮廓之内，"
            "适合立幅或山子剖面式构图。"
        ),
    },
    "blue_calico": {
        "name": "蓝印花布",
        "prompt": (
            "扬州蓝印花布纹样，江淮传统植物染织工艺。"
            "工艺特点：黄豆粉加石灰刮浆防染，靛缸低温多次浸染，形成冰裂纹理。"
            "色彩特征：靛蓝与纯白两色相映，蓝得沉着、白得洁净，朴素典雅。"
            "构图规则：蓝白对比鲜明，常见凤穿牡丹、五福捧寿、吉祥花鸟等图案，"
            "适合连续四方纹或中心团花构图。"
        ),
    },
    "lacquer_painting": {
        "name": "漆画",
        "prompt": (
            "扬州漆画，漆器髹饰技艺与绘画结合的画种。"
            "工艺特点：以大漆、蛋壳、螺钿、金箔为材，髹涂、镶嵌、研磨、推光数十道工序。"
            "色彩特征：黑漆底上鎏金溢彩，蛋壳呈冰白肌理，红漆温润深沉。"
            "构图规则：借鉴中国画章法，虚实留白、计白当黑，适合装饰性构图。"
        ),
    },
    "ink_painting": {
        "name": "水墨画",
        "prompt": (
            "江南水墨画风格，取法扬州画派“笔墨灵变、跌宕纵横”的意趣。"
            "工艺特点：以毛笔水墨写意，浓淡干湿、皴擦点染一气呵成。"
            "色彩特征：墨分五色（焦浓重淡清），偶施浅绛青绿，素雅清远。"
            "构图规则：三远法布局（高远、深远、平远），留白透气，适合立轴或册页构图。"
        ),
    },
    "new_year_painting": {
        "name": "年画",
        "prompt": (
            "中国传统木版年画风格，民俗节庆气息浓郁。"
            "工艺特点：木版套印加手工彩绘，线条粗犷有力，色彩平涂饱满。"
            "色彩特征：桃红、槐黄、翠绿、紫、黑五色鲜亮对比，喜庆欢快。"
            "构图规则：画面丰满均衡、主次分明，常见门神、胖娃娃、五谷丰登题材，"
            "适合对开或斗方式构图。"
        ),
    },
    "embroidery": {
        "name": "刺绣",
        "prompt": (
            "扬州刺绣风格，以仿古绣与水墨绣著称，有“针画”之誉。"
            "工艺特点：以针代笔、以线代墨，虚实针、散套针层层晕染，绣理细腻。"
            "色彩特征：桑蚕丝线劈丝细如发，色阶过渡自然，雅致温和。"
            "构图规则：临摹书画原作章法，讲求画绣一体，适合册页或立轴式构图。"
        ),
    },
}

# 风格别名映射：兼容中文名称与常见写法，统一归一到模板 key
STYLE_ALIASES: dict[str, str] = {
    "扬州剪纸": "yangzhou_papercut",
    "剪纸": "yangzhou_papercut",
    "papercut": "yangzhou_papercut",
    "漆器纹样": "lacquer_pattern",
    "漆器": "lacquer_pattern",
    "lacquer": "lacquer_pattern",
    "玉雕图案": "jade_carving",
    "玉雕": "jade_carving",
    "jade": "jade_carving",
    "蓝印花布": "blue_calico",
    "蓝染": "blue_calico",
    "calico": "blue_calico",
    "漆画": "lacquer_painting",
    "lacquer_painting": "lacquer_painting",
    "水墨画": "ink_painting",
    "水墨": "ink_painting",
    "ink": "ink_painting",
    "年画": "new_year_painting",
    "new_year": "new_year_painting",
    "刺绣": "embroidery",
    "扬绣": "embroidery",
    "embroidery": "embroidery",
}

# AI 生成占位图（未配置图像 API 时返回，文件位于 server/static/images/）
PLACEHOLDER_IMAGE_URL = f"{settings.STATIC_URL_PREFIX}/images/gen-placeholder.svg"


def resolve_style(style: str) -> str:
    """将任意风格入参归一化为模板 key，未知风格默认扬州剪纸。"""
    key = (style or "").strip()
    if key in STYLE_PROMPTS:
        return key
    alias = STYLE_ALIASES.get(key) or STYLE_ALIASES.get(key.lower())
    return alias if alias else "yangzhou_papercut"


def build_image_prompt(prompt: str, style: str) -> str:
    """融合风格模板与用户主题，构造完整绘图 Prompt。"""
    template = STYLE_PROMPTS[resolve_style(style)]
    return f"{template['prompt']}创作主题：{prompt.strip()}。"


def _mock_delay(low: float = 0.4, high: float = 1.2) -> None:
    """Mock 生成延迟模拟（可在 .env 中用 MOCK_DELAY=false 关闭）。"""
    if settings.MOCK_DELAY:
        time.sleep(random.uniform(low, high))


def _extract_json(text: str) -> Optional[dict[str, Any]]:
    """从模型输出中提取 JSON（容忍 ```json 代码块与前后缀文本）。"""
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.S)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            candidate = text[start : end + 1]
    if not candidate:
        return None
    try:
        data = json.loads(candidate)
        return data if isinstance(data, dict) else None
    except (ValueError, TypeError):
        return None


class TextProvider:
    """文本生成 Provider：OpenAI 兼容接口（豆包/通义千问等），未配置则 Mock。"""

    def __init__(self) -> None:
        self.enabled: bool = bool(settings.AI_API_KEY and settings.AI_BASE_URL)
        self.base_url: str = settings.AI_BASE_URL.rstrip("/")
        self.api_key: str = settings.AI_API_KEY
        self.model: str = settings.AI_MODEL
        self.timeout: float = settings.AI_TIMEOUT_SECONDS

    def chat(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> Optional[str]:
        """发起对话补全；不可用或调用失败返回 None（调用方走本地 Mock）。"""
        if not self.enabled:
            logger.info("AI 文本服务未配置，使用本地 Mock 生成")
            return None
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
            }
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001 - 网络/协议错误统一降级
            logger.warning("AI 文本调用失败，降级为本地 Mock：%s", exc)
            return None


class ImageProvider:
    """图像生成 Provider：Stable Diffusion API，未配置则返回占位图 URL。"""

    def __init__(self) -> None:
        self.enabled: bool = bool(settings.IMAGE_API_URL)
        self.api_url: str = settings.IMAGE_API_URL.rstrip("/")
        self.api_key: str = settings.IMAGE_API_KEY
        self.timeout: float = settings.IMAGE_TIMEOUT_SECONDS

    def generate(self, prompt: str, size: str = "1024x1024", image: Optional[str] = None) -> dict[str, Any]:
        """生成图片，返回 {url, provider, task_id}；不可用时返回占位图。"""
        if not self.enabled:
            logger.info("AI 图像服务未配置，返回占位图")
            _mock_delay(0.8, 2.0)
            return {
                "url": PLACEHOLDER_IMAGE_URL,
                "provider": "placeholder",
                "task_id": uuid.uuid4().hex,
            }
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            payload: dict[str, Any] = {"prompt": prompt, "size": size}
            if image:
                payload["init_image"] = image  # 图生图：base64 输入图
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(f"{self.api_url}/generate", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
            # 兼容 {url} 与 OpenAI 风格 {data:[{url}]} 两种响应
            url = data.get("url") or (data.get("data") or [{}])[0].get("url")
            if not url:
                raise ValueError("图像 API 响应中未找到 url 字段")
            return {"url": url, "provider": "stable-diffusion", "task_id": uuid.uuid4().hex}
        except Exception as exc:  # noqa: BLE001 - 网络/协议错误统一降级
            logger.warning("AI 图像调用失败，降级为占位图：%s", exc)
            return {
                "url": PLACEHOLDER_IMAGE_URL,
                "provider": "placeholder",
                "task_id": uuid.uuid4().hex,
            }


# 剧本 Mock 数据池（AI 不可用时的本地模板生成）
_MOCK_ROLE_POOL = ["旁白", "老师傅", "徒弟", "青年", "阿婆", "小传承人"]
_MOCK_SCENE_TITLES = [
    ("开场·溯源", "【旁白】扬州非遗，千年文脉。今天我们要讲的是「{theme}」的故事。{dialect}"),
    ("传承·技艺", "【老师傅】这门手艺讲究的是心到、眼到、手到，一板一眼都马虎不得。\n【徒弟】师父，这第一步该从哪里下手？\n【老师傅】莫急，先把心静下来。"),
    ("焕新·传承", "【青年】老手艺也能有新玩法，我们用短视频让更多年轻人看见它。\n【老师傅】好啊，传承不守旧，创新不忘本。"),
    ("匠心·坚守", "【老师傅】一件作品从选料到成品，要经过几十道工序，少一道就不是那个味道。\n【徒弟】原来如此，弟子受教了。"),
    ("民俗·印记", "【阿婆】这项手艺啊，和咱扬州人的婚丧嫁娶、岁时节庆都分不开，是刻在日子里的记忆。\n【小传承人】奶奶，我长大了也要学！"),
    ("礼成·展望", "【旁白】一技传千年，匠心永流转。愿「{theme}」在老手艺人与年轻传承者手中，代代相传、生生不息。"),
]


class AIService:
    """AI 创作门面：纹样 / 剧本 / 画作生成（统一降级策略）。"""

    def __init__(self) -> None:
        self.text = TextProvider()
        self.image = ImageProvider()

    # ---------- 纹样生成 ----------
    def generate_pattern(self, prompt: str, style: str, size: str = "1024x1024") -> dict[str, Any]:
        """生成非遗纹样，返回 {task_id, image_url, style, prompt, ai_created, ...}。"""
        style_key = resolve_style(style)
        template = STYLE_PROMPTS[style_key]
        full_prompt = build_image_prompt(prompt, style_key)
        result = self.image.generate(full_prompt, size)
        return {
            "task_id": result["task_id"],
            "image_url": result["url"],
            "style": style_key,
            "style_label": template["name"],
            "style_source": f"非遗风格模板：{template['name']}",
            "prompt": prompt,
            "full_prompt": full_prompt,
            "size": size,
            "provider": result["provider"],
            "ai_created": True,
        }

    # ---------- 剧本生成 ----------
    def generate_script(
        self, theme: str, duration: int = 5, dialect: bool = False, role_count: int = 3
    ) -> dict[str, Any]:
        """生成科普剧本，返回 {theme, duration, dialect, scenes, roles, ai_created}。"""
        system_prompt = (
            "你是扬州非遗科普编剧。请根据用户给出的主题生成一段非遗科普小剧本，"
            "严格输出 JSON，不要输出多余内容。JSON 结构："
            '{"scenes": [{"scene": 1, "title": "场景标题", "content": "台词内容（含【角色】前缀）", '
            '"roles": ["角色1", "角色2"]}], "roles": ["全部角色名"]}。'
            "台词需体现非遗工艺特点与扬州地域文化。"
        )
        user_prompt = (
            f"主题：{theme}；时长约 {duration} 分钟；"
            f"角色数量：{role_count}；{'请使用扬州方言词汇演绎' if dialect else '使用普通话'}。"
        )
        raw = self.text.chat(system_prompt, user_prompt)
        parsed = _extract_json(raw) if raw else None
        if parsed and parsed.get("scenes"):
            scenes = [
                {
                    "scene": int(s.get("scene", idx + 1)),
                    "title": str(s.get("title", f"第{idx + 1}幕")),
                    "content": str(s.get("content", "")),
                    "roles": [str(r) for r in (s.get("roles") or [])],
                }
                for idx, s in enumerate(parsed["scenes"])
            ]
            roles = [str(r) for r in (parsed.get("roles") or [])] or _mock_roles(role_count)
        else:
            _mock_delay(0.8, 1.8)
            scenes, roles = _mock_script(theme, duration, dialect, role_count)
        return {
            "theme": theme,
            "duration": duration,
            "dialect": dialect,
            "scenes": scenes,
            "roles": roles,
            "ai_created": True,
        }

    # ---------- 画作生成 ----------
    def generate_painting(
        self, mode: str = "text", prompt: str = "", style: str = "lacquer_painting", image: Optional[str] = None
    ) -> dict[str, Any]:
        """生成非遗风格画作（文生图 / 图生图），返回结构与纹样一致并附加 mode。"""
        style_key = resolve_style(style)
        template = STYLE_PROMPTS[style_key]
        full_prompt = build_image_prompt(prompt, style_key)
        if mode == "image":
            full_prompt += "以输入图片为构图基础进行图生图再创作，保持参考图主体结构。"
        result = self.image.generate(full_prompt, image=image)
        return {
            "task_id": result["task_id"],
            "image_url": result["url"],
            "style": style_key,
            "style_label": template["name"],
            "style_source": f"非遗风格模板：{template['name']}",
            "prompt": prompt,
            "full_prompt": full_prompt,
            "mode": mode,
            "provider": result["provider"],
            "ai_created": True,
        }


def _mock_roles(role_count: int) -> list[str]:
    """Mock 角色表：按数量从角色池截取。"""
    return _MOCK_ROLE_POOL[: max(1, min(role_count, len(_MOCK_ROLE_POOL)))]


def _mock_script(
    theme: str, duration: int, dialect: bool, role_count: int
) -> tuple[list[dict[str, Any]], list[str]]:
    """本地 Mock 剧本：按时长推导幕数，逐幕套用模板。"""
    scene_count = max(2, min(len(_MOCK_SCENE_TITLES), round(duration / 2)))
    roles = _mock_roles(role_count)
    dialect_note = "（本幕使用扬州方言演绎）" if dialect else ""
    scenes: list[dict[str, Any]] = []
    for idx in range(scene_count):
        title, content_tpl = _MOCK_SCENE_TITLES[idx]
        content = content_tpl.format(theme=theme, dialect=dialect_note)
        # 每幕角色 = 全局角色表中与该幕台词相关的子集
        scene_roles = [r for r in roles if f"【{r}】" in content] or [roles[0]]
        scenes.append({"scene": idx + 1, "title": title, "content": content, "roles": scene_roles})
    return scenes, roles


# 全局单例（main.py 启动时即实例化，连接状态在各 Provider 内部惰性判断）
ai_service = AIService()
