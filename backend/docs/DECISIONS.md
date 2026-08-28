# 设计决策（DECISIONS）

> 重要设计决策记录在此，落地后划掉「待决策」项。

## 已决策

### D1 存储从 PostgreSQL 切换为 MySQL
- **决策**：数据库用本机 MySQL（brew，`root/root`，库 `info_harbor`），不走 docker。
- **原因**：作者熟悉 MySQL（CMS 同栈）；本机已有 MySQL 运行。
- **影响**：`asyncpg`/`pgvector` → `aiomysql`/`pymysql`；`JSONB` → `JSON`；docker-compose 移除 postgres 服务。
- **向量检索**：原 pgvector 预留能力推迟，后续语义去重可用独立向量库（MySQL 8.0.3+ 也支持向量近似搜索）。

### D2 数据源配置权威 = YAML seed + DB 运行时
- `config/sources/*.yaml` 作引导，`lifespan` 幂等 upsert 进 DB；CRUD 走 DB。

### D3 原始文章存 articles 单表 + status='raw'
- 复用 `Article` 契约，后续清洗/评分原地 UPDATE，不二次落库。

### D4 去重粒度 = url 唯一索引
- MVP 用 `articles.url` 唯一索引 + `ON CONFLICT DO NOTHING`；RedisBloom 语义去重推迟。

### D5 端口规划
- Redis 当前本机 **6379**（brew）；未来 docker 版映射到 **6380**，以免与本机实例冲突。
- 曾用 pg@5433，已随 D1 切到 MySQL，不再相关。

### D6 事件总线 in-process
- MVP 单进程 EventBus；多 worker 后切 Redis Streams（只换实现）。

## 待决策

- （爬虫阶段补充：RSS 解析用 feedparser / 抓取超时与重试策略 / 任务失败告警）
