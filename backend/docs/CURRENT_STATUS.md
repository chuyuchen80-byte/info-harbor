# 当前开发状态

> 本文档记录「开发到哪了」，是进度的唯一事实来源。其他文档里过期的进度描述以本文为准。

## 阶段定位

**早期骨架阶段 + 学习期**。架构骨架由朋友搭建完成，作者在熟悉架构、学习 docker 的过程中用 docs 当教材重建认知。爬虫管理系统（M1）尚未实现，先打基础。

## 已完成（骨架）

### 架构骨架
- 六边形分层目录：`core/` / `domain/`（六域）/ `plugins/` / `config/`
- `core/models/article.py`：统一数据契约 `Article` / `Source` / `Score` / `Entity`（Pydantic v2）
- `core/events.py`：in-process 事件总线 `EventBus` + 完整事件链（raw → cleaned → translated → screened → scored → ready）
- `core/config.py`：pydantic-settings 配置中心（`HARBOR_` 前缀 + 仓库根 `config/` YAML 规则目录）
- `core/db.py` / `core/logging.py`：异步 engine/session、structlog
- `core/llm_gateway.py` / `core/dedup.py`：抽象层占位
- `plugins/registry.py`：`SourcePlugin` 抽象类 + `Registry` 容器

### 已落地的真实文件（学习过程中创建）
- `domain/{sources,articles,tasks}/models.py`：三域 ORM 模型（字段对齐契约）
- alembic 脚手架 + `env.py`（async）+ 初始迁移 `3c9d2c1976b3`（sources/articles/crawl_tasks 三表，**已 upgrade 到本机 MySQL**）

### 基础设施
- 数据库：本机 MySQL（brew，`root/root`，库 `info_harbor`）
- 缓存：本机 Redis（brew，6379）
- MinIO：预留，暂未接入（`articles.raw_snapshot_key` 字段已建，无读写客户端）
- 依赖按 extras 分组：`crawler` / `storage` / `tasks` / `ai` / `dedup` / `dev`（已装到 `.venv`）

## 环境（MySQL / Redis 当前走本地，后续统一 docker）

- MySQL：本机 3306，`root/root`，库 `info_harbor`
- Redis：本机 6379（brew）
- MinIO：预留，暂未接入
- 曾用 PostgreSQL@5433，已切换为 MySQL（见 `DECISIONS.md` D1）

## 文档体系（对齐 CMS）

- 已建：`CLAUDE.md` / `PROJECT.md` / `ARCHITECTURE.md` / `DOCKER.md` / `DEVELOPMENT.md` / `CURRENT_STATUS.md` / `API.md` / `DATABASE.md` / `DECISIONS.md` / `TECH_DEBT.md` / `AI_AGENT_GUIDE.md` / `DEVELOPER_PROFILE.md`（gitignored）
- 根 README 仍引用不存在的 `backend/README.md` / `frontend/README.md`（见 `TECH_DEBT.md` T1）

## 当前任务进度

- [x] 装依赖、起本机 MySQL（info_harbor 库）+ 本机 Redis（6379）
- [x] 创建 db.py / logging.py / 三域 ORM 模型 / alembic 初始迁移并建表（MySQL）
- [x] 建立 docs 体系（12 个文件，对齐 CMS）
- [x] 学架构（ARCHITECTURE.md 已写，用户已理解请求链路/plugins 概念）
- [ ] 学 docker（DOCKER.md 已建骨架，命令实操待练）
- [ ] 跑通系统：起 uvicorn + arq worker + 观察日志
- [ ] 爬虫管理系统 M1（用户熟悉架构/学会 docker 后布置）

## 下一步计划

1. 练 docker 常用命令（ps/logs/exec/compose），完善 DOCKER.md
2. 起 uvicorn + worker 跑通，写复盘
3. 进入爬虫管理系统 M1
