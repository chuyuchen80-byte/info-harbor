# 系统架构（六边形 / 端口适配器）

> 本文档讲清"一个请求、一条数据怎么流转"，以及各层为什么存在。讲解者理解的版本，供速查。

## 整体分层

```
HTTP ──► FastAPI(main.py) ──► domain/<域>/api ──► domain/<域>/service ──► repository / 各域 models.py
                                                    │
                                                    └──► core/models（统一契约，全局唯一权威）
                                                    └──► core/events（事件总线）
                                                    └──► core/config（配置）
                                                    └──► core/db（异步会话）
```

## 请求链路（核心）

```
http → api → service → (repository → 各域 models.py / 或 plugins)
```

- **api**：只接 HTTP 请求、调 service、返回响应。不写业务、不直接碰 DB。
- **service**：业务逻辑全在这。负责调 repository 做数据访问、调 plugins 做抓取/处理。
- **repository**：数据库访问层（对标 CMS 的 models.py 碰 DB 部分），持有一个 session。
- **各域 models.py**：该域的 ORM 模型（SQLAlchemy），**不是**统一数据形状。
- **core/models**：Pydantic 统一契约（Article/Source/Score/Entity），**整个项目最权威的模型列表**。所有层共用，别在各域各写一份。

## plugins = "插排"

- `utils/` 是被动工具箱（字符串/文件/时间处理），任何地方可调用。
- `plugins/` 是主动的能力扩展点（插槽）：插一个 `SourcePlugin` 就多一种数据源，插一个 processor 就多一道处理。
- 核心只认抽象接口（`SourcePlugin` 的 list_items / fetch_detail / normalize），不认具体实现。

## 事件驱动（解耦主线）

`core/events.py` 定义事件链：

```
raw → cleaned → translated → screened → scored → ready
```

各阶段只监听自己关心的事件，互不调用。当前用 in-process EventBus，多 worker 后切 Redis Streams。

## 领域划分

`domain/` 下六域：`articles` / `sources` / `screening` / `stats` / `tasks` / `users`。每域同构三层：`api / service / repository`。M1（爬虫系统）后：users（认证）/ articles（真实列表详情）/ sources（CRUD+触发）/ tasks（任务监控）四域落地；screening / stats 仍为骨架。

## 插件落地（M1）

- `SourcePlugin` 抽象已 async 化（list_items / fetch_detail / normalize，输入 `Source` 契约）
- 首个实现：`plugins/sources/infoq.py`（InfoQ JSON 接口，12 频道，见 DECISIONS D10）
- 登记：`plugins/sources/__init__.py` 进程内单例 registry；worker 按 `source.adapter_key` 取用

## 与 CMS 的关键差异

| 维度 | ai_cms_server | info-harbor |
|------|---------------|-------------|
| 分层方向 | 线性 api→schemas→services→models→core | 以域为中心，api→service→repository→core/models |
| 统一契约 | schemas = Pydantic 校验 | core/models = 全局唯一权威契约 |
| ORM 位置 | 统一 models/ 目录 | 各域自己的 models.py |
| 扩展方式 | 写死业务逻辑 | plugins 插排式扩展 |
| 事件 | 无 | EventBus + 事件链 |

> 更完整的项目背景见 `PROJECT.md`；环境见 `DOCKER.md`；开发规范见 `DEVELOPMENT.md`。
