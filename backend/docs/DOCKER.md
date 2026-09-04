# 环境 / 基础设施

> **唯一陈述：项目依赖本机 MySQL（3306，库 `info_harbor`，`root/root`）与本机 Redis（6379），由各开发机自行安装启动；后续统一用 docker-compose 编排。**
> 本文档只写「项目需要什么」；「你的机器怎么装、怎么启动」属于机器差异，写进各机器本地笔记
> `docs/LOCAL_ENV_<机器名>.md`（gitignored，模板见 `LOCAL_ENV_TEMPLATE.md`），**不再写进公共文档**。

## 公共约定（所有机器一致）

| 服务 | 端口 | 说明 |
|------|------|------|
| MySQL | 3306 | 库 `info_harbor`，用户 `root/root`；连接串走 `.env` 的 `HARBOR_DATABASE_URL` |
| Redis | 6379 | 登录验证码 + 防爆破计数依赖；未启动时对应接口返回 503（fail-closed） |

## 开发机与本地笔记

两台开发机协作（macOS / Windows）。安装路径、启动命令等机器差异各自记录：

| 机器 | 本地笔记（gitignored） | 记什么 |
|------|------------------------|--------|
| 任意 | `docs/LOCAL_ENV_TEMPLATE.md` | **模板（入库）**，复制填写 |
| macOS | `docs/LOCAL_ENV_MAC.md` | brew 服务管理、pyenv / venv 等 |
| Windows | `docs/LOCAL_ENV_WINDOWS.md` | MySQL 安装包、下载版 Redis 7.4.11 的启动命令等 |

- 复制模板为 `LOCAL_ENV_<机器名>.md` 后填写即可，`.gitignore` 已忽略 `LOCAL_ENV_*.md`，不会提交。
- **Windows 同学首次迁移**：旧版本文档里的 Redis 启动段落可在 git 历史找回（`git log -p backend/docs/DOCKER.md`），拷进你本地的笔记。

## 未来：容器（docker-compose）

> 后续统一用 `docker compose up` 编排，本机实例可停掉。

| 服务 | 镜像 | 宿主机端口 | 说明 |
|------|------|-----------|------|
| Redis | redis:7-alpine | **6380** | 映射到容器 6379；用 6380 以免与本地 6379 冲突 |
| MinIO | minio/minio | 9000 / 9001 | 原始快照存储（**预留，暂未启用**，见下） |

## MinIO：预留，暂未配置

- 代码侧仅 `articles.raw_snapshot_key` 字段预留，尚无真正的 MinIO 读写客户端。
- 等真正接入「抓取原始快照」时再启用（届时 `docker compose up minio` + 在 `.env` 配 `HARBOR_MINIO_*`，默认 localhost:9000）。

## 端口演进说明

- 本地 Redis 各机器统一 **6379**；docker 版 Redis 映射到 **6380**，以免与本机实例冲突。
- PostgreSQL 曾用 @5433，已随 D1 决策切到 MySQL，不再相关。

## 常用命令

```bash
# 各机器 MySQL / Redis 的安装与启动方式 → 看你自己的 LOCAL_ENV_<机器名>.md

# 未来容器：起 Redis + MinIO（本机实例可先停）
# docker compose up -d redis minio
# docker ps            # 查看运行中的容器
# docker ps --format '{{.Names}}\t{{.Ports}}'   # 查端口映射
```
