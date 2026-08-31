# 已知技术债（TECH_DEBT）

> 发现问题记录在此，不顺手修复；修复后移入「已解决历史」。

## 当前技术债

### T1 `__pycache__` 被误提交进版本库
- **现象**：`git ls-files` 含 `*.pyc`（约 20 个，`backend/app/__pycache__/*.cpython-314.pyc` 等）。`.gitignore` 已忽略 `__pycache__/`，但已跟踪文件不生效。
- **方案**：`git rm -r --cached` 清理已跟踪的 `.pyc`，提交一次。

### T2 in-process 事件总线的跨进程局限
- **现象**：API 与 worker 各持独立 EventBus，事件不跨进程传递。
- **影响**：worker 内发布的 `ArticleRawIngested` 不会被 API 进程的消费方收到。
- **方案**：多 worker 后切 Redis Streams（见 DECISIONS D6）。当前 MVP 可接受。

### T3 配置治理 YAML 加载未验证
- `core/config.py` 声明 `CONFIG_DIR`，但 `get_settings()` 仅加载 env，未实际读取 `config/*.yaml` 业务规则。
- **方案**：爬虫/规则初筛阶段接入 YAML 加载。

### T4 Redis 服务需手动启动（Windows）
- **现象**：本机用下载版 Redis 7.4.11，需手动 `redis-server.exe --port 6379`（见 DOCKER.md），重启后不会自启。
- **方案**：后续统一 docker-compose 编排，或注册为 Windows 服务。

### T5 前端 /auth/me 启动时异步回填
- **现象**：`authStore.init()` 在 App.vue `onMounted` 异步拉取用户；刷新页面瞬间 header 可能短暂显示「登录」。
- **方案**：可接受（毫秒级）；后续可改为应用启动 `beforeMount` + splash，或同步读 localStorage 缓存 user。

## 已解决历史

### R1 根 README 引用不存在的子 README（原 T1）
- **现象**：`README.md` 引用 `backend/README.md` 与 `frontend/README.md`，两文件均不存在。
- **解决**：dev 分支根 `README.md` 改为内联快速开始（含 .env / 迁移 / 登录说明），不再引用不存在的子 README。
- **解决时间**：登录认证轮次（2026-08）。
