# 数据库设计

> 存储：本机 MySQL 8（库 `info_harbor`，`root/root`）。异步访问（aiomysql）。

## 表清单

### sources（数据源）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(64) PK | 源 ID |
| name | VARCHAR(200) | 名称 |
| country | VARCHAR(8) | 国家码 |
| type | VARCHAR(32) | media / arxiv / github ... |
| adapter_key | VARCHAR(64) | 对应 SourcePlugin.key |
| config | JSON | 源配置（feed_url 等） |
| weight | FLOAT | 权重 |
| enabled | BOOLEAN | 是否启用 |
| health | JSON | 健康度 |
| created_at / updated_at | DATETIME | 时间戳 |

### articles（文章）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(64) PK | |
| source_id | VARCHAR(64) FK→sources | 索引 |
| title | VARCHAR(500) | |
| url | VARCHAR(512) | **唯一索引**（去重）；utf8mb4 下 767 字节上限，故限 512 |
| raw_url | VARCHAR(512) | |
| content / summary / content_translated | TEXT | |
| author | VARCHAR(200) | |
| published_at | DATETIME | |
| detected_lang / translated_lang / country / source_type | VARCHAR | |
| tags / entities / categories / ext_json | JSON | |
| status | VARCHAR(32) | raw / cleaned / ... / ready，索引 |
| cluster_id / raw_snapshot_key | VARCHAR | |

### crawl_tasks（抓取任务）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(64) PK | |
| source_id | VARCHAR(64) FK→sources | 索引 |
| status | VARCHAR(32) | queued / running / succeeded / failed，索引 |
| task_type | VARCHAR(32) | manual / scheduled |
| arq_job_id | VARCHAR(64) | ARQ 任务 ID |
| result_count | INT | 产出条数 |
| error | TEXT | 失败原因 |
| created_at / started_at / finished_at | DATETIME | 生命周期时间戳 |

### users（用户，认证/权限）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | VARCHAR(64) PK | uuid4().hex |
| username | VARCHAR(64) 唯一 | 登录账号（2-64 字符） |
| email | VARCHAR(200) 唯一 | 邮箱（登录也可用） |
| password_hash | VARCHAR(255) | bcrypt 哈希，不存明文 |
| role | VARCHAR(32) | user / admin（默认 user，RBAC 预留） |
| status | VARCHAR(32) | active / disabled（默认 active） |
| created_at / updated_at | DATETIME | 时间戳 |
| last_login_at | DATETIME | 最近登录时间 |

## JSON 字段说明

MySQL 8 用 `JSON` 类型（PostgreSQL 的 `JSONB` 等价替代）。`config` / `health` / `tags` / `entities` / `categories` / `ext_json` 均为 JSON。

## 迁移流程

```bash
# 改 models 后生成迁移
alembic revision --autogenerate -m "描述"
# 检查生成的 SQL，再执行
alembic upgrade head
```

> 当前迁移：
> - `3c9d2c1976b3`（sources / articles / crawl_tasks 初始表）
> - `2941dfbc0d58`（users 表，认证/权限）
