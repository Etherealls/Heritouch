# Heritouch REST API 文档

| 项目 | 说明 |
| --- | --- |
| 项目名称 | Heritouch —— 地方非遗文化AI解码与传承平台 |
| 文档版本 | v1.0 |
| 接口风格 | RESTful，数据格式统一为 JSON |
| 基础路径 | `/api/v1` |
| 适用端 | H5 / 微信小程序 / 安卓 APP / iOS APP（多端共用同一套接口） |

## 目录

- [1. 通用说明](#1-通用说明)
  - [1.1 统一响应格式](#11-统一响应格式)
  - [1.2 认证方式](#12-认证方式)
  - [1.3 分页约定](#13-分页约定)
- [2. 非遗内容接口（5 个）](#2-非遗内容接口5-个)
- [3. 知识图谱接口（1 个）](#3-知识图谱接口1-个)
- [4. AI 创作接口（6 个）](#4-ai-创作接口6-个)
- [5. 多模态导览接口（4 个）](#5-多模态导览接口4-个)
- [6. 科普闯关接口（6 个）](#6-科普闯关接口6-个)
- [7. 用户中心接口（6 个）](#7-用户中心接口6-个)
- [8. 错误码表](#8-错误码表)
- [9. 附录：扫码二维码内容格式约定](#9-附录扫码二维码内容格式约定)

---

## 1. 通用说明

### 1.1 统一响应格式

所有接口返回统一的 JSON 信封结构：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 状态码，200 表示成功，其余见[错误码表](#8-错误码表) |
| message | string | 提示信息，成功为 "success"，失败为具体错误描述 |
| data | object/array/null | 业务数据，失败时为 null |

> 本文档各接口示例中，为节省篇幅仅展示 `data` 部分内容。

### 1.2 认证方式

除登录接口外，涉及用户数据的接口均需在请求头携带 Token（登录时下发）：

```http
Authorization: Bearer {token}
```

Token 由 `POST /user/login` 返回，有效期 7 天；过期后前端引导重新登录。

### 1.3 分页约定

列表类接口统一采用 `page`（页码，从 1 开始）+ `size`（每页条数，默认 20，最大 100）分页，返回结构为：

```json
{
  "total": 14,
  "list": []
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| total | int | 符合条件的总记录数 |
| list | array | 当前页数据列表 |

---

## 2. 非遗内容接口（5 个）

### 2.1 获取非遗分类列表

```http
GET /api/v1/heritage/categories
```

**请求参数**：无

**请求示例**：

```bash
curl http://localhost:8000/api/v1/heritage/categories
```

**响应示例**：

```json
[
  { "id": 1, "name": "传统技艺", "icon": "🔨", "count": 4 },
  { "id": 2, "name": "传统美术", "icon": "🎨", "count": 3 },
  { "id": 3, "name": "传统戏剧", "icon": "🎭", "count": 2 },
  { "id": 4, "name": "传统音乐", "icon": "🎵", "count": 2 },
  { "id": 5, "name": "曲艺", "icon": "📢", "count": 2 },
  { "id": 6, "name": "民俗", "icon": "🏮", "count": 1 },
  { "id": 7, "name": "传统医药", "icon": "🌿", "count": 1 }
]
```

**备注**：分类由项目表 `category` 字段聚合生成，无需独立分类表。

---

### 2.2 非遗项目检索列表

```http
GET /api/v1/heritage
```

**请求参数（Query）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| category | string | 否 | 按类别筛选，如 `传统美术` |
| level | string | 否 | 按级别筛选，如 `国家级` / `省级` |
| region | string | 否 | 按地区筛选（模糊匹配），如 `江苏扬州` |
| keyword | string | 否 | 关键词，匹配项目名称、简介、标签 |
| page | int | 否 | 页码，默认 1 |
| size | int | 否 | 每页条数，默认 20 |

**请求示例**：

```bash
curl "http://localhost:8000/api/v1/heritage?category=传统美术&page=1&size=20"
```

**响应示例**：

```json
{
  "total": 3,
  "list": [
    {
      "id": 1,
      "name": "扬州剪纸",
      "level": "国家级",
      "category": "传统美术",
      "region": "江苏扬州",
      "batch": 2006,
      "intro": "扬州剪纸是南方剪纸艺术的代表流派之一，以“细、秀、雅、活”著称……",
      "cover_image": "/static/images/paper-cut.jpg",
      "latitude": 32.394,
      "longitude": 119.412,
      "create_time": "2026-01-01T09:00:00"
    }
  ]
}
```

**备注**：列表返回摘要字段，不含 `history` / `craft` 长文本，详情见 2.3。

---

### 2.3 获取非遗项目详情

```http
GET /api/v1/heritage/{id}
```

**请求参数（Path）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | 是 | 非遗项目 ID |

**请求示例**：

```bash
curl http://localhost:8000/api/v1/heritage/1
```

**响应示例**：

```json
{
  "id": 1,
  "name": "扬州剪纸",
  "level": "国家级",
  "category": "传统美术",
  "region": "江苏扬州",
  "batch": 2006,
  "intro": "……",
  "history": "扬州剪纸源于唐宋，兴盛于明清……",
  "craft": "选纸→起稿→剪刻→点染……",
  "cover_image": "/static/images/paper-cut.jpg",
  "audio_mandarin": "/static/audio/jianzhi-mandarin.mp3",
  "audio_dialect": "/static/audio/jianzhi-dialect.mp3",
  "qrcode": "/static/images/qrcode-1.png",
  "latitude": 32.394,
  "longitude": 119.412,
  "tags": ["第一批国家级", "传统美术", "示范性流派"],
  "inheritor_list": [
    { "id": 101, "name": "张秀芳", "title": "国家级代表性传承人", "photo": "/static/images/person-1.jpg" }
  ],
  "create_time": "2026-01-01T09:00:00"
}
```

**备注**：`inheritor_list` 返回该项目关联传承人摘要；作品与民俗关联可由知识图谱接口（第 3 节）获取。

---

### 2.4 获取传承人详情

```http
GET /api/v1/heritage/inheritor/{id}
```

**请求参数（Path）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | 是 | 传承人 ID |

**请求示例**：

```bash
curl http://localhost:8000/api/v1/heritage/inheritor/101
```

**响应示例**：

```json
{
  "id": 101,
  "name": "张秀芳",
  "gender": "女",
  "project_id": 1,
  "project_name": "扬州剪纸",
  "title": "国家级代表性传承人",
  "biography": "扬州剪纸代表性传承人，以点色剪纸见长……",
  "photo": "/static/images/person-1.jpg",
  "create_time": "2026-01-01T09:00:00"
}
```

**备注**：`project_name` 由关联项目表拼接返回，便于前端展示。

---

### 2.5 智能关联推荐

```http
GET /api/v1/heritage/{id}/recommendations
```

**请求参数（Path）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | 是 | 非遗项目 ID |

**请求示例**：

```bash
curl http://localhost:8000/api/v1/heritage/1/recommendations
```

**响应示例**：

```json
{
  "similar": [
    { "id": 8, "name": "扬州刺绣", "cover_image": "/static/images/embroidery.jpg" }
  ],
  "sameCategory": [
    { "id": 2, "name": "扬州玉雕", "cover_image": "/static/images/jade-carving.jpg" }
  ],
  "sameRegion": [
    { "id": 3, "name": "扬州漆器髹饰技艺", "cover_image": "/static/images/lacquerware.jpg" }
  ]
}
```

**备注**：推荐逻辑：`similar` 基于材料/工艺相似度（图谱 `USES_MATERIAL` 路径），`sameCategory` 同类别，`sameRegion` 同地区；每组最多 4 条。

---

## 3. 知识图谱接口（1 个）

### 3.1 获取知识图谱数据

```http
GET /api/v1/knowledge-graph
```

**请求参数（Query）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| category | string | 否 | 按类别筛选，返回该类别相关子图 |
| region | string | 否 | 按地区筛选 |
| depth | int | 否 | 关联展开深度，默认 2（1=仅项目节点，2=一度关联） |

**请求示例**：

```bash
curl "http://localhost:8000/api/v1/knowledge-graph?category=传统美术&depth=2"
```

**响应示例**：

```json
{
  "nodes": [
    { "id": "h1", "name": "扬州剪纸", "type": "heritage", "refId": 1 },
    { "id": "c2", "name": "传统美术", "type": "category" },
    { "id": "i101", "name": "张秀芳", "type": "inheritor", "refId": 101 },
    { "id": "d1", "name": "唐宋", "type": "dynasty" },
    { "id": "m1", "name": "宣纸彩纸", "type": "material" },
    { "id": "f2", "name": "春节窗花", "type": "folk_custom" }
  ],
  "edges": [
    { "source": "h1", "target": "c2", "label": "BELONGS_TO_CATEGORY" },
    { "source": "i101", "target": "h1", "label": "INHERITS" },
    { "source": "h1", "target": "d1", "label": "PREVAILED_IN" },
    { "source": "h1", "target": "m1", "label": "USES_MATERIAL" },
    { "source": "h1", "target": "f2", "label": "ASSOCIATED_WITH" }
  ]
}
```

**备注**：

- 节点 `id` 规则：项目 `h{项目id}`、传承人 `i{传承人id}`、类别 `c{序号}`、朝代 `d{序号}`、材料 `m{序号}`、民俗 `f{序号}`；`refId` 为对应 MySQL 主键，用于点击跳转；
- 关系类型：`INHERITS`（传承人→项目）、`BELONGS_TO_CATEGORY`（项目→类别）、`PREVAILED_IN`（项目→朝代）、`USES_MATERIAL`（项目→材料）、`ASSOCIATED_WITH`（项目→民俗）；
- **降级策略**：Neo4j 不可用时后端自动降级为内置关系数据返回，保证图谱页可用。

---

## 4. AI 创作接口（6 个）

> 通用说明：以下接口均由后端调用 AI 模型服务生成，返回结果均带 `ai_created: true` 标识，前端须展示"AI 创作"角标。

### 4.1 生成非遗纹样

```http
POST /api/v1/ai/generate-pattern
```

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| prompt | string | 是 | 纹样描述提示词，如 `梅花主题` |
| style | string | 是 | 非遗风格，如 `扬州剪纸` / `蓝印花布` / `漆器纹样` |
| size | string | 否 | 图片尺寸，默认 `1024x1024` |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/ai/generate-pattern \
  -H "Content-Type: application/json" \
  -d '{"prompt": "梅花主题", "style": "扬州剪纸", "size": "1024x1024"}'
```

**响应示例**：

```json
{
  "task_id": "task_20260101120000",
  "image_url": "/static/images/gen-pattern-1.jpg",
  "style": "扬州剪纸",
  "prompt": "梅花主题",
  "ai_created": true
}
```

---

### 4.2 生成科普剧本

```http
POST /api/v1/ai/generate-script
```

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| theme | string | 是 | 剧本主题，如 `漆器制作流程` |
| duration | int | 否 | 目标时长（秒），默认 60 |
| dialect | bool | 否 | 是否使用方言演绎，默认 false |
| roleCount | int | 否 | 角色数量，默认 3 |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/ai/generate-script \
  -H "Content-Type: application/json" \
  -d '{"theme": "漆器制作流程", "duration": 60, "dialect": true, "roleCount": 3}'
```

**响应示例**：

```json
{
  "theme": "漆器制作流程",
  "duration": 60,
  "dialect": true,
  "roles": ["旁白", "老师傅", "徒弟"],
  "scenes": [
    {
      "scene": 1,
      "title": "开场·溯源",
      "content": "【旁白】扬州非遗，千年文脉。今天我们要讲的是「漆器制作流程」的故事。（本幕使用扬州方言演绎）",
      "roles": ["旁白"]
    },
    {
      "scene": 2,
      "title": "传承·技艺",
      "content": "【老师傅】这门手艺讲究的是心到、眼到、手到……",
      "roles": ["老师傅", "徒弟"]
    }
  ],
  "ai_created": true
}
```

---

### 4.3 生成非遗风格画作（文生图 / 图生图）

```http
POST /api/v1/ai/generate-painting
```

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| mode | string | 否 | 生成模式：`text` 文生图 / `image` 图生图，默认 `text` |
| prompt | string | 是 | 画面描述提示词 |
| style | string | 否 | 画风，如 `漆画` / `剪纸风` / `水墨`，默认 `漆画` |
| image | string | 否 | 图生图模式的参考图 URL（mode=image 时必填） |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/ai/generate-painting \
  -H "Content-Type: application/json" \
  -d '{"mode": "text", "prompt": "瘦西湖春晓，剪纸风格", "style": "剪纸风"}'
```

**响应示例**：

```json
{
  "task_id": "task_20260101120500",
  "image_url": "/static/images/gen-painting-2.jpg",
  "style": "剪纸风",
  "prompt": "瘦西湖春晓，剪纸风格",
  "mode": "text",
  "ai_created": true
}
```

---

### 4.4 保存作品到"我的作品"

```http
POST /api/v1/ai/works
```

**请求头**：`Authorization: Bearer {token}`

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| work_type | string | 是 | 作品类型：`pattern` 纹样 / `script` 剧本 / `painting` 画作 |
| title | string | 否 | 作品标题 |
| content | string | 是 | 作品内容（图片 URL 或剧本文本） |
| style | string | 否 | 创作风格 |
| prompt | string | 否 | 创作提示词（AI 溯源留存） |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/ai/works \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"work_type": "pattern", "title": "梅花纹样", "content": "/static/images/gen-pattern-1.jpg", "style": "扬州剪纸", "prompt": "梅花主题"}'
```

**响应示例**：

```json
{
  "id": 1,
  "user_id": 1,
  "work_type": "pattern",
  "title": "梅花纹样",
  "content": "/static/images/gen-pattern-1.jpg",
  "style": "扬州剪纸",
  "prompt": "梅花主题",
  "create_time": "2026-01-01T12:10:00"
}
```

---

### 4.5 获取我的作品列表

```http
GET /api/v1/ai/works
```

**请求头**：`Authorization: Bearer {token}`

**请求参数（Query）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| work_type | string | 否 | 按类型筛选：`pattern` / `script` / `painting` |

**请求示例**：

```bash
curl http://localhost:8000/api/v1/ai/works \
  -H "Authorization: Bearer {token}"
```

**响应示例**：

```json
[
  {
    "id": 1,
    "work_type": "pattern",
    "title": "梅花纹样",
    "content": "/static/images/gen-pattern-1.jpg",
    "style": "扬州剪纸",
    "prompt": "梅花主题",
    "create_time": "2026-01-01T12:10:00"
  }
]
```

---

### 4.6 删除作品

```http
DELETE /api/v1/ai/works/{id}
```

**请求头**：`Authorization: Bearer {token}`

**请求参数（Path）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | 是 | 作品 ID |

**请求示例**：

```bash
curl -X DELETE http://localhost:8000/api/v1/ai/works/1 \
  -H "Authorization: Bearer {token}"
```

**响应示例**：

```json
{ "id": 1 }
```

---

## 5. 多模态导览接口（4 个）

### 5.1 获取讲解音频

```http
GET /api/v1/audio/guide/{projectId}
```

**请求参数（Path）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| projectId | int | 是 | 非遗项目 ID |

**请求参数（Query）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| lang | string | 否 | 语言：`mandarin` 普通话 / `dialect` 方言，默认 `mandarin` |

**请求示例**：

```bash
curl "http://localhost:8000/api/v1/audio/guide/1?lang=dialect"
```

**响应示例**：

```json
{
  "url": "/static/audio/jianzhi-dialect.mp3",
  "text": "扬州剪纸是南方剪纸艺术的代表流派之一……",
  "duration": 70
}
```

---

### 5.2 智能问答（RAG + 大模型）

```http
POST /api/v1/audio/qa
```

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| question | string | 是 | 用户问题，如 `扬州剪纸有多少年历史？` |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/audio/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "扬州剪纸有多少年历史？"}'
```

**响应示例**：

```json
{
  "answer": "扬州剪纸源于唐宋、兴盛于明清，距今已有一千多年历史……",
  "audio": "/static/audio/qa-jianzhi.mp3",
  "question": "扬州剪纸有多少年历史？"
}
```

**备注**：后端流程为 ChromaDB 向量检索相关知识片段 → 豆包/通义千问组织答案 → TTS 合成语音；答案为 AI 生成内容，前端须标注"AI 创作"。

---

### 5.3 扫码内容解析

```http
POST /api/v1/guide/scan-resolve
```

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| code | string | 是 | 二维码原始内容，格式见[附录](#9-附录扫码二维码内容格式约定) |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/guide/scan-resolve \
  -H "Content-Type: application/json" \
  -d '{"code": "heritouch://project?id=1"}'
```

**响应示例**：

```json
{
  "projectId": 1,
  "name": "扬州剪纸"
}
```

**备注**：解析失败（格式错误或项目不存在）返回 400，message 为 `无效的非遗二维码` 或 `未找到对应非遗项目`。

---

### 5.4 下载离线数据包

```http
POST /api/v1/guide/offline-pack
```

**请求头**：`Authorization: Bearer {token}`（可选）

**请求参数**：无

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/guide/offline-pack
```

**响应示例**：

```json
{
  "version": "1.0.0",
  "download_time": "2026-01-01T12:00:00",
  "size": "12.6MB",
  "projects": [
    { "id": 1, "name": "扬州剪纸", "intro": "……", "audio": "/static/audio/jianzhi-mandarin.mp3" }
  ]
}
```

**备注**：返回核心讲解音频与基础数据清单，供前端缓存离线使用。

---

## 6. 科普闯关接口（6 个）

### 6.1 获取关卡列表（含解锁状态）

```http
GET /api/v1/game/levels
```

**请求头**：`Authorization: Bearer {token}`（可选；携带时返回个人解锁状态与最好成绩）

**请求参数**：无

**请求示例**：

```bash
curl http://localhost:8000/api/v1/game/levels
```

**响应示例**：

```json
[
  {
    "id": 1,
    "name": "入门学徒",
    "subtitle": "初识扬州非遗",
    "rank": "学徒",
    "need_score": 0,
    "theme": "基础认知",
    "question_count": 10,
    "icon": "🌱",
    "unlocked": true,
    "bestScore": 0,
    "passed": false
  },
  {
    "id": 2,
    "name": "匠人弟子",
    "subtitle": "技艺门类辨一辨",
    "rank": "弟子",
    "need_score": 100,
    "theme": "传统技艺",
    "question_count": 10,
    "icon": "🔨",
    "unlocked": false,
    "bestScore": 0,
    "passed": false
  }
]
```

**备注**：`unlocked` 依据用户累计积分与 `need_score` 比较得出；`passed` 表示该关最好成绩是否达到 60 分及格线。

---

### 6.2 获取关卡题目

```http
GET /api/v1/game/questions/{levelId}
```

**请求参数（Path）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| levelId | int | 是 | 关卡 ID |

**请求参数（Query）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| count | int | 否 | 抽取题量，默认 10 |

**请求示例**：

```bash
curl http://localhost:8000/api/v1/game/questions/1?count=10
```

**响应示例**：

```json
[
  {
    "id": 1,
    "level_id": 1,
    "question_type": "single",
    "question_text": "扬州剪纸属于下列哪一类非遗？",
    "option_a": "传统美术",
    "option_b": "传统戏剧",
    "option_c": "传统医药",
    "option_d": "民俗",
    "image": null,
    "difficulty": 1
  },
  {
    "id": 2,
    "level_id": 1,
    "question_type": "judge",
    "question_text": "扬州玉雕以大型山子雕见长，被誉为中国玉雕“南派”代表。",
    "option_a": "正确",
    "option_b": "错误",
    "option_c": null,
    "option_d": null,
    "image": null,
    "difficulty": 1
  }
]
```

**备注**：**题目接口不返回 `answer` 与 `analysis` 字段**，防止答案泄露；答案校验统一走 6.3 提交接口。`question_type`：`single` 单选 / `judge` 判断 / `image` 识图。

---

### 6.3 提交单题答案

```http
POST /api/v1/game/submit
```

**请求头**：`Authorization: Bearer {token}`（可选；携带时自动记录错题）

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| questionId | int | 是 | 题目 ID |
| answer | string | 是 | 用户作答（`A` / `B` / `C` / `D`） |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/game/submit \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"questionId": 1, "answer": "A"}'
```

**响应示例**：

```json
{
  "correct": true,
  "answer": "A",
  "analysis": "扬州剪纸是国家级传统美术类非遗，以细秀雅活著称。",
  "score": 10,
  "difficulty": 1
}
```

**备注**：得分规则为难度 1 得 10 分、难度 2 得 15 分、难度 3 得 20 分；答错时若携带 Token，自动写入错题本（`wrong_question` 表，`wrong_count` 累计）。

---

### 6.4 获取排行榜

```http
GET /api/v1/game/rank
```

**请求参数（Query）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| limit | int | 否 | 榜单人数，默认 50 |

**请求示例**：

```bash
curl http://localhost:8000/api/v1/game/rank
```

**响应示例**：

```json
[
  { "rank": 1, "nickname": "非遗小达人", "avatar": "/static/images/avatar-1.jpg", "score": 980 },
  { "rank": 2, "nickname": "扬州小秀才", "avatar": "/static/images/avatar-2.jpg", "score": 860 },
  { "rank": 0, "nickname": "我", "avatar": "", "score": 120, "me": true }
]
```

**备注**：按累计积分降序；当前用户记录以 `me: true` 标识混排返回。

---

### 6.5 获取错题本

```http
GET /api/v1/game/wrong
```

**请求头**：`Authorization: Bearer {token}`

**请求参数**：无

**请求示例**：

```bash
curl http://localhost:8000/api/v1/game/wrong \
  -H "Authorization: Bearer {token}"
```

**响应示例**：

```json
[
  {
    "id": 1,
    "question_id": 13,
    "question_text": "富春三丁包的“三丁”不包括下列哪一项？",
    "question_type": "single",
    "option_a": "笋丁",
    "option_b": "鸡丁",
    "option_c": "肉丁",
    "option_d": "虾丁",
    "answer": "D",
    "analysis": "三丁指鸡丁、肉丁、笋丁……",
    "wrong_count": 2,
    "last_wrong_time": "2026-01-01T12:30:00"
  }
]
```

---

### 6.6 移除错题（已掌握）

```http
DELETE /api/v1/game/wrong/{id}
```

**请求头**：`Authorization: Bearer {token}`

**请求参数（Path）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | 是 | 错题记录 ID（错题本列表项的 `id`，非题目 ID） |

**请求示例**：

```bash
curl -X DELETE http://localhost:8000/api/v1/game/wrong/1 \
  -H "Authorization: Bearer {token}"
```

**响应示例**：

```json
{ "id": 1 }
```

---

## 7. 用户中心接口（6 个）

### 7.1 登录 / 注册

```http
POST /api/v1/user/login
```

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| openid | string | 是 | 微信 openid 或设备唯一标识（演示环境可用 `demo_admin`） |
| nickname | string | 否 | 用户昵称 |
| avatar | string | 否 | 头像 URL |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{"openid": "demo_admin", "nickname": "非遗管理员", "avatar": "/static/images/avatar-default.jpg"}'
```

**响应示例**：

```json
{
  "id": 1,
  "openid": "demo_admin",
  "nickname": "非遗管理员",
  "avatar": "/static/images/avatar-default.jpg",
  "score": 0,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "create_time": "2026-01-01T09:00:00"
}
```

**备注**：openid 不存在时自动注册新用户；`token` 为后续接口的认证凭证。

---

### 7.2 获取用户信息

```http
GET /api/v1/user/info
```

**请求头**：`Authorization: Bearer {token}`

**请求参数**：无

**请求示例**：

```bash
curl http://localhost:8000/api/v1/user/info \
  -H "Authorization: Bearer {token}"
```

**响应示例**：

```json
{
  "id": 1,
  "openid": "demo_admin",
  "nickname": "非遗管理员",
  "avatar": "/static/images/avatar-default.jpg",
  "score": 120,
  "favorite_count": 5,
  "work_count": 3,
  "wrong_count": 2,
  "create_time": "2026-01-01T09:00:00"
}
```

---

### 7.3 更新个人资料

```http
PUT /api/v1/user/profile
```

**请求头**：`Authorization: Bearer {token}`

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| nickname | string | 否 | 新昵称 |
| avatar | string | 否 | 新头像 URL |

**请求示例**：

```bash
curl -X PUT http://localhost:8000/api/v1/user/profile \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"nickname": "扬州非遗爱好者"}'
```

**响应示例**：

```json
{
  "id": 1,
  "nickname": "扬州非遗爱好者",
  "avatar": "/static/images/avatar-default.jpg",
  "score": 120
}
```

---

### 7.4 添加收藏

```http
POST /api/v1/user/favorite
```

**请求头**：`Authorization: Bearer {token}`

**请求体（JSON）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| fav_type | string | 是 | 收藏类型：`project` 项目 / `inheritor` 传承人 / `work` 作品 |
| fav_id | int | 是 | 收藏目标 ID |
| fav_name | string | 否 | 收藏目标名称（冗余存储便于展示） |

**请求示例**：

```bash
curl -X POST http://localhost:8000/api/v1/user/favorite \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"fav_type": "project", "fav_id": 1, "fav_name": "扬州剪纸"}'
```

**响应示例**：

```json
{
  "id": 1,
  "fav_type": "project",
  "fav_id": 1,
  "fav_name": "扬州剪纸",
  "create_time": "2026-01-01T13:00:00"
}
```

**备注**：重复收藏同一目标返回 400（`该内容已在收藏夹中`）；数据库层 `UNIQUE(user_id, fav_type, fav_id)` 约束保证唯一性。

---

### 7.5 取消收藏

```http
DELETE /api/v1/user/favorite/{id}
```

**请求头**：`Authorization: Bearer {token}`

**请求参数（Path）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | 是 | 收藏记录 ID（收藏列表项的 `id`） |

**请求示例**：

```bash
curl -X DELETE http://localhost:8000/api/v1/user/favorite/1 \
  -H "Authorization: Bearer {token}"
```

**响应示例**：

```json
{ "id": 1 }
```

---

### 7.6 获取收藏列表

```http
GET /api/v1/user/favorites
```

**请求头**：`Authorization: Bearer {token}`

**请求参数（Query）**：

| 名称 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| fav_type | string | 否 | 按类型筛选：`project` / `inheritor` / `work` |

**请求示例**：

```bash
curl http://localhost:8000/api/v1/user/favorites \
  -H "Authorization: Bearer {token}"
```

**响应示例**：

```json
[
  {
    "id": 1,
    "fav_type": "project",
    "fav_id": 1,
    "fav_name": "扬州剪纸",
    "create_time": "2026-01-01T13:00:00"
  }
]
```

---

## 8. 错误码表

| HTTP 状态码 | 业务 code | 典型 message | 说明与处理建议 |
| --- | --- | --- | --- |
| 400 | 400 | `参数错误：prompt 不能为空` | 请求参数缺失或格式不正确，检查请求体与文档参数表 |
| 400 | 400 | `该内容已在收藏夹中` | 重复收藏，前端可直接切换为"已收藏"态 |
| 400 | 400 | `无效的非遗二维码` | 扫码内容不符合约定格式（见附录） |
| 400 | 400 | `未找到对应非遗项目` | 二维码中的项目 ID 不存在 |
| 401 | 401 | `未登录或登录已过期` | Token 缺失/失效，前端跳转登录页重新登录 |
| 401 | 401 | `openid 不能为空` | 登录参数缺失 |
| 404 | 404 | `项目不存在` | 请求的资源 ID 不存在，检查路径参数 |
| 404 | 404 | `传承人不存在` | 同上 |
| 500 | 500 | `服务器内部错误` | 后端异常，查看服务日志；AI 接口超时会有独立提示 `AI 服务繁忙，请稍后重试` |

**错误响应示例**：

```json
{
  "code": 401,
  "message": "未登录或登录已过期",
  "data": null
}
```

---

## 9. 附录：扫码二维码内容格式约定

非遗项目二维码采用自定义 Scheme 内容，兼容 H5 短链接两种形态：

| 形态 | 内容示例 | 适用场景 |
| --- | --- | --- |
| 自定义 Scheme | `heritouch://project?id=1` | APP 内扫码（`uni.scanCode`） |
| H5 短链接 | `https://heritouch.example.com/p?id=1` | 微信等外部扫码，跳转 H5 落地页 |

**参数约定**：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | int | 是 | 非遗项目 ID（对应 `heritage_project.id`） |

**解析规则**：后端 `POST /guide/scan-resolve` 通过正则 `[?&]id=(\d+)` 提取项目 ID，校验存在性后返回 `projectId` 与 `name`；前端据此跳转项目详情页并自动播放讲解音频。

---

© Heritouch 团队 · API 文档 v1.0 · 与后端 FastAPI 路由及前端 `mobile-app/api/` 契约保持一致
