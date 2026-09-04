# API 接口文档

> 当前版本：v0.1.0
> 基础路径：`http://localhost:8000`

## 统一响应格式

所有接口返回 JSON 格式：

```json
{
    "code": 200,
    "message": "success",
    "data": { ... }
}
```

> 注：当前 FastAPI 默认响应格式，后续可统一为上述结构。

---

## 目录

- [系统接口](#系统接口)
- [认证接口](#认证接口)
- [文章接口](#文章接口)
- [数据源接口（admin）](#数据源接口admin)
- [任务接口（admin）](#任务接口admin)

---

## 系统接口

### 健康检查

- **Method:** `GET`
- **Path:** `/health`
- **Auth:** 无

**Response (200):**

```json
{
    "status": "ok",
    "service": "info-harbor",
    "version": "0.1.0"
}
```

---

## 认证接口

> 所有认证接口均需图形验证码。验证码通过 `GET /captcha` 获取，一次使用，有效期 5 分钟。

### 获取验证码

- **Method:** `GET`
- **Path:** `/api/v1/auth/captcha`
- **Auth:** 无

**Response (200):**

```json
{
    "captcha_id": "a1b2c3d4e5f6...",
    "image_base64": "iVBORw0KGgo..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| captcha_id | string | 验证码 ID，用于后续请求 |
| image_base64 | string | 验证码图片的 base64 编码（PNG 格式） |

> 前端渲染：`<img src="data:image/png;base64,{image_base64}">`

---

### 注册账号

- **Method:** `POST`
- **Path:** `/api/v1/auth/register`
- **Auth:** 无

**Request Body:**

```json
{
    "username": "string (2-64 字符, 必填)",
    "email": "string (邮箱格式, 必填)",
    "password": "string (6-128 字符, 必填)",
    "captcha_id": "string (必填)",
    "captcha_code": "string (必填)"
}
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| username | string | 2-64 字符 | 用户名，唯一 |
| email | string | 邮箱格式 | 邮箱，唯一 |
| password | string | 6-128 字符 | 密码（明文传输，后端哈希存储） |
| captcha_id | string | - | 验证码 ID（从 `/captcha` 获取） |
| captcha_code | string | - | 用户输入的验证码 |

**Response (201):**

```json
{
    "id": "user_id_xxx",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "role": "user",
    "status": "active",
    "last_login_at": null
}
```

**错误：**

| 状态码 | 场景 |
|--------|------|
| 400 | 验证码缺失 / 错误 / 已过期 / 已使用 |
| 409 | 用户名或邮箱已被注册 |
| 422 | 参数校验失败（格式/长度不合法） |

> 注册成功后不会自动登录，前端需切换到登录模式。

---

### 用户登录

- **Method:** `POST`
- **Path:** `/api/v1/auth/login`
- **Auth:** 无

**Request Body:**

```json
{
    "account": "string (用户名或邮箱, 必填)",
    "password": "string (必填)",
    "captcha_id": "string (必填)",
    "captcha_code": "string (必填)"
}
```

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| account | string | - | 用户名或邮箱（含 `@` 视为邮箱） |
| password | string | - | 密码 |
| captcha_id | string | - | 验证码 ID |
| captcha_code | string | - | 验证码 |

**Response (200):**

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| access_token | string | JWT Token，用于后续请求 |
| token_type | string | 固定值 `bearer` |

**错误：**

| 状态码 | 场景 |
|--------|------|
| 400 | 验证码缺失 / 错误 / 已过期 / 已使用 |
| 401 | 账号不存在 / 密码错误 / 账号已停用 |
| 429 | 同一账号 5 分钟内登录失败 ≥5 次（防爆破锁定） |

> Token 有效期：24 小时（可通过 `HARBOR_JWT_EXPIRE_MINUTES` 配置）

---

### 获取当前用户

- **Method:** `GET`
- **Path:** `/api/v1/auth/me`
- **Auth:** Bearer Token

**Request Headers:**

```
Authorization: Bearer {access_token}
```

**Response (200):**

```json
{
    "id": "user_id_xxx",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "role": "user",
    "status": "active",
    "last_login_at": "2026-08-31T20:50:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 用户 ID |
| username | string | 用户名 |
| email | string | 邮箱 |
| role | string | 角色（`user` / `admin`） |
| status | string | 状态（`active` / `disabled`） |
| last_login_at | string \| null | 最后登录时间（ISO 8601） |

**错误：**

| 状态码 | 场景 |
|--------|------|
| 401 | Token 缺失 / 无效 / 已过期 / 用户不存在 |

> 每次请求都会从数据库获取最新用户信息，权限变更即时生效。

---

## 文章接口

### 文章列表

- **Method:** `GET`
- **Path:** `/api/v1/articles`
- **Auth:** 无

**Query Params:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码 |
| page_size | int | 否 | 20 | 每页数量 |
| country | string | 否 | - | 国家/地区筛选（如 `CN`） |
| source_id | string | 否 | - | 数据源 ID 筛选（如 `infoq`） |
| sort | string | 否 | published_at | 排序字段（`published_at` / `created_at`），NULL 排最后 |

**Response (200):**

```json
{
    "items": [
        {
            "id": "hex32",
            "source_id": "infoq",
            "title": "文章标题",
            "url": "https://www.infoq.cn/article/xxx",
            "content": "正文（trafilatura 提取）",
            "summary": "摘要",
            "author": "作者昵称",
            "published_at": "2026-09-02T04:00:01Z",
            "detected_lang": "zh",
            "country": "CN",
            "source_type": "api",
            "tags": ["AI & 大模型"],
            "status": "raw",
            "ext_json": {"channel_id": 31, "channel": "AI & 大模型", "infoq_aid": "390682"}
        }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
}
```

> M1 起为真实数据（InfoQ 适配器写入）；`min_score` 筛选待评分管道（V2）后开放。

---

### 文章详情

- **Method:** `GET`
- **Path:** `/api/v1/articles/{article_id}`
- **Auth:** 无

**Response (200):** Article 契约完整字段（含 entities / ext_json）。**404** 文章不存在。

---

## 数据源接口（admin）

> 全部要求 `Authorization: Bearer <token>` 且 `role=admin`，否则 401/403。

### 来源产出概况（公开）

- **Method:** `GET` · **Path:** `/api/v1/sources/overview`
- **Auth:** 无（来源页/国家页公开数据）
- **Response (200):** `[{id, name, country, type, adapter_key, enabled, article_count, last_published_at}]`（按文章数倒序）

### 数据源列表

- **Method:** `GET` · **Path:** `/api/v1/sources`
- **Response (200):** `Source[]`（id / name / country / type / adapter_key / weight / enabled / health / config）

### 数据源详情

- **Method:** `GET` · **Path:** `/api/v1/sources/{source_id}` · **404** 不存在

### 更新数据源（启停 / 权重）

- **Method:** `PATCH` · **Path:** `/api/v1/sources/{source_id}`
- **Body:** `{"enabled": true, "weight": 1.5}`（部分更新，只传要改的字段）
- **Response (200):** 更新后的 Source

### 触发抓取（手动）

- **Method:** `POST` · **Path:** `/api/v1/sources/{source_id}/crawl`
- **Response (202):** `TaskOut`（status=`queued`，含 arq_job_id）
- 执行在 worker 进程；状态流转见任务接口

---

## 任务接口（admin）

### 任务列表

- **Method:** `GET` · **Path:** `/api/v1/tasks`
- **Query:** `source_id` / `task_status`（queued|running|succeeded|failed）/ `page` / `page_size`
- **Response (200):** `{"items": [TaskOut], "total": n, "page": 1, "page_size": 20}`，created_at 倒序

### 任务详情

- **Method:** `GET` · **Path:** `/api/v1/tasks/{task_id}` · **404** 不存在

**TaskOut 字段：** id / source_id / status / task_type(manual|scheduled) / arq_job_id / result_count / error / created_at / started_at / finished_at

> 任务状态以 DB 为权威：queued → running → succeeded | failed；单条失败不中断整源（错误摘要写入 error）。retry / cancel 留下轮。

---

## RBAC 权限说明

| 角色 | 说明 | 本轮接线 |
|------|------|----------|
| user | 普通用户（默认） | 文章接口公开可读 |
| admin | 管理员 | sources / tasks 全部接口 |

**运维工具：** `.venv/bin/python -m app.scripts.promote_admin <username> [--password <pw>]` —— 创建/提升 admin，可打印调试 token（`--no-token` 关闭）。

---

## 附录

### 错误码汇总

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | 成功 | 正常响应 |
| 201 | 已创建 | 资源创建成功 |
| 400 | 请求错误 | 验证码错误、业务逻辑错误 |
| 401 | 未授权 | Token 缺失/无效/过期、账号密码错误 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 未找到 | 资源不存在 |
| 409 | 冲突 | 资源已存在（用户名/邮箱重复） |
| 422 | 参数错误 | 请求体格式不合法 |
| 429 | 请求过多 | 防爆破限流 |

### 认证流程

```
1. GET /captcha → 获取 captcha_id + 图片
2. 用户填写表单
3. POST /register 或 /login → 附带 captcha_id + captcha_code
4. 登录成功后存储 access_token
5. GET /me + Authorization: Bearer {token} → 获取用户信息
```
