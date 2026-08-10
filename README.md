# info-harbor

聚合全球多源 AI 动态，经 LLM 筛选评估后按国家/地区维度展示，助你快速捕捉世界 AI 前沿。

技术栈：**FastAPI（Python 3.12+）+ Vue 3（Vite + TypeScript）**。模块化单体、插件化扩展、事件驱动、配置治理。完整技术方案见协作目录 `D:\Decktop\计划\AI信息聚合平台技术方案.md`（建议后续同步进 `docs/`）。

## 仓库结构

```
├── backend/     FastAPI 后端（六边形架构，按领域拆包）
├── frontend/    Vue3 前端（Vite + TS + Pinia + Naive UI）
├── config/      YAML 业务规则配置（评分权重 / 筛选规则 / 管道拓扑 / 数据源）
└── docker-compose.yml   本地基础设施（PostgreSQL / Redis / MinIO）
```

## 快速开始

基础设施（PostgreSQL / Redis / MinIO）：

```bash
docker compose up -d postgres redis minio
```

- 后端：见 `backend/README.md`
- 前端：见 `frontend/README.md`

## Git 协作约定

- 个人/功能分支开发 → 确认后合并到 `main`，不直接改主分支。
- 前后端**同仓库、分目录**（`backend/` / `frontend/`）。

## 路线图

MVP（抓取 → 清洗 → 规则初筛 → 展示）→ V2（LLM 全面接入 + 国内源）→ V3（搜索推荐 + 多语言 + 实时）。详见技术方案 §11。
