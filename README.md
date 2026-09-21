# info-harbor

聚合全球多源 AI 动态，经 LLM 筛选评估后按国家/地区维度展示，助你快速捕捉世界 AI 前沿。

技术栈：**FastAPI（Python 3.12+，全异步）+ Vue 3（Vite + TypeScript）**。六边形架构、插件化扩展、事件驱动（EventBus + ARQ）、配置治理。设计决策与架构详见 `backend/docs/`。

## 仓库结构

```
├── backend/     FastAPI 后端（六边形架构，按领域拆包；docs/ 为全部文档）
├── frontend/    Vue3 前端（Vite + TS + Pinia + Naive UI）
├── config/      YAML 业务规则配置（数据源 / 评分权重 / 筛选规则 / 管道拓扑）
└── docker-compose.yml   本地基础设施编排（Redis / MinIO）
```

## 快速开始

> 前提：本机 MySQL（3306，`root/root`，库 `info_harbor`）与 Redis（6379）已运行。
> 安装/启动方式因开发机而异：公共约定见 `backend/docs/DOCKER.md`；各机器细节记在各自 gitignored 的
> `backend/docs/LOCAL_ENV_<机器名>.md`（模板见 `LOCAL_ENV_TEMPLATE.md`）。

### 1. 环境变量

复制 `.env.example` 为 `.env`（gitignored，不会提交），按需修改：
`HARBOR_JWT_SECRET` 必须改为随机长字符串（生产必填）。

### 2. 后端（FastAPI）

依赖装在虚拟环境 `backend/.venv`，安装方式（首次或换机器后）：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[storage,tasks,crawler,auth,dev]"
```

> extras 组说明见 `backend/docs/DEVELOPMENT.md`（存储 / 任务 / 抓取 / 认证 / 开发）。

启动 API：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

数据库迁移（首次或改模型后）：

```bash
cd backend
.venv/bin/alembic upgrade head
```

启动后验证：

- 健康检查：<http://localhost:8000/health>
- Swagger 文档：<http://localhost:8000/docs>
- 文章列表：<http://localhost:8000/api/v1/articles>
- 来源概况（公开）：<http://localhost:8000/api/v1/sources/overview>

### 3. Worker（ARQ 异步任务队列）

定时抓取与手动触发的执行端（M1 爬虫核心，需与 API 并行运行）：

```bash
cd backend
.venv/bin/arq app.worker.WorkerSettings
```

> 手动触发抓取：`POST /api/v1/sources/{source_id}/crawl`（需 admin token，Swagger 可试）。
> 定时调度：arq cron，默认每 12 小时全量 enabled 源入队（`HARBOR_CRAWL_INTERVAL_HOURS` 可调）。

### 4. 前端（Vue3 + Vite）

```bash
cd frontend
npm run dev
```

启动后访问 <http://localhost:5173>，登录页在 <http://localhost:5173/login>（注册 → 登录 → 进入首页）。

### 5. 基础设施（可选）

Redis 本机已运行；MinIO（原始快照存储，V2 接入）需要时再起：

```bash
docker compose up -d minio
```

## Git 协作约定

- 个人/功能分支开发 → 确认后合并到 `dev`，再合 `main`，不直接改主分支。
- 前后端**同仓库、分目录**（`backend/` / `frontend/`）。

## 路线图

MVP（抓取 → 清洗 → 规则初筛 → 展示）→ V2（LLM 全面接入 + 国内源）→ V3（搜索推荐 + 多语言 + 实时）。

M1 已落地爬虫管理系统（InfoQ 源、任务管理、前端监控面板），详见 `backend/docs/CURRENT_STATUS.md`。
