# 环境 / 基础设施

> **唯一陈述：MySQL 与 Redis 当前走本机（brew），后续统一用 docker-compose 启动。**
> 本文档是环境描述的唯一事实来源，其他文档只引用此处，不再各写各的端口。

## 概念速记（学 docker 用）

| 概念 | 是什么 | 类比 |
|------|--------|------|
| image 镜像 | 模板，只读 | 安装包 |
| container 容器 | 镜像的运行实例 | 正在跑的程序 |
| volume 卷 | 容器外的持久化数据盘 | 硬盘 |
| port 端口映射 | 容器端口 ↔ 宿主机端口 | 接线板插孔 |
| compose | 多容器编排文件 | 一键启动脚本 |

## 当前：本地（brew）

| 服务 | 来源 | 端口 | 说明 |
|------|------|------|------|
| MySQL | 本机 brew | 3306 | 库 `info_harbor`，用户 `root/root` |
| Redis | 本机 brew | 6379 | `brew services start redis` 即起 |

## 未来：容器（docker-compose）

> 等学会 docker 后，统一用 `docker compose up` 编排，本机 brew 实例可停掉。

| 服务 | 镜像 | 宿主机端口 | 说明 |
|------|------|-----------|------|
| Redis | redis:7-alpine | **6380** | 映射到容器 6379；用 6380 以免与本地 6379 冲突 |
| MinIO | minio/minio | 9000 / 9001 | 原始快照存储（**预留，暂未启用**，见下） |

## MinIO：预留，暂未配置

- 代码侧仅 `articles.raw_snapshot_key` 字段预留，尚无真正的 MinIO 读写客户端。
- 等真正接入「抓取原始快照」时再启用（届时 `docker compose up minio` + 在 `.env` 配 `HARBOR_MINIO_*`，默认 localhost:9000）。

## 端口演进说明

- 本地 Redis 用 **6379**；docker 版 Redis 映射到 **6380**，以免与本机实例冲突。
- PostgreSQL 曾用 @5433，已随 D1 决策切到 MySQL，不再相关。

## 常用命令

```bash
# 当前本地：起 MySQL（若未起）/ Redis
brew services start mysql
brew services start redis

# 未来容器：起 Redis + MinIO（本机 brew 实例可先停）
# docker compose up -d redis minio
# docker ps            # 查看运行中的容器
# docker logs harbor-redis
# docker exec -it harbor-redis sh
# docker compose down
# docker ps --format '{{.Names}}\t{{.Ports}}'   # 查端口映射
```

> 详细命令与心智模型在学习期由 DOCKER 学习笔记补充。
