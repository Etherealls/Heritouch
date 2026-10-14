# -*- coding: utf-8 -*-
"""修复 .vue 样式块中缺少 display:flex 的问题。

uni-app 编译到 H5/APP 时 view 默认块级布局，仅写 flex-direction 不生效。
本脚本扫描所有 <style> 块中的 CSS 规则：
- 规则含 flex-direction / align-items / justify-content 但未声明 display:flex（或 grid/inline-flex 等已有布局）时，自动补 `display: flex;`
- 对横向滚动容器（.cat-row/.feature-row 类，由参数 --scroll-rows 指定文件中的选择器）补充 width: max-content，其子项补 flex-shrink: 0
"""
import io
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mobile-app')

FLEX_PROPS = re.compile(r'^\s*(flex-direction|align-items|justify-content)\s*:', re.M)
HAS_DISPLAY = re.compile(r'display\s*:\s*(flex|inline-flex|grid|inline-grid|block|none)\s*;')

# 横向滚动容器选择器 → (行选择器, 子项选择器)
SCROLL_ROWS = {
    ('pages/index/index.vue', '.cat-row'): '.cat-item',
    ('pages/index/index.vue', '.feature-row'): '.feature-card',
}


def fix_style(css, relpath):
    """按 } 切分规则块逐条修复，返回 (新css, 修改次数)。"""
    changed = 0
    out = []
    idx = 0
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        selector, body = m.group(1), m.group(2)
        sel = selector.strip()
        new_body = body
        if FLEX_PROPS.search(body) and not HAS_DISPLAY.search(body):
            new_body = '  display: flex;\n' + body.lstrip('\n ')
            changed += 1
        # 横向滚动容器：保证不换行且子项不被压缩
        if (relpath, sel) in SCROLL_ROWS:
            if 'max-content' not in new_body:
                new_body = new_body.rstrip() + '\n  width: max-content;\n'
                changed += 1
            out.append((selector, new_body))
            continue
        out.append((selector, new_body))
        # 子项 flex-shrink
        child = SCROLL_ROWS.get((relpath, sel))
    # 单独处理子项（也可能自身不满足 flex 补丁条件）
    # 重新拼接
    result = []
    pos = 0
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        pass
    return out, changed


def process_file(path, relpath):
    with io.open(path, encoding='utf-8') as f:
        src = f.read()

    total = 0

    def repl_style(match):
        nonlocal total
        prefix, css, suffix = match.group(1), match.group(2), match.group(3)
        new_css, n = fix_css(css, relpath)
        total += n
        return prefix + new_css + suffix

    new_src = re.sub(r'(<style[^>]*>)([\s\S]*?)(</style>)', repl_style, src)
    if new_src != src:
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(new_src)
    return total


def fix_css(css, relpath):
    """逐条规则：补 display:flex；横滑行补 width:max-content；横滑子项补 flex-shrink:0。"""
    changed = 0
    child_map = {sel: child for (f, sel), child in SCROLL_ROWS.items() if f == relpath}

    def rule_repl(m):
        nonlocal changed
        selector, body = m.group(1), m.group(2)
        sel = selector.strip()
        new_body = body
        if FLEX_PROPS.search(body) and not HAS_DISPLAY.search(body):
            new_body = body.replace(body.lstrip(), 'display: flex;\n  ' + body.lstrip(), 1)
            changed += 1
        if sel in child_map:
            if 'max-content' not in new_body:
                new_body = new_body.rstrip('\n') + '\n  width: max-content;'
                changed += 1
            child_sel = child_map[sel]
            if not re.search(re.escape(child_sel) + r'[^{]*\{[^}]*flex-shrink', css):
                changed += 1  # 标记需补子项（稍后统一加）
        return selector + '{' + new_body + '}'

    new_css = re.sub(r'([^{}]+)\{([^{}]*)\}', rule_repl, css)

    # 为横滑子项补 flex-shrink: 0（若尚无）
    for sel, child_sel in child_map.items():
        pattern = re.compile('(' + re.escape(child_sel) + r'[^{]*)\{([^}]*)\}')
        def child_repl(m):
            nonlocal changed
            s, b = m.group(1), m.group(2)
            if 'flex-shrink' in b:
                return m.group(0)
            changed += 1
            return s + '{' + b.rstrip() + '\n  flex-shrink: 0;\n}'
        new_css = pattern.sub(child_repl, new_css)

    return new_css, changed


def main():
    grand = 0
    for dirpath, _, files in os.walk(ROOT):
        # 跳过 node_modules / 构建产物
        if 'node_modules' in dirpath or 'unpackage' in dirpath or 'dist' in dirpath:
            continue
        for name in files:
            if not name.endswith('.vue'):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT).replace('\\', '/')
            n = process_file(full, rel)
            if n:
                print(f'{rel}: 修复 {n} 处')
                grand += n
    print(f'\n共修复 {grand} 处')


if __name__ == '__main__':
    main()
