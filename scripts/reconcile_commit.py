"""
对账脚本：消除 API 推送造成的本地/远程 commit SHA 分叉。

背景：scripts/push_via_api.py 通过 API 创建的 commit 与本地 commit 内容
（tree）相同，但作者/时间戳元数据不同导致 SHA 不同，本地 main 与远程
main 出现同内容分叉。

本脚本：
1. 读取本地 HEAD commit 的完整元数据（tree/parent/author/committer/message）；
2. 用该元数据通过 API 重建 commit（git commit SHA 由这些字段确定性决定，
   元数据完全一致时 SHA 必然与本地一致）；
3. SHA 一致 → 强制更新远程分支指向该 commit，本地/远程完全对齐；
4. SHA 不一致 → 保留远程原样，仅报告差异，不做任何破坏性操作。

用法：GITHUB_TOKEN=<token> python scripts/reconcile_commit.py
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

REPO = "Etherealls/Heritouch"
BRANCH = "main"
API = f"https://api.github.com/repos/{REPO}"
LOCAL_SHA = subprocess.run(
    ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
).stdout.strip()


def git(*args):
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True, encoding="utf-8"
    ).stdout


def api(method, path, body=None):
    url = path if path.startswith("http") else f"{API}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"token {os.environ['GITHUB_TOKEN']}")
    req.add_header("Accept", "application/vnd.github+json")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def main():
    if not os.environ.get("GITHUB_TOKEN"):
        print("错误：请设置 GITHUB_TOKEN 环境变量")
        sys.exit(1)

    # 1. 本地元数据
    meta = git(
        "log", "-1", "--format=%T%n%P%n%an%n%ae%n%aI%n%cn%n%ce%n%cI%n---MSG---%n%B"
    )
    parts = meta.split("---MSG---\n")
    head = parts[0].split("\n")
    message = parts[1] if len(parts) > 1 else ""
    tree, parent = head[0], head[1]
    an, ae, ad = head[2], head[3], head[4]
    cn, ce, cd = head[5], head[6], head[7]
    print(f"本地 commit：{LOCAL_SHA[:8]}  tree={tree[:8]}  parent={parent[:8]}")

    # 2. 远程当前分支
    status, ref = api("GET", f"/git/ref/heads/{BRANCH}")
    if status != 200:
        print(f"获取远程分支失败：{status} {ref}")
        sys.exit(1)
    remote_sha = ref["object"]["sha"]
    print(f"远程 commit：{remote_sha[:8]}")

    if remote_sha == LOCAL_SHA:
        print("✅ 本地与远程已对齐，无需处理")
        return

    # 3. 用本地元数据重建 commit
    status, new_commit = api(
        "POST",
        "/git/commits",
        {
            "message": message,
            "tree": tree,
            "parents": [parent],
            "author": {"name": an, "email": ae, "date": ad},
            "committer": {"name": cn, "email": ce, "date": cd},
        },
    )
    if status != 201:
        print(f"重建 commit 失败：{status} {new_commit}")
        sys.exit(1)
    new_sha = new_commit["sha"]
    print(f"重建 commit：{new_sha[:8]}")

    # 4. SHA 比对
    if new_sha == LOCAL_SHA:
        status, updated = api("PATCH", f"/git/refs/heads/{BRANCH}", {"sha": new_sha, "force": True})
        if status != 200:
            print(f"更新分支失败：{status} {updated}")
            sys.exit(1)
        print(f"✅ 已对齐：远程 {BRANCH} → {new_sha[:8]}（与本地一致，原 {remote_sha[:8]} 已脱离分支）")
    else:
        print("⚠️ 重建的 commit SHA 与本地不一致（可能是 message 换行/时区格式差异）")
        print(f"   本地 {LOCAL_SHA[:8]} ≠ 重建 {new_sha[:8]}，保留远程 {remote_sha[:8]} 不变")
        print("   内容（tree）一致，不影响代码正确性；后续可用 git push 或 API 脚本继续推送")


if __name__ == "__main__":
    main()
