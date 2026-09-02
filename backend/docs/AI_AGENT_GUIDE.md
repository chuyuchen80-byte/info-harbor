# AI Agent 协作指南

本文档说明 AI（Claude Code）如何参与本项目的开发。

---

## 两阶段工作流（必读）

所有开发 / 重构 / 修复类任务均采用两阶段：**Plan → 确认 → Development**。

- **Plan 阶段**：只分析、只出方案，**不修改任何代码**。
- **确认**：Plan 输出后**必须等待用户确认**，确认后才进入 Development。
- **Development 阶段**：确认方案后再实现。
- 用户自行切换 CC 的 Plan / Development 模式，**提示词不指示 CC 切换模式**。

> 与 `DEVELOPER_PROFILE.md`（开发者画像）一致：用户明确要求提示词"必须两阶段：Plan → 确认 → Development"。

---

## 新会话必读

每次新的 Claude Code 会话启动时，按以下顺序阅读：

1. **[PROJECT.md](PROJECT.md)** — 项目是什么
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** — 系统架构（六边形、事件链）
3. **[DOCKER.md](DOCKER.md)** — 环境 / 基础设施（本地→docker 规划）
4. **[DEVELOPMENT.md](DEVELOPMENT.md)** — 开发规则
5. **[CURRENT_STATUS.md](CURRENT_STATUS.md)** — 当前进度
6. **[DEVELOPER_PROFILE.md](DEVELOPER_PROFILE.md)** — 开发者画像（不提交，仅本地可读；事实以 CURRENT_STATUS.md 为准）

---

## Plan 阶段要求

收到任务后，**先进入 Plan 阶段，不修改代码**，必须完成分析并向用户说明：

1. **当前现状分析** —— 相关代码/文档/测试的真实当前状态（读文件确认，不凭记忆）
2. **影响文件分析** —— 列出会被影响的文件，含跨层（api / service / repository / core / plugins / config）
3. **问题与目标** —— 要解决什么、预期结果、边界与非目标
4. **流程绘制** —— 请求 / 数据 / 状态流转（复杂任务必画图）
5. **多方案列举（必要时）** —— 存在多种合理实现时，列 2~N 种方案 + 优缺点对比，由用户决策

## 按任务读取

| 任务类型 | 必读文档 |
|----------|----------|
| 开发新接口 | [API.md](API.md) |
| 修改数据库 | [DATABASE.md](DATABASE.md) |
| 架构调整 | [DECISIONS.md](DECISIONS.md) |
| 了解已知问题 | [TECH_DEBT.md](TECH_DEBT.md) |
| 编写测试用例 | [DEVELOPMENT.md](DEVELOPMENT.md)（四、测试规范） |

---

## 测试工作流（必读）

每次开发或修改接口，都需要测试用例：

### 新接口
1. 开发完接口后，等用户确认功能正常
2. 用户确认后再编写测试用例
3. 测试文件放在 `tests/` 目录，文件名 `test_<模块名>.py`

### 修改接口
1. 在原有测试文件中新增测试用例
2. 新用例需说明与上一版的区别
3. 保留原有测试用例，不删除

### 测试用例格式
```python
def test_xxx_v2_new_behavior(client):
    """测试新行为（v2 接口新增功能）。"""
    # 原接口：返回 200
    # 新接口：返回 201 并包含额外字段
    ...
```

---

## 修改代码后必须同步更新文档

| 变更内容 | 需更新的文档 |
|----------|-------------|
| 新增接口 | [API.md](API.md) |
| 修改数据库 | [DATABASE.md](DATABASE.md) |
| 架构变化 | [ARCHITECTURE.md](ARCHITECTURE.md) |
| 重要设计决策 | [DECISIONS.md](DECISIONS.md) |
| 开发进度变化 | [CURRENT_STATUS.md](CURRENT_STATUS.md) |
| 发现新问题 | [TECH_DEBT.md](TECH_DEBT.md) |
| 新增开发规范 | [DEVELOPMENT.md](DEVELOPMENT.md) |

**文档作废要求（对治漂移）：** 更新文档时，不仅同步新增内容，也要作废已不适用的旧条目。阶段推进后，过期的进度描述及时清除，进度事实只保留在 `CURRENT_STATUS.md`。

---

## 行为约束

- 只修改与任务直接相关的文件，不做无关重构
- 遵循现有分层架构（api → service → repository → core/models），不引入新模式除非有明确决策
- 数据库变更必须通过 Alembic 迁移，不直接修改表
- 不在代码中硬编码配置值，使用 `.env` 环境变量
- 不将密钥提交到仓库

## 前端任务约定

前端提示词尽量简洁明确，**不引入 harness / 后端概念**。前端重点是功能展示和美观，不呈现为传统后台管理系统。

## 禁止事项

- 禁止在 `api/` 层写业务逻辑或直接操作数据库（交给 service / repository）
- 禁止在 `service/` 层接收 Request 对象或返回 HTTPResponse
- 禁止在 `core/models`（统一契约）里加领域私有字段——统一契约是单一权威，各层共用
- 禁止跳过 Schema 校验直接操作数据库
- 禁止修改 `.env` 或 `.env.example` 中的实际密钥值
