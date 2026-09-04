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
- 各开发机本机 Redis 统一 **6379**；未来 docker 版映射到 **6380**，以免与本机实例冲突。
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

### D9 环境文档去机器化：公共 docs 讲约定，机器差异进本地笔记
- **决策**：两台开发机（macOS / Windows）协作。公共文档（`DOCKER.md` 等）只写「项目需要什么服务、什么端口、什么库」；安装路径 / 启动命令等机器差异写进各机器 gitignored 的 `backend/docs/LOCAL_ENV_<机器名>.md`，模板 `LOCAL_ENV_TEMPLATE.md` 入库供复制。
- **原因**：此前 `DOCKER.md` 以 Windows 视角写成环境「唯一事实来源」，与 macOS 实际（brew）持续漂移——公共文档被某一台机器的环境事实污染。
- **影响**：环境相关公共文档禁止再写入具体机器路径；Windows 机的 Redis 启动说明由本人迁入其本地笔记（可从 git 历史找回）；依赖权威源为 `backend/pyproject.toml` extras（`requirements.txt` 已删）。

### D10 InfoQ JSON 适配器：源粒度 1 源 12 频道；正文从文章页提取
- **决策**：首批源 = InfoQ 中文站（用户数据源规划）。`sources` 表建 **1 行**（id=infoq，country=CN），12 个频道放 `config.channels`，任务按源执行、插件内逐频道游标翻页。正文获取：`getDetail.content` **已不再直出**、`content_url` 签名链接 403（2026-09-03 实测）——改为抓文章页 HTML（`/article/<uuid>`）后 **trafilatura 提取正文**，失败回退 `ai_summary` / `article_summary`。
- **接口事实**：列表 `POST /public/v1/article/getList`（body `{"type":1,"ptype":0,"size":20,"id":<频道ID>,"score":""}`，score 毫秒游标翻页）；详情 `POST /public/v1/article/getDetail`（author[].nickname / publish_time / ai_summary）。请求带 UA + Referer 头。
- **影响**：`crawler` extras（trafilatura/tenacity）自本轮起真实使用；文章 `tags` 存频道名，`ext_json` 存 channel_id/aid。

### D11 定时与重试：arq 原生 cron；httpx 10s + tenacity 共 3 次尝试
- **决策**：定时调度用 **arq `cron_jobs`**（worker 进程内，`HARBOR_CRAWL_INTERVAL_HOURS` 默认 12h，unique=True 防重复入队）——替代原计划的 APScheduler（同进程再养一个调度器属过度设计；tasks extras 的 apscheduler 保留给未来复杂调度）。HTTP 层 httpx 超时 10s；tenacity `stop_after_attempt(3)` + 1s 间隔。首轮量控制：每频道前 2 页 × 20 条。
- **影响**：worker 重写（`crawl_source` 真任务 + T8 修复接线 db1）；APScheduler 未引入运行时依赖。

### D12 插件抽象 async 化 + RBAC 接线
- **决策**：`SourcePlugin` 三方法改 async（网络 IO 与全异步栈一致，骨架期同步签名废弃）；sources/tasks 管理接口全部 `require_roles("admin")`（D7 兑现），文章接口公开；运维工具 `app/scripts/promote_admin.py` 创建/提升 admin。
- **影响**：`registry.py` 签名变更；前端 `/admin` 路由守卫 + 页面内角色兜底。

## 待决策

- （下轮补充：文章清洗/摘要 stage、评分接入、任务 retry/cancel、多源扩展）
