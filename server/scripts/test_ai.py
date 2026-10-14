"""火山方舟 AI 连通性测试脚本。

用法（在 server/ 目录下运行）：
    python scripts/test_ai.py

会读取 .env 中的 AI_API_KEY / AI_BASE_URL / AI_MODEL，向火山方舟发起一次
真实的 chat/completions 调用，打印返回结果。若未配置 Key 会提示并退出。
"""
from __future__ import annotations

import sys
from pathlib import Path

import httpx

# 允许从 server/ 目录直接运行：把 server/ 加入 sys.path 以便 import app.core.config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402


def main() -> int:
    base_url = settings.AI_BASE_URL.rstrip("/")
    api_key = settings.AI_API_KEY
    model = settings.AI_MODEL

    print("=" * 60)
    print("火山方舟 AI 连通性测试")
    print("=" * 60)
    print(f"  Base URL : {base_url}")
    print(f"  Model    : {model}")
    print(f"  API Key  : {'已配置 (' + api_key[:6] + '...)' if api_key else '❌ 未配置'}")

    if not api_key:
        print("\n❌ 未配置 AI_API_KEY，请在 server/.env 中填入你的火山方舟 API Key 后重试。")
        print("   获取方式：https://console.volcengine.com/ark → 创建 API Key")
        return 1

    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是扬州非遗文化科普助手，回答简洁亲切。"},
            {"role": "user", "content": "用一句话介绍扬州剪纸。"},
        ],
        "temperature": 0.7,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    print(f"\n→ 请求地址：{url}")
    print("→ 发送测试问题：用一句话介绍扬州剪纸。\n")
    try:
        with httpx.Client(timeout=settings.AI_TIMEOUT_SECONDS) as client:
            resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            print(f"❌ 请求失败（HTTP {resp.status_code}）：")
            print("   " + resp.text[:800])
            return 1
        data = resp.json()
        content = data["choices"][0]["message"].get("content")
        print("✅ 调用成功！模型回复：")
        print("-" * 60)
        print(content)
        print("-" * 60)
        print("\nAI 接入已就绪，可正常用于剧本生成与智能问答。")
        return 0
    except httpx.HTTPError as exc:
        print(f"❌ 网络异常：{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
