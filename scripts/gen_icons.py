# -*- coding: utf-8 -*-
"""生成 Heritouch 移动端 tabBar 图标与应用 Logo（非遗风：朱砂红/黛青/泥金）"""
from PIL import Image, ImageDraw
import math, os

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mobile-app', 'static'))
os.makedirs(os.path.join(OUT, 'tab'), exist_ok=True)

S = 162  # 2x for crispness
C_GREY = (154, 143, 125, 255)   # normal
C_RED = (176, 58, 46, 255)      # active 朱砂红
C_GOLD = (201, 160, 99, 255)
C_TEAL = (63, 111, 106, 255)
BG = (255, 255, 255, 0)

def new_canvas():
    img = Image.new('RGBA', (S, S), BG)
    return img, ImageDraw.Draw(img)

def save(img, name):
    img.save(os.path.join(OUT, 'tab', name))

# ---------- 首页：房屋 ----------
def icon_index(color):
    img, d = new_canvas()
    cx = S / 2
    d.polygon([(cx, S*0.16), (S*0.16, S*0.48), (S*0.84, S*0.48)], outline=color, width=10)
    d.rectangle([S*0.26, S*0.48, S*0.74, S*0.84], outline=color, width=10)
    d.rectangle([S*0.44, S*0.60, S*0.56, S*0.84], outline=color, width=8)
    return img

# ---------- 图谱：节点网络 ----------
def icon_atlas(color):
    img, d = new_canvas()
    pts = [(S*0.5, S*0.20), (S*0.20, S*0.68), (S*0.80, S*0.68), (S*0.50, S*0.86)]
    for a, b in [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]:
        d.line([pts[a], pts[b]], fill=color, width=7)
    for p in pts:
        d.ellipse([p[0]-S*0.09, p[1]-S*0.09, p[0]+S*0.09, p[1]+S*0.09], fill=color)
    d.ellipse([pts[0][0]-S*0.13, pts[0][1]-S*0.13, pts[0][0]+S*0.13, pts[0][1]+S*0.13], outline=color, width=7)
    return img

# ---------- 创作：画笔 ----------
def icon_create(color):
    img, d = new_canvas()
    d.line([(S*0.24, S*0.78), (S*0.62, S*0.40)], fill=color, width=14)      # 笔杆
    d.polygon([(S*0.60, S*0.42), (S*0.80, S*0.22), (S*0.72, S*0.36)], fill=color)  # 笔尖
    d.arc([S*0.16, S*0.14, S*0.56, S*0.54], start=200, end=340, fill=color, width=9)  # 灵感弧线
    for ang, r in [(300, 0.10), (330, 0.13), (0, 0.10)]:
        x = S*0.5 + S*r*math.cos(math.radians(ang)); y = S*0.34 + S*r*math.sin(math.radians(ang))
        d.ellipse([x-6, y-6, x+6, y+6], fill=color)
    return img

# ---------- 闯关：勋章 ----------
def icon_game(color):
    img, d = new_canvas()
    d.polygon([(S*0.38, S*0.86), (S*0.28, S*0.52), (S*0.48, S*0.66)], fill=color)   # 绶带左
    d.polygon([(S*0.62, S*0.86), (S*0.72, S*0.52), (S*0.52, S*0.66)], fill=color)   # 绶带右
    d.ellipse([S*0.24, S*0.12, S*0.76, S*0.64], outline=color, width=10)            # 勋章外圈
    d.ellipse([S*0.33, S*0.21, S*0.67, S*0.55], outline=color, width=7)
    # 中心五角星
    cx, cy, r = S*0.5, S*0.38, S*0.14
    star = [(cx + r*math.sin(math.radians(a)), cy - r*math.cos(math.radians(a))) for a in range(0, 360, 72)]
    inner = []
    for a in range(36, 396, 72):
        inner.append((cx + r*0.45*math.sin(math.radians(a)), cy - r*0.45*math.cos(math.radians(a))))
    poly = []
    for i in range(5):
        poly.append(star[i]); poly.append(inner[i])
    d.polygon(poly, fill=color)
    return img

# ---------- 我的：人像 ----------
def icon_profile(color):
    img, d = new_canvas()
    d.ellipse([S*0.34, S*0.12, S*0.66, S*0.44], outline=color, width=10)
    d.arc([S*0.16, S*0.46, S*0.84, S*0.98], start=180, end=360, fill=color, width=10)
    return img

makers = {
    'index': icon_index,
    'atlas': icon_atlas,
    'create': icon_create,
    'game': icon_game,
    'profile': icon_profile,
}

for name, fn in makers.items():
    save(fn(C_GREY), name + '.png')
    save(fn(C_RED), name + '-active.png')

# ---------- 应用 Logo：印章风「遗」字 ----------
logo = Image.new('RGBA', (512, 512), (248, 245, 239, 255))
d = ImageDraw.Draw(logo)
d.rounded_rectangle([36, 36, 476, 476], radius=88, fill=(176, 58, 46, 255))
# 内框
d.rounded_rectangle([64, 64, 448, 448], radius=72, outline=(201, 160, 99, 255), width=8)
# 简化的「遗」字形（篆刻方块化处理）
cell = 52
ox, oy = 106, 106
glyph = [
    "0110011001100110",
    "0110011001100110",
    "1111111111111111",
    "0110011001100110",
    "0110011001100110",
    "1111111111111111",
    "0110011001100110",
    "0110011001100110",
]
for r, row in enumerate(glyph):
    for c, ch in enumerate(row):
        if ch == '1':
            d.rectangle([ox + c*cell, oy + r*cell, ox + (c+1)*cell - 8, oy + (r+1)*cell - 8], fill=(248, 245, 239, 255))
logo.save(os.path.join(OUT, 'logo.png'))

print('icons + logo generated:', sorted(os.listdir(os.path.join(OUT, 'tab'))), 'logo.png')
