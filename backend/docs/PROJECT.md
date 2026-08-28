# 项目介绍

## 它是做什么的

info-harbor 是一个 **AI 信息聚合平台**：自动采集全球多个来源的 AI 动态，经过清洗、规则初筛、LLM 评估打分后，按国家/地区维度展示，帮用户快速捕捉世界 AI 前沿。

对应一条数据流水线（pipeline）：

```
采集(raw) → 清洗(clean) → 去重(dedup) → 语言识别(language) → 翻译(translate) → 规则初筛(rule_screen) → LLM 评分(scored) → 展示(ready)
```

## 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI 0.115 | 异步 ASGI |
| 数据库 | MySQL 8（本机，库 info_harbor） | 异步访问（aiomysql） |
| ORM | SQLAlchemy 2.0 async | `aiomysql` 驱动 |
| 任务队列 | ARQ | 基于 Redis 的异步任务 |
| 缓存/队列 | Redis | 去重、任务队列、事件 |
| 对象存储 | MinIO | 原始快照存储 |
| 日志 | structlog | 结构化日志 |
| 前端 | Vue 3 + Vite + TS + Pinia + Naive UI | 独立仓库目录 |

## 架构风格

端口适配器（六边形 / Hexagonal）架构：领域逻辑在中心，外部依赖（HTTP、数据库、消息、存储）通过「端口 + 适配器」接入，不直接耦合。

- **核心层 `core/`**：统一数据契约、领域事件总线、配置、LLM 网关、去重协调器
- **领域层 `domain/`**：按业务域拆包（articles / sources / screening / stats / tasks / users），每域同构分层 `api → service → repository`
- **插件层 `plugins/`**：数据源适配器（RSS/API）、处理 Stage（清洗/翻译/筛选）
- **配置层 `config/`**：YAML 业务规则（评分权重 / 筛选规则 / 管道拓扑 / 数据源）

详见 `ARCHITECTURE.md`。

## 路线图

- **MVP**：抓取 → 清洗 → 规则初筛 → 展示
- **V2**：LLM 全面接入 + 国内源
- **V3**：搜索推荐 + 多语言 + 实时

## 与 CMS 项目的对照（供熟悉 CMS 的开发者参考）

如果你做过 `ai_cms_server`（同步栈 CMS），本项目的关键差异：

| 维度 | ai_cms_server | info-harbor |
|------|---------------|-------------|
| 分层 | api → schemas → services → models → core（线性） | api → service → repository → core/models（端口适配器） |
| 数据模型 | models = ORM，schemas = Pydantic 校验 | core/models 是**统一契约**（Pydantic），ORM 在 domain/\<域\>/models.py |
| 异步 | 同步 + `asyncio.run` 桥接 AI | 全异步：async SQLAlchemy + ARQ |
| 事件 | 无 | EventBus + 领域事件链（raw→...→ready） |
| 日志 | 几乎无 | structlog 结构化日志 |
| 存储 | MySQL + 本地文件 | MySQL + Redis + MinIO |

> 更详细的架构讲解见 `ARCHITECTURE.md`；开发规范见 `DEVELOPMENT.md`。
