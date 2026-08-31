# 接口定义（API）

> 当前已有登录注册认证接口与文章骨架接口；爬虫系统落地后补充完整字段与示例。

## 已实现端点

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/health` | 健康检查 | ✅ 可用 |
| GET | `/api/v1/articles` | 文章列表（分页/过滤/排序） | ⚠️ 返回空集 |
| GET | `/api/v1/articles/{id}` | 文章详情 | ⚠️ TODO 占位 |

## 认证（登录 / 注册 / 验证码）

> 登录与注册均需图形验证码（一次性使用，Redis 存储，TTL 5 分钟）。token 有效期 `HARBOR_JWT_EXPIRE_MINUTES`（默认 24h），请求时放入 `Authorization: Bearer <token>`。

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/api/v1/auth/captcha` | 获取图形验证码 | 无需登录。返回 `{captcha_id, image_base64}`，`image_base64` 为 PNG 的 base64（前端以 `data:image/png;base64,` 渲染） |
| POST | `/api/v1/auth/register` | 注册账号 | 201 返回用户信息（**不自动登录**）。body：`{username, email, password, captcha_id, captcha_code}` |
| POST | `/api/v1/auth/login` | 登录获取 token | 200 返回 `{access_token, token_type}`。body：`{account, password, captcha_id, captcha_code}`，account 为用户名或邮箱 |
| GET | `/api/v1/auth/me` | 当前登录用户 | 需 Bearer token，返回 `{id, username, email, role, status}` |

### 认证错误码

| 状态码 | 场景 |
|--------|------|
| 400 | 验证码缺失 / 错误 / 已过期 / 已使用 |
| 401 | 账号或密码错误 / 账号停用 / token 缺失或无效 |
| 409 | 用户名或邮箱已被注册 |
| 429 | 同一账号 5 分钟内登录失败 ≥5 次（防爆破锁定） |

## 规划中（爬虫系统 M1）

- `GET/POST /api/v1/sources` —— 数据源列表 / 创建
- `GET/PATCH/DELETE /api/v1/sources/{id}` —— 源详情 / 更新 / 删除
- `POST /api/v1/sources/{id}/crawl` —— 触发抓取（→ 202 任务）
- `GET /api/v1/tasks` —— 任务列表
- `GET /api/v1/tasks/{id}` —— 任务详情
- `POST /api/v1/tasks/{id}/retry` / `cancel` —— 重试 / 取消

## RBAC（预留）

- `users.role` 字段（默认 `user`）已落库；JWT payload 携带 `role` claim
- 后端 `require_roles("admin")` 依赖工厂已就绪，待权限管理轮次接线
- 前端路由 `meta.role` 已预留（如 `/admin` 为 `admin`），当前仅做「未登录跳转」