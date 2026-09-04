# 当前开发状态

> 本文档记录「开发到哪了」，是进度的唯一事实来源。其他文档里过期的进度描述以本文为准。

## 阶段定位

**M1 爬虫管理系统已完成开发，待用户验收**。登录认证（2026-08）→ 跑通系统（2026-09-03）→ M1 首批源 InfoQ 接入（本轮）。

## 已完成（骨架）

### 架构骨架
- 六边形分层目录：`core/` / `domain/`（六域）/ `plugins/` / `config/`
- `core/models/article.py`：统一数据契约 `Article` / `Source` / `Score` / `Entity`（Pydantic v2）
- `core/events.py`：in-process 事件总线 `EventBus` + 完整事件链（raw → cleaned → translated → screened → scored → ready）
- `core/config.py`：pydantic-settings 配置中心（`HARBOR_` 前缀 + 仓库根 `config/` YAML 规则目录）
- `core/db.py` / `core/logging.py`：异步 engine/session、structlog
- `core/llm_gateway.py` / `core/dedup.py`：抽象层占位
- `plugins/registry.py`：`SourcePlugin` 抽象类 + `Registry` 容器

### 已落地的真实文件
- `domain/{sources,articles,tasks,users}.models.py`：四域 ORM 模型（字段对齐契约）
- alembic 脚手架 + `env.py`（async）+ 初始迁移 `3c9d2c1976b3`（sources/articles/crawl_tasks 三表，**已 upgrade 到本机 MySQL**）+ `2941dfbc0d58`（users 表，认证/权限）

### 登录认证（新增，2026-08）
- 完成：图形验证码 + 密码登录 + 注册，JWT（24h），验证码存 Redis（一次性、5 分钟 TTL），登录防爆破（5 次/5 分钟 → 429）
- 完成：前端登录/注册页（Naive UI）+ 路由守卫（未登录跳 /login）+ 401 自动清理 token；`/admin` 等带 `meta.role` 的页面未登录跳登录页
- RBAC 预留：`users.role`、JWT `role` claim、后端 `require_roles()`、前端 `meta.role`（权限管理轮次接线）

### 爬虫管理系统 M1（新增，2026-09-03）

- 完成：**InfoQ 适配器**（`plugins/sources/infoq.py`，12 频道 JSON 接口、score 游标翻页、trafilatura 提取正文，D10）
- 完成：**worker 真任务**（`crawl_source`：任务状态机 DB 为权威；修 T8 接线 db1、T9 占位任务删除；arq cron 定时默认 12h，D11）
- 完成：**三域 API 真实化**——sources（列表/详情/PATCH 启停/触发抓取）、tasks（列表/详情）、articles（真实分页列表/详情）；管理接口全部 `require_roles("admin")`（D12，RBAC 兑现）
- 完成：**seed**（`config/sources/infoq.yaml` + lifespan 幂等 upsert，不覆盖手动关停）；`app/scripts/promote_admin.py` 运维工具
- 完成：**前端管理页**三页签（爬虫管理 / 源管理 / 任务监控，Naive UI，风格对照高保真原型）；文章页/来源页风格改造未做
- 实测：手动触发端到端通——任务 queued→running，文章带正文落库（~480 条/轮上限，去重后增量有限）
- ⏳ 测试用例：按测试规范等用户确认功能正常后补（test_sources / test_tasks / test_articles）

### 前端对齐原型（新增，2026-09-04）

- 完成：**全局壳原型化**——吸顶头部（品牌渐变标 + 横向导航 + 激活态）、1180px 容器、页脚；导航栏「管理」入口仅 `role=admin` 渲染（未登录/普通用户不可见）
- 完成：**六个页面按 5174 原型重做**（真实数据填充原型壳）——总览（统计卡+动态流+国家热力+TOP8）、文章列表（筛选+卡片流+分页）、文章详情（正文阅读+侧栏摘要/信息）、国家/地区（左导航+热点+来源贡献条形）、来源（统计卡+卡片网格，走公开 overview）、搜索（本地检索壳，V3 换后端）
- 完成：**公开接口** `GET /sources/overview`（每源文章数/最近发布，来源页/国家页数据源）
- 修正：前端类型与后端实际响应对齐（snake_case，旧 camelCase 类型是错的）；ArticleCard/WorldHeat/timeAgo 等对齐原型
- 待办：评分调试/筛选规则页签为占位（V2）；T10 时区显示待专项

### 基础设施
- 数据库：本机 MySQL（`root/root`，库 `info_harbor`）
- 缓存：本机 Redis（6379）
- MinIO：预留，暂未接入（`articles.raw_snapshot_key` 字段已建，无读写客户端）
- 依赖按 extras 分组：`crawler` / `storage` / `tasks` / `ai` / `dedup` / `auth` / `dev`（装法：`pip install -e ".[...]"`）

## 环境（MySQL / Redis 当前走本地，后续统一 docker）

- 两台开发机（macOS / Windows）各自本机跑 MySQL 3306 + Redis 6379；公共约定见 `DOCKER.md`，各机器的安装/启动细节记在 gitignored 的 `docs/LOCAL_ENV_<机器名>.md`（见 DECISIONS.md D9）
- MinIO：预留，暂未接入
- 曾用 PostgreSQL@5433，已切换为 MySQL（见 `DECISIONS.md` D1）

## 文档体系（对齐 CMS）

- 已建：`CLAUDE.md` / `PROJECT.md` / `ARCHITECTURE.md` / `DOCKER.md` / `DEVELOPMENT.md` / `CURRENT_STATUS.md` / `API.md` / `DATABASE.md` / `DECISIONS.md` / `TECH_DEBT.md` / `AI_AGENT_GUIDE.md` / `DEVELOPER_PROFILE.md`（gitignored）/ `LOCAL_ENV_TEMPLATE.md`（机器本地笔记模板；各机器实际笔记 `LOCAL_ENV_*.md` gitignored）

## 当前任务进度

- [x] 装依赖、起本机 MySQL（info_harbor 库）+ 本机 Redis（6379）
- [x] 创建 db.py / logging.py / 四域 ORM 模型 / alembic 初始迁移并建表（MySQL）
- [x] 登录认证：图形验证码 + 密码登录/注册 + JWT + 防爆破 + 前端登录页与路由守卫
- [x] 建立 docs 体系（12 个文件，对齐 CMS）
- [x] 学架构（ARCHITECTURE.md 已写，用户已理解请求链路/plugins 概念）
- [x] 跑通系统：起 uvicorn + arq worker + 观察日志（2026-09-03 验证：uvicorn 8000 / worker 正常运行；入队 `run_pipeline` → Redis db0 → worker 消费全链路通；占位任务因缺 `aggregate_id` 抛 ValidationError（T9）、arq 实际连 db0（T8），均记录 TECH_DEBT 未修——已于 M1 轮修复，见 R4）
- [x] 爬虫管理系统 M1（后端最小链路 + 前端管理页；待验收后补测试）

## 下一步计划

1. M1 验收（Swagger / 管理页实际操作）→ 补测试用例 → 合并 dev
2. 下一轮候选：文章清洗/摘要 stage、任务 retry/cancel、第二个数据源、文章页/来源页风格对齐原型
