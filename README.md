# info-harbor

聚合全球多源 AI 动态，经 LLM 筛选评估后按国家/地区维度展示，助你快速捕捉世界 AI 前沿。

技术栈：**FastAPI（Python 3.12+）+ Vue 3（Vite + TypeScript）**。模块化单体、插件化扩展、事件驱动、配置治理。完整技术方案见协作目录 `D:\Decktop\计划\AI信息聚合平台技术方案.md`（建议后续同步进 `docs/`）。

## 仓库结构

```
├── backend/     FastAPI 后端（六边形架构，按领域拆包）
├── frontend/    Vue3 前端（Vite + TS + Pinia + Naive UI）
├── config/      YAML 业务规则配置（评分权重 / 筛选规则 / 管道拓扑 / 数据源）
└── docker-compose.yml   本地基础设施编排（未来统一用 docker 启动 Redis / MinIO）
```

## 快速开始

> 前提：本机 MySQL（3306，`root/root`，库 `info_harbor`）与 Redis（6379）已运行。
> 安装/启动方式因开发机而异：公共约定见 `backend/docs/DOCKER.md`；各机器细节记在各自 gitignored 的
> `backend/docs/LOCAL_ENV_<机器名>.md`（模板见 `LOCAL_ENV_TEMPLATE.md`）。

### 1. 环境变量

复制 `.env.example` 为 `.env`（gitignored，不会提交），按需修改：
`HARBOR_JWT_SECRET` 必须改为随机长字符串（生产必填）。

### 2. 后端（FastAPI）

依赖已装在 `backend/.venv`（含认证 `auth` extras），直接启动：

**PowerShell（Windows）**

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

**Git Bash / macOS / Linux**

```bash
cd backend
source .venv/Scripts/activate   # macOS/Linux 用 .venv/bin/activate
uvicorn app.main:app --reload
```

数据库迁移（首次或改模型后）：

```bash
cd backend
.venv/Scripts/alembic upgrade head
```

启动后验证：

- 健康检查：<http://localhost:8000/health>
- Swagger 文档：<http://localhost:8000/docs>（含认证接口）
- 文章列表：<http://localhost:8000/api/v1/articles>

### 3. 前端（Vue3 + Vite）

```bash
cd frontend
npm run dev
```

启动后访问 <http://localhost:5173>，登录页在 <http://localhost:5173/login>（注册 → 登录 → 进入首页）。

### 4. 基础设施（可选）

PostgreSQL / MinIO 目前阶段非启动 API/前端的前置条件，需要时再起（Redis 已在本地运行）：

```bash
docker compose up -d redis minio
```

## Git 协作约定

- 个人/功能分支开发 → 确认后合并到 `main`，不直接改主分支。
- 前后端**同仓库、分目录**（`backend/` / `frontend/`）。

## 路线图

MVP（抓取 → 清洗 → 规则初筛 → 展示）→ V2（LLM 全面接入 + 国内源）→ V3（搜索推荐 + 多语言 + 实时）。详见技术方案 §11。
