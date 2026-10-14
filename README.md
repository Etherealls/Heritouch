# 指尖非遗 —— 地方非遗文化AI解码与传承平台（移动端）

[![技术栈](https://img.shields.io/badge/UniApp-Vue3-green)](https://uniapp.dcloud.net.cn/) [![后端](https://img.shields.io/badge/FastAPI-Python%203.10-teal)](https://fastapi.tiangolo.com/) [![数据库](https://img.shields.io/badge/MySQL%208.0-Neo4j%205-ChromaDB-blue)](https://www.mysql.com/)

> 一句话简介：**指尖非遗（Heritouch）是一款基于 UniApp 多端框架的地方非遗文化数字化平台，以扬州非遗为示范，融合知识图谱可视化、AI 互动创作、多模态智能导览与科普闯关，让非遗"看得见、听得懂、玩得动、传得开"。**

---

## 1. 项目背景

地方非物质文化遗产面临三大传承痛点：

| 痛点 | 现状描述 |
| --- | --- |
| **传播门槛高** | 非遗资料多为纸质文献与长视频，专业术语多、载体重，年轻人接触意愿低 |
| **展示形式单一** | 传统展板/网页以图文堆砌为主，缺乏关联解读与互动，难以呈现技艺间的脉络关系 |
| **传承后继乏人** | 传承人年龄结构老化，缺少面向青少年群体的轻量化、游戏化传播渠道 |

## 2. 项目目标

- **跨端复用**：一套 UniApp 代码同时产出 H5、微信小程序、安卓 APP、iOS APP，降低开发与维护成本；
- **非遗解码**：以知识图谱解构"项目—类别—传承人—朝代—材料—民俗"关联，让非遗知识可检索、可推理；
- **AI 互动**：接入大模型与文生图能力，提供纹样生成、科普剧本、非遗画作等低门槛创作体验；
- **轻量化体验**：默认 Mock 演示模式，无需后端即可完整跑通全部功能，适配教学与快速演示场景；
- **可复用地推**：数据层按城市维度设计（示范：扬州），更换种子数据即可复用到其他地域非遗。

## 3. 功能特性

平台围绕六大模块构建：

| 模块 | 核心功能点 |
| --- | --- |
| **非遗知识图谱可视化** | 力导图展示项目/类别/传承人/朝代/材料/民俗关联；按类别筛选；节点点击跳转详情 |
| **AI 互动创作** | 非遗纹样生成（SDXL+LoRA 风格化）；科普剧本生成（多角色台词，支持方言演绎）；非遗画作创作（文生图/图生图）；"我的作品"云端/本地管理 |
| **多模态智能导览** | 扫码导览（二维码解析项目 ID）；普通话/方言双语音讲解；RAG 智能问答（大模型 + 向量库检索）；离线音频缓存 |
| **科普闯关** | 5 大关卡渐进解锁；单选/判断/识图三类题型；实时判分与解析；段位积分与排行榜；错题本巩固 |
| **个人中心** | 微信登录；积分与段位展示；收藏管理（项目/传承人/作品）；我的作品；设置页切换真实服务器 |
| **后台管理** | 项目/传承人/关卡/题目内容维护；用户与作品数据查看；AI 生成内容统一标注管理 |

## 4. 系统架构

### 4.1 分层架构图

```
┌──────────────────────────────────────────────────────────────────────┐
│                        前端展示层（UniApp 多端）                        │
│   H5 │ 微信小程序 │ 安卓 APP │ iOS APP                                │
│   Vue3 + uView Plus + Pinia + uCharts + 条件编译（#ifdef）              │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ HTTP / JSON（/api/v1，Bearer Token）
┌───────────────────────────────▼──────────────────────────────────────┐
│                        业务逻辑层（FastAPI）                           │
│   路由 / 认证 / 参数校验（Pydantic） / 业务编排（SQLAlchemy ORM）        │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│                        算法服务层（AI 能力）                           │
│   豆包/通义千问（问答·剧本） │ SDXL+LoRA（纹样·画作）                    │
│   BGE-small-zh（向量化） │ 讯飞/Edge-TTS（语音合成）                    │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│                        数据存储层                                      │
│   MySQL 8.0（业务数据） │ Neo4j 5（知识图谱） │ ChromaDB（向量检索）     │
│   MinIO / 本地静态目录（图片·音频·二维码文件）                          │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.2 技术栈

| 分层 | 技术选型 | 说明 |
| --- | --- | --- |
| 前端 | UniApp + Vue3 | 一套代码编译多端 |
| 前端 | uView Plus | 移动端 UI 组件库 |
| 前端 | uCharts | 图表（积分趋势等） |
| 前端 | Pinia | 状态管理（用户态/收藏/作品） |
| 前端 | 条件编译 `#ifdef` | 处理 H5/小程序/APP 平台差异 |
| 后端 | Python 3.10 + FastAPI | 异步高性能 Web 框架，原生 OpenAPI 文档 |
| 后端 | Uvicorn | ASGI 服务器 |
| 后端 | Pydantic | 请求/响应模型校验 |
| 后端 | SQLAlchemy + PyMySQL | ORM 与 MySQL 连接池 |
| 后端 | Py2neo | Neo4j 图数据库驱动 |
| 存储 | MySQL 8.0 | 业务数据（InnoDB / utf8mb4） |
| 存储 | Neo4j 5.x | 非遗知识图谱 |
| 存储 | MinIO / 本地静态目录 | 图片、音频、二维码等文件 |
| 存储 | ChromaDB | 非遗知识向量库（RAG） |
| AI | 豆包 / 通义千问 API | 智能问答、科普剧本生成 |
| AI | SDXL + LoRA | 非遗风格纹样/画作图生图 |
| AI | 讯飞 / Edge-TTS | 普通话/方言语音合成 |
| AI | BGE-small-zh | 中文向量化模型（RAG 检索） |

## 5. 仓库目录结构

```
Heritouch/
├── mobile-app/                  # UniApp 前端工程（HBuilderX 导入）
│   ├── api/                     # 接口封装 + Mock 数据源（默认演示模式）
│   ├── components/              # 公共组件（导航栏/力导图/空状态等）
│   ├── pages/                   # 页面（首页/图鉴/创作/导览/闯关/我的）
│   ├── store/                   # Pinia 状态管理
│   ├── utils/                   # 请求封装/全局配置/工具函数
│   ├── static/                  # 静态资源（图片/音频）
│   ├── main.js / App.vue / pages.json / manifest.json
│   └── package.json
├── server/                      # FastAPI 后端工程
│   ├── app/                     # main / core / models / schemas / api / services
│   ├── scripts/seed_data.py     # 一键灌数脚本（python -m scripts.seed_data）
│   ├── static/images/           # 占位图（封面/头像/作品/题目，SVG 矢量）
│   ├── requirements.txt / Dockerfile / .env.example
├── database/                    # 数据库脚本
│   ├── mysql/
│   │   ├── schema.sql           # 建库建表脚本
│   │   ├── seed.sql             # 扬州非遗演示数据（14 项目，默认兜底）
│   │   └── seed_national.sql    # 全国非遗数据（4234 项目/3959 传承人，由脚本生成）
│   └── neo4j/
│       ├── init.cypher          # 知识图谱初始化脚本（扬州演示）
│       └── init_national.cypher # 全国知识图谱初始化脚本（由脚本生成）
├── docs/
│   ├── API.md                   # REST API 接口文档
│   └── 开发文档.md               # 开发文档（Markdown 版，由 scripts/docx_to_md.py 提取）
├── scripts/
│   ├── gen_icons.py             # 图标生成工具脚本（PIL 绘制 tabBar 图标与 Logo）
│   ├── docx_to_md.py            # 开发文档 docx → Markdown 提取脚本
│   ├── crawl_ihchina.py         # 数据采集：抓取 ihchina.cn 全国非遗名录
│   ├── build_seed_national.py   # 数据转换：全国名录 → seed_national.json
│   ├── build_all_data.py        # 数据生成：seed_national.json → 前端 mock/MySQL/Neo4j
│   ├── check_imports.js         # 静态检查：页面 import 可解析性
│   ├── check_exports.js         # 静态检查：命名导入是否为目标模块真实导出
│   ├── check_sfc.js             # 静态检查：全部 .vue 的 SFC 编译校验
│   ├── check_scss.js            # 静态检查：全部 SCSS 样式块编译校验
│   ├── fix_uni_imports.js       # 修复工具：将误导入的 Vue API 拆分回 'vue'
│   └── repair_imports.js        # 修复工具：恢复导入丢失的兜底脚本
├── docker-compose.yml           # 一键编排：MySQL + Neo4j + API + ChromaDB
├── .gitignore
└── README.md
```

## 6. 快速开始

### 6.1 环境要求

| 方式 | 要求 |
| --- | --- |
| 完整开发 | Node.js 18+、HBuilderX 3.8+、Python 3.10+、MySQL 8.0、Neo4j 5.x |
| Docker 演示 | Docker 20+ 与 Docker Compose v2（无需本地安装数据库） |

### 6.2 方式一：Docker Compose 一键启动（推荐演示）

```bash
# 1. 克隆仓库后进入项目根目录
cd Heritouch

# 2. 一键启动 MySQL / Neo4j / API / ChromaDB
docker compose up -d

# 3. 查看容器状态
docker compose ps

# 4. 初始化知识图谱（可选，Neo4j 启动后执行一次）
docker compose exec neo4j cypher-shell -u neo4j -p password \
  -f /var/lib/neo4j/import/init.cypher
```

启动后访问地址：

| 服务 | 地址 | 账号 |
| --- | --- | --- |
| API 根路径 | http://localhost:5757/api/v1 | — |
| API 交互式文档 | http://localhost:5757/docs | — |
| Neo4j 浏览器 | http://localhost:7474 | neo4j / password |
| MySQL | localhost:3306 | root / heritouch |
| ChromaDB | http://localhost:8001 | — |

> 首次启动 MySQL 会自动执行 `database/mysql/schema.sql` 与 `seed.sql` 完成建库灌数；数据卷已持久化，重复启动不会重复初始化。

### 6.3 方式二：手动部署（本地开发）

**后端：**

```bash
cd server
pip install -r requirements.txt      # 安装依赖
cp .env.example .env                 # 配置数据库/AI 密钥（按注释填写）
python -m scripts.seed_data          # 一键灌数（MySQL 结构+数据、Neo4j 图谱）
uvicorn app.main:app --reload        # 启动服务，默认 http://localhost:5757

# 真机/局域网调试时，需监听所有网卡（否则手机连不上）：
uvicorn app.main:app --reload --host 0.0.0.0 --port 5757
```

**前端：**

```bash
# 1. 生成应用图标（tabBar 图标 + Logo，PIL 绘制，约 10 秒）
pip install Pillow
python scripts/gen_icons.py

# 2. 安装前端依赖（提供 pinia / sass / vue 等运行时依赖；
#    @dcloudio/* 由 HBuilderX 内部编译器提供，此处安装用于 CLI 构建与模块解析）
cd mobile-app
npm install
```

2. HBuilderX → 文件 → 导入目录，选择 `mobile-app/`（项目为 **uni-app Vue3 经典布局**：`manifest.json`、`pages.json`、`index.html` 均位于 `mobile-app/` 根目录，首次运行若提示"项目模板是否支持 vue3 / 缺少 index.html"，确认这三者在根目录即可）；
3. HBuilderX → 运行 → 运行到浏览器（H5 调试）/ 运行到小程序模拟器 / 运行到手机或模拟器；
4. 默认 `useMock=true`，无需后端即可体验；接入真实后端见第 8 节。

## 7. 多端编译说明

| 目标平台 | 编译步骤 | 注意事项 |
| --- | --- | --- |
| **H5** | HBuilderX → 发行 → uniapp 版 H5；或 `npm run build:h5` | 浏览器调试最方便；语音等原生能力自动降级 |
| **微信小程序** | HBuilderX → 发行 → 小程序-微信，生成目录后用微信开发者工具导入 | 必须配置 **request/socket/uploadFile/downloadFile 合法域名**（见 FAQ）；`uni.scanCode` 需企业主体或相应类目 |
| **安卓 APP** | HBuilderX → 发行 → 原生 App-云打包，选择 Android，配置名称/图标/启动页生成 APK | 免费云打包需 DCloud 账号；真机安装需允许未知来源 |
| **iOS APP** | HBuilderX → 发行 → 原生 App-云打包，需苹果开发者账号生成 IPA | 通过 TestFlight 分发测试；上架 App Store 需完整资质 |

> 平台差异通过条件编译处理，例如：`// #ifdef MP-WEIXIN ... // #endif`。

## 8. 演示模式说明（Mock 切换）

- **默认演示模式**：前端 `mobile-app/utils/config.js` 中 `useMock = true`，所有接口由本地 Mock 数据（`api/mock/data.js`）驱动，**无需后端即可完整体验**全部功能；
- **数据规模**：Mock 数据源为**全国非遗真实名录**（中国非物质文化遗产网 ihchina.cn，4234 个项目 / 3959 位传承人 / 10 大门类），由 `scripts/build_all_data.py` 生成 `api/mock/national-data.js`；
- **切换真实服务器**：进入「我的 → 设置 → 服务器配置」，填写后端地址（如 `http://localhost:5757/api/v1`）并关闭 Mock 开关即可；后端种子脚本 `server/scripts/seed_data.py` 会自动检测并灌入同一份全国数据；
- **真机/局域网调试**：手机与电脑连接**同一 WiFi**，在「我的 → 设置 → 服务器地址」填写电脑的局域网 IP（如 `http://192.168.1.100:5757/api/v1`，用 `ipconfig` 查看电脑 IPv4 地址），点击「测试连接」验证可达即可；后端需以 `--host 0.0.0.0` 启动，且 Windows 防火墙需放行 5757 端口。换网络后只需在设置页更新 IP，**无需重新打包**；
- **Mock 与真实接口契约一致**：Mock 层与 `docs/API.md` 中定义的请求/响应结构完全一致，切换时业务代码零改动。

> **关于图谱性能**：全国数据量达 8000+ 实体节点，移动端力导向图无法一次性渲染全部。图谱页默认展示「类别 → 代表项目」概览，点击类别筛选后展示该类项目与传承人子图（单类限流约 120 个项目，避免卡顿）。

## 9. API 文档

完整 REST API 文档见 [docs/API.md](docs/API.md)，涵盖非遗内容、知识图谱、AI 创作、导览服务、科普闯关、用户中心共 **28 个接口**，含请求参数、响应示例与错误码说明。FastAPI 启动后亦可访问交互式文档 `http://localhost:5757/docs`。

## 10. 数据来源与合规说明

- **公开数据来源**：项目名称、类别、级别、批次、简介等结构化信息来源于中国非物质文化遗产网（ihchina.cn）公开名录（通过 `scripts/crawl_ihchina.py` 采集）；
- **数据采集与生成**：`scripts/crawl_ihchina.py`（采集）→ `scripts/build_seed_national.py`（转换）→ `scripts/build_all_data.py`（生成前端 mock/MySQL/Neo4j 三份数据）；
- **演示数据声明**：闯关题目、智能问答回复为**演示内容**；部分扩展项目（如刺绣类）的类别按名称推断，个别简介为名录原始描述，正式发布前建议经非遗研究领域专家审校；
- **AI 内容合规**：所有 AI 生成内容（纹样、剧本、画作、问答答案）在界面中统一标注 **"AI 创作"** 标识，数据库作品表以 `prompt` 字段留存创作提示词以便溯源；
- **非商业用途**：本项目为教学实训与非遗公益传播演示，不作商业用途；图片音频资源如涉版权请联系替换。

## 11. 开发路线图（8 周精简表）

| 阶段 | 周期 | 核心任务 | 里程碑产出 |
| --- | --- | --- | --- |
| W1 需求与设计 | 第 1 周 | 需求调研、原型设计、数据库与接口设计 | 原型图、schema.sql、API 文档 |
| W2 基础框架 | 第 2 周 | 前端脚手架、后端框架、登录与基础接口 | 可运行的工程骨架 |
| W3 内容与图谱 | 第 3 周 | 内容管理接口、Neo4j 图谱构建与可视化 | 非遗图鉴 + 知识图谱页 |
| W4 AI 创作 | 第 4 周 | 对接 AI 接口，纹样/剧本/画作模块 | AI 创作全流程可用 |
| W5 导览能力 | 第 5 周 | 语音导览、扫码导览、RAG 智能问答、离线缓存 | 多模态导览闭环 |
| W6 闯关与中心 | 第 6 周 | 闯关游戏、积分排行、个人中心 | 游戏化学习闭环 |
| W7 多端适配 | 第 7 周 | 条件编译、真机调试、小程序审核材料 | 三端可安装包 |
| W8 测试收尾 | 第 8 周 | 单元/接口/兼容性测试、文档与答辩材料 | 可交付版本 |

## 12. 常见问题 FAQ

**Q1：前端请求后端报跨域错误（CORS）？**
A：后端已通过 FastAPI `CORSMiddleware` 放开跨域；若自行修改，请确认 `server/app/main.py` 中 `allow_origins` 包含你的前端地址。H5 调试建议后端开启 `--reload` 并保持 `http://localhost:5757` 访问。

**Q2：微信小程序报不在合法域名列表中？**
A：微信开发者工具 → 详情 → 本地设置 → 勾选"不校验合法域名"仅供开发调试；真机预览需在小程序后台（开发 → 开发管理 → 开发设置 → 服务器域名）将后端域名加入 `request`、`uploadFile`、`downloadFile` 合法域名列表，且必须为 HTTPS。

**Q3：Neo4j 连接失败，知识图谱页无数据？**
A：平台已做**降级处理**——图谱接口异常时自动返回内置关系数据，页面正常渲染并提示"图谱服务降级"。排查：确认 Neo4j 已启动（`docker compose ps`）、Bolt 端口 7687 可访问、`NEO4J_BOLT_URL` 指向正确服务名。

**Q4：如何在没有后端的情况下体验全部功能？**
A：保持 `useMock=true`（默认即此状态），所有数据来自 `mobile-app/api/mock/data.js`；接入真实后端时在设置页填写服务器地址并关闭 Mock 开关，详见第 8 节。

**Q5：MySQL 初始化脚本没有执行？**
A：`docker-entrypoint-initdb.d` 仅在数据卷为空（首次启动）时执行。如需重新灌数：`docker compose down -v` 删除卷后重新 `up -d`，或手动执行 `mysql -uroot -pheritouch heritouch < database/mysql/schema.sql && mysql -uroot -pheritouch heritouch < database/mysql/seed.sql`。

**Q6：克隆仓库后 tabBar 图标缺失 / 想看原始 Word 开发文档？**
A：仓库中的二进制资源（tabBar 图标 PNG、应用 Logo、原始 docx）均由脚本生成，首次使用请执行：
```bash
pip install Pillow python-docx
python scripts/gen_icons.py     # 生成 mobile-app/static/tab 图标与 logo.png
python scripts/docx_to_md.py    # 将 docs/ 下 docx 重新提取为 开发文档.md
```
原始 Word 文档请从项目负责人处获取放入 `docs/` 目录即可。

**Q7：HBuilderX 运行报“请确认您的项目模板是否支持 vue3：根目录缺少 index.html”？**
A：uni-app **Vue3** 编译器（Vite 模式）要求 `mobile-app/` 根目录存在 `index.html` 入口文件（Vue2 项目不需要），本仓库已包含该文件。若从旧版本克隆后仍报此错，确认 `mobile-app/index.html`、`manifest.json`、`pages.json` 三者都在 `mobile-app/` 根目录，且 `manifest.json` 中 `"vueVersion": "3"`。

**Q8：`python -m scripts.seed_data` 报 No module named scripts.seed_data / 启动报连接串错误？**
A：① 脚本名是 `seed_data`（数据），注意不是 `seed_date`，且必须在 `server/` 目录下执行；② 若报 `DATABASE_URL` 相关错误，检查 `server/.env`：该值必须是完整连接串（如 `mysql+pymysql://root:密码@localhost:3306/heritouch?charset=utf8mb4`），只填 `localhost:3306` 会被识别为非法配置并自动降级为 SQLite（`server/heritouch.db`）；③ 未配置 MySQL 时留空 `DATABASE_URL=` 即可零配置使用 SQLite。

**Q9：编译报 "xxx is not exported by @dcloudio/uni-app"？**
A：uni-app Vue3 的导入规范：**页面生命周期钩子**（`onLoad`/`onShow`/`onPullDownRefresh`/`onReachBottom`/`onUnload` 等）从 `@dcloudio/uni-app` 导入；**Vue 响应式 API**（`ref`/`reactive`/`computed`/`watch`/`nextTick` 等）必须从 `vue` 导入——uni-app 不导出这些。提交前可运行 `node scripts/check_exports.js` 自动校验全部命名导入。

---

© Heritouch 团队 · 地方非遗文化 AI 解码与传承平台 · 教学实训演示项目（非商业用途）
