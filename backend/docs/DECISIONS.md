# 设计决策（DECISIONS）

> 重要设计决策记录在此，落地后划掉「待决策」项。

## 已决策

### D1 存储从 PostgreSQL 切换为 MySQL
- **决策**：数据库用本机 MySQL（brew，`root/root`，库 `info_harbor`），不走 docker。
- **原因**：作者熟悉 MySQL（CMS 同栈）；本机已有 MySQL 运行。
- **影响**：`asyncpg`/`pgvector` → `aiomysql`/`pymysql`；`JSONB` → `JSON`；docker-compose 移除 postgres 服务。
- **向量检索**：原 pgvector 预留能力推迟，后续语义去重可用独立向量库（MySQL 8.0.3+ 也支持向量近似搜索）。

### D2 数据源配置权威 = YAML seed + DB 运行时
- `config/sources/*.yaml` 作引导，`lifespan` 幂等 upsert 进 DB；CRUD 走 DB。

### D3 原始文章存 articles 单表 + status='raw'
- 复用 `Article` 契约，后续清洗/评分原地 UPDATE，不二次落库。

### D4 去重粒度 = url 唯一索引
- MVP 用 `articles.url` 唯一索引 + `ON CONFLICT DO NOTHING`；RedisBloom 语义去重推迟。

### D5 端口规划
- Redis 当前本机 **6379**（brew）；未来 docker 版映射到 **6380**，以免与本机实例冲突。
- 曾用 pg@5433，已随 D1 切到 MySQL，不再相关。

### D6 事件总线 in-process
- MVP 单进程 EventBus；多 worker 后切 Redis Streams（只换实现）。

### D7 认证：JWT（HS256）+ 密码 bcrypt + 图形验证码存 Redis
- **决策**：登录用 PyJWT 签发 Bearer token（`HARBOR_JWT_EXPIRE_MINUTES`，默认 24h）；密码哈希用 pwdlib[bcrypt]（不用 passlib，其已停维护且与 bcrypt>=4.1 不兼容）；图形验证码用 Pillow 手绘 PNG，验证码存 Redis（`captcha:<uuid>`，TTL 300s，**一次性消费**——Lua 原子 GET+DEL）。
- **影响**：新增 `auth` extras 依赖组（pyjwt / pwdlib[bcrypt] / redis / pillow / email-validator）；`.env` 需配置 `HARBOR_JWT_SECRET`。
- **RBAC 预留**：`users.role` 字段 + JWT payload 带 `role` claim；后端 `require_roles()` 依赖工厂、前端 `meta.role` 均已预留，权限管理轮次接线。

### D8 登录防爆破：5 次失败 / 5 分钟锁定
- **决策**：同一账号（用户名或邮箱）在 Redis `login_fail:<account>` 计数，窗口 5 分钟；达到 5 次后返回 429，登录成功或窗口过期后重置。
- **原因**：代价低（复用 Redis）、能挡住口令爆破；不引入验证码滑动等重交互。
- **影响**：登录接口可能返回 429；验证码消费失败返回 400（不计数，防绕过）。

## 待决策

- （爬虫阶段补充：RSS 解析用 feedparser / 抓取超时与重试策略 / 任务失败告警）
