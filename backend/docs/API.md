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
- [规划中接口](#规划中接口)

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
| country | string | 否 | - | 国家/地区筛选 |
| source_id | string | 否 | - | 数据源 ID 筛选 |
| min_score | float | 否 | - | 最低评分筛选 |
| sort | string | 否 | published_at | 排序字段 |

**Response (200):**

```json
{
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20
}
```

> 当前为骨架实现，返回空集。

---

### 文章详情

- **Method:** `GET`
- **Path:** `/api/v1/articles/{article_id}`
- **Auth:** 无

**Path Params:**

| 参数 | 类型 | 说明 |
|------|------|------|
| article_id | string | 文章 ID |

**Response (200):**

```json
{
    "id": "article_id_xxx",
    "title": "文章标题",
    "content": "文章内容...",
    "source_id": "source_id_xxx",
    "published_at": "2026-08-31T10:00:00Z",
    "score": 8.5,
    "status": "published"
}
```

> 当前为骨架实现，返回 TODO 占位。

---

## 规划中接口

> 以下接口计划在爬虫系统 M1 阶段实现。

### 数据源管理

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/v1/sources` | 数据源列表 | 📋 规划中 |
| POST | `/api/v1/sources` | 创建数据源 | 📋 规划中 |
| GET | `/api/v1/sources/{id}` | 数据源详情 | 📋 规划中 |
| PATCH | `/api/v1/sources/{id}` | 更新数据源 | 📋 规划中 |
| DELETE | `/api/v1/sources/{id}` | 删除数据源 | 📋 规划中 |
| POST | `/api/v1/sources/{id}/crawl` | 触发抓取 | 📋 规划中 |

### 任务管理

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/v1/tasks` | 任务列表 | 📋 规划中 |
| GET | `/api/v1/tasks/{id}` | 任务详情 | 📋 规划中 |
| POST | `/api/v1/tasks/{id}/retry` | 重试任务 | 📋 规划中 |
| POST | `/api/v1/tasks/{id}/cancel` | 取消任务 | 📋 规划中 |

---

## RBAC 权限说明

> 当前已预留 RBAC 支持，尚未完全启用。

| 角色 | 说明 |
|------|------|
| user | 普通用户（默认） |
| admin | 管理员 |

**已实现的权限控制：**
- `deps.py` 中的 `require_roles(*roles)` 依赖工厂已就绪
- JWT payload 携带 `role` claim
- 前端路由 `meta.role` 已预留

**使用示例：**
```python
@router.get("/admin/dashboard")
async def admin_dashboard(user = Depends(require_roles("admin"))):
    ...
```

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
