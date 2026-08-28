# info-harbor 后端

聚合全球多源 AI 动态，经 LLM 筛选评估后按国家/地区维度展示。后端 FastAPI + 全异步栈（async SQLAlchemy + aiomysql + ARQ + structlog + MinIO）。

## 启动流程

按顺序读取 `docs/`，每次一本，读完再读下一本：

1. `docs/PROJECT.md` — 项目是什么
2. `docs/ARCHITECTURE.md` — 系统怎么设计（六边形架构、事件链）
3. `docs/DOCKER.md` — 环境 / 基础设施（本地→docker 规划、端口速查）
4. `docs/DEVELOPMENT.md` — 代码怎么写（分层约束、命名、流程）
5. `docs/CURRENT_STATUS.md` — 开发到哪了
6. `docs/DEVELOPER_PROFILE.md` — 开发者画像与当前进度（理解「谁来学、怎么配合」时读；事实以 CURRENT_STATUS.md 为准）

基础设施（Redis / MinIO）见仓库根 `README.md` 的「快速开始」；数据库用本机 MySQL。

## 按任务查阅

| 任务 | 文档 |
|------|------|
| 开发接口 | `docs/API.md` |
| 修改数据库 | `docs/DATABASE.md` |
| 架构调整 | `docs/DECISIONS.md` |
| 了解已知问题 | `docs/TECH_DEBT.md` |
| AI 协作规则 | `docs/AI_AGENT_GUIDE.md` |

## 核心约束

- 所有详细规则在 docs/ 中，不要凭记忆猜测，去读对应的文档
- 改代码后必须同步更新 docs/ 中对应文档（对照表见 `docs/AI_AGENT_GUIDE.md`）
- 发现代码问题记录到 `docs/TECH_DEBT.md`，不要顺手修复
