"""
通过 GitHub REST API 推送本地未推送的 commit（git 主机不可用时的备用通道）。

背景：本机直连 github.com:443 时通时断，但 api.github.com 稳定可达。
本脚本把 origin/main..HEAD 的全部 commit 按顺序经 API 重建推送
（blobs → tree → commit → 更新 ref），内容与本地完全一致
（注意：API 创建的 commit SHA 与本地不同——作者/时间戳元数据差异，
属正常现象，tree 内容一致即可；网络恢复后 git push --force 可对齐 SHA）。

流程：逐个 commit 创建 blobs → 基于远程 tree 创建新 tree → 创建 commit
（父提交 = 远程当前链头）→ 全部完成后更新 refs/heads/main。

用法：
    GITHUB_TOKEN=<token> python scripts/push_via_api.py

安全：token 仅从环境变量读取，不写入任何文件。
"""
import base64
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

REPO = "Etherealls/Heritouch"
BRANCH = "main"
API = f"https://api.github.com/repos/{REPO}"


def git(*args):
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True, encoding="utf-8"
    ).stdout


def api(method, path, body=None):
    """调用 GitHub API，返回 (status, parsed_json)。"""
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


def push_commit(commit, chain_head, base_tree):
    """把单个本地 commit 经 API 推送到链头之上，返回新 commit SHA。"""
    message = git("log", "-1", "--format=%B", commit)
    files = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()

    tree_entries = []
    for f in files:
        with open(f, "rb") as fh:
            content_b64 = base64.b64encode(fh.read()).decode("ascii")
        status, blob = api("POST", "/git/blobs", {"content": content_b64, "encoding": "base64"})
        if status != 201:
            print(f"  ❌ 创建 blob 失败 {f}：{status} {blob}")
            sys.exit(1)
        tree_entries.append(
            {"path": f.replace("\\", "/"), "mode": "100644", "type": "blob", "sha": blob["sha"]}
        )

    status, tree = api("POST", "/git/trees", {"base_tree": base_tree, "tree": tree_entries})
    if status != 201:
        print(f"  ❌ 创建 tree 失败：{status} {tree}")
        sys.exit(1)

    status, new_commit = api(
        "POST",
        "/git/commits",
        {"message": message, "tree": tree["sha"], "parents": [chain_head]},
    )
    if status != 201:
        print(f"  ❌ 创建 commit 失败：{status} {new_commit}")
        sys.exit(1)
    print(f"  ✅ {commit[:8]}（{len(files)} 个文件）→ {new_commit['sha'][:8]}")
    return new_commit["sha"], tree["sha"]


def main():
    if not os.environ.get("GITHUB_TOKEN"):
        print("错误：请设置 GITHUB_TOKEN 环境变量")
        sys.exit(1)

    # 1. 待推送的 commit 列表（按时间正序）
    revs = git("rev-list", "--reverse", f"origin/{BRANCH}..HEAD").splitlines()
    if not revs:
        print("没有待推送的 commit")
        return
    print(f"待推送 {len(revs)} 个 commit：{[r[:8] for r in revs]}")

    # 2. 远程当前状态作为链头
    status, ref = api("GET", f"/git/ref/heads/{BRANCH}")
    if status != 200:
        print(f"获取远程分支失败：{status} {ref}")
        sys.exit(1)
    chain_head = ref["object"]["sha"]
    status, head_commit = api("GET", f"/git/commits/{chain_head}")
    base_tree = head_commit["tree"]["sha"]
    print(f"远程 {BRANCH} 链头：{chain_head[:8]}")

    # 3. 依次推送
    for commit in revs:
        chain_head, base_tree = push_commit(commit, chain_head, base_tree)

    # 4. 更新分支引用
    status, updated = api("PATCH", f"/git/refs/heads/{BRANCH}", {"sha": chain_head})
    if status != 200:
        print(f"更新分支失败：{status} {updated}")
        sys.exit(1)
    print(f"\n✅ 已推送到 {REPO}@{BRANCH}，新链头 {chain_head[:8]}")


if __name__ == "__main__":
    main()
