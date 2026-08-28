# 已知技术债（TECH_DEBT）

> 发现问题记录在此，不顺手修复；修复后移入「已解决历史」。

## 当前技术债

### T1 根 README 引用不存在的子 README
- **现象**：`README.md` 引用 `backend/README.md` 与 `frontend/README.md`，两文件均不存在。
- **影响**：新读者按README找不到文档。
- **方案**：补 `backend/README.md`；或改根 README 引用 `backend/CLAUDE.md` + `backend/docs/`。

### T2 `__pycache__` 被误提交进版本库
- **现象**：`git ls-files` 含 `*.pyc`（约 20 个）。`.gitignore` 已忽略 `__pycache__/`，但已跟踪文件不生效。
- **方案**：`git rm -r --cached` 清理已跟踪的 `.pyc`，提交一次。

### T3 in-process 事件总线的跨进程局限
- **现象**：API 与 worker 各持独立 EventBus，事件不跨进程传递。
- **影响**：worker 内发布的 `ArticleRawIngested` 不会被 API 进程的消费方收到。
- **方案**：多 worker 后切 Redis Streams（见 DECISIONS D6）。当前 MVP 可接受。

### T4 配置治理 YAML 加载未验证
- `core/config.py` 声明 `CONFIG_DIR`，但 `get_settings()` 仅加载 env，未实际读取 `config/*.yaml` 业务规则。
- **方案**：爬虫/规则初筛阶段接入 YAML 加载。

## 已解决历史

- （暂无）
