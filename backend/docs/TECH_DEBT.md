# 已知技术债（TECH_DEBT）

> 发现问题记录在此，不顺手修复；修复后移入「已解决历史」。

## 当前技术债

### T2 in-process 事件总线的跨进程局限
- **现象**：API 与 worker 各持独立 EventBus，事件不跨进程传递。
- **影响**：worker 内发布的 `ArticleRawIngested` 不会被 API 进程的消费方收到。
- **方案**：多 worker 后切 Redis Streams（见 DECISIONS D6）。当前 MVP 可接受。
- **实测复现**：2026-09-03 跑通验证确认——worker 进程内向自建 EventBus 发布 `ArticleRawIngested` 无 handler 消费；隔离实验：空总线 publish 为静默空操作（不报错、handler 数 0）。

### T3 配置治理 YAML 加载未验证
- `core/config.py` 声明 `CONFIG_DIR`，但 `get_settings()` 仅加载 env，未实际读取 `config/*.yaml` 业务规则。
- **方案**：爬虫/规则初筛阶段接入 YAML 加载。

### T4 Redis 服务不自启（Windows 机）
- **现象**：Windows 机用下载版 Redis 7.4.11，需手动启动且重启后不自启（启动命令记在该机 `LOCAL_ENV_WINDOWS.md`，2026-09-03 从公共文档迁出）。
- **方案**：后续统一 docker-compose 编排，或注册为 Windows 服务。

### T5 前端 /auth/me 启动时异步回填
- **现象**：`authStore.init()` 在 App.vue `onMounted` 异步拉取用户；刷新页面瞬间 header 可能短暂显示「登录」。
- **方案**：可接受（毫秒级）；后续可改为应用启动 `beforeMount` + splash，或同步读 localStorage 缓存 user。

### T6 前端登录/注册页面问题
- **现象**：
  1. 图形验证码显示太小，用户体验不佳
  2. 用户注册完跳转到登录页面后，验证码和密码字段会保留，需要手动清空
- **方案**：调整验证码尺寸；注册成功后清空表单字段

### T7 后端用户注册逻辑问题
- **现象**：
  1. 状态机过于单调，只有 active/disabled 两种状态
  2. 没有手机号字段
  3. 注册必须填写用户名和密码，过于严苛
- **方案**：增加更多状态；添加手机号字段；优化注册流程

### T10 时间字段时区混乱，前端耗时/时间显示错乱
- **现象**（2026-09-03 M1 验收截图发现）：任务监控"耗时 1147m"（实际约 1 小时）；同一任务 created_at=06:00 与 started_at=前一日 22:00 相差 8 小时；「累计入库条数」在任务运行中恒为 0（result_count 仅在任务结束时回写，统计口径误导）。
- **根因**：时间值多方混写且无统一时区约定——`created_at` 走 MySQL `NOW()`（会话时区）、`started_at/finished_at` 由 Python 写 aware-UTC（aiomysql 对 aware datetime 再做偏移转换）、arq cron 自行解释触发时区；API 序列化为**无时区后缀**的 naive 字符串，前端 `new Date()` 按浏览器本地时区解析。
- **方案**：统一 UTC 约定——MySQL 连接显式设会话时区 UTC（connect_args）+ Python 全部写 naive-UTC 或全 aware + 序列化带 `Z` 后缀 + 前端按 ISO8601 解析；「累计入库条数」改读 articles 表 total。涉及存量数据口径，需专项一轮（勿顺手修）。

## 已解决历史

### R1 根 README 引用不存在的子 README（原 T1）
- **现象**：`README.md` 引用 `backend/README.md` 与 `frontend/README.md`，两文件均不存在。
- **解决**：dev 分支根 `README.md` 改为内联快速开始（含 .env / 迁移 / 登录说明），不再引用不存在的子 README。
- **解决时间**：登录认证轮次（2026-08）。

### R2 `__pycache__` 被误提交进版本库（原 T1）
- **现象**：`git ls-files` 含 14 个 `.pyc`（`backend/app/**/__pycache__/*.cpython-314.pyc`）。`.gitignore` 已忽略 `__pycache__/`，但已跟踪文件不受忽略影响。
- **解决**：`git rm -r --cached` 移除全部已跟踪 `.pyc`（磁盘文件保留），随环境去机器化轮次提交。
- **解决时间**：2026-09-03。

### R3 环境文档被单机事实污染（原「跨机器环境问题」）
- **现象**：`DOCKER.md` 以 Windows 视角写成环境「唯一事实来源」（Redis 路径 `D:\...`），而 macOS 机 `.env` 已是 brew，文档与实际漂移。
- **解决**：见 `DECISIONS.md` D9——公共 docs 只写服务约定，机器差异迁入各机 gitignored 的 `LOCAL_ENV_<机器名>.md`（模板入库）；同时删除失效的 `requirements.txt`（依赖权威源 = pyproject extras）。
- **解决时间**：2026-09-03。

### R4 worker 队列接线脱节 + 占位任务必失败（原 T8/T9）
- **现象**：T8——`WorkerSettings` 未接 `HARBOR_TASK_QUEUE_URL`，arq 实际连 db0（配置写 db1 且无消费方）；T9——占位任务 `run_pipeline` 构造事件缺必填 `aggregate_id`，一跑即 ValidationError。
- **解决**：M1 轮 worker 重写时一并落地（方案已批准）——`redis_settings = RedisSettings.from_dsn(settings.task_queue_url)` 接线 db1；`run_pipeline` 占位任务被真任务 `crawl_source` 取代（事件均带 `aggregate_id`）。
- **解决时间**：爬虫 M1 轮（2026-09-03）。
