# 接口定义（API）

> 当前仅有骨架端点，爬虫系统落地后补充完整字段与示例。

## 已实现端点

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/health` | 健康检查 | ✅ 可用 |
| GET | `/api/v1/articles` | 文章列表（分页/过滤/排序） | ⚠️ 返回空集 |
| GET | `/api/v1/articles/{id}` | 文章详情 | ⚠️ TODO 占位 |

## 规划中（爬虫系统 M1）

- `GET/POST /api/v1/sources` —— 数据源列表 / 创建
- `GET/PATCH/DELETE /api/v1/sources/{id}` —— 源详情 / 更新 / 删除
- `POST /api/v1/sources/{id}/crawl` —— 触发抓取（→ 202 任务）
- `GET /api/v1/tasks` —— 任务列表
- `GET /api/v1/tasks/{id}` —— 任务详情
- `POST /api/v1/tasks/{id}/retry` / `cancel` —— 重试 / 取消
