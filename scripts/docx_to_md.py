# -*- coding: utf-8 -*-
"""将开发文档 docx 干净提取为 Markdown（段落 + 表格）"""
import docx
from docx.document import Document as _Doc
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

SRC = 'docs/地方非遗文化AI解码与传承平台.docx'
DST = 'docs/开发文档.md'

def iter_block_items(parent):
    """按文档顺序迭代段落与表格"""
    body = parent.element.body
    for child in body.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, parent)
        elif child.tag == qn('w:tbl'):
            yield Table(child, parent)

doc = docx.Document(SRC)
lines = []
for block in iter_block_items(doc):
    if isinstance(block, Paragraph):
        text = block.text.strip()
        if not text:
            continue
        style = (block.style.name or '').lower()
        if 'heading 1' in style:
            lines.append('\n# ' + text + '\n')
        elif 'heading 2' in style:
            lines.append('\n## ' + text + '\n')
        elif 'heading 3' in style:
            lines.append('\n### ' + text + '\n')
        elif 'heading 4' in style:
            lines.append('\n#### ' + text + '\n')
        else:
            lines.append(text)
    elif isinstance(block, Table):
        rows = []
        for r in block.rows:
            cells = [c.text.strip().replace('\n', ' ') for c in r.cells]
            rows.append(cells)
        if not rows:
            continue
        # 输出为 Markdown 表格
        lines.append('')
        header = rows[0]
        lines.append('| ' + ' | '.join(header) + ' |')
        lines.append('| ' + ' | '.join(['---'] * len(header)) + ' |')
        for r in rows[1:]:
            lines.append('| ' + ' | '.join(r) + ' |')
        lines.append('')

with open(DST, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('written:', DST, 'lines:', len(lines))
