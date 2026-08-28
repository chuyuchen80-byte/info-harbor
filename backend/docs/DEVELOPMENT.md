# 开发规范

> 分层约束与命名规范。详细约定在实践过程中逐步补充。

## 一、分层约束

项目采用六边形（端口适配器）架构，依赖单向：

```
api → service → repository → core/models
```

### api/ — 路由层（inbound adapter）
- 接收 HTTP 请求、调用 service、返回响应
- **禁止**：写业务逻辑、直接操作数据库

### service/ — 业务层
- 所有业务逻辑；调用 repository、调用 plugins
- **禁止**：接收 Request 对象、返回 HTTPResponse

### repository/ — 数据访问层（outbound adapter）
- 数据库读写，持有一个 session
- **禁止**：写业务逻辑

### core/models — 统一契约
- 全局唯一权威的数据形状（Pydantic），所有层共用
- **禁止**：在各域各写一份；加领域私有字段

### plugins/ — 扩展插槽
- 数据源适配器（sources）、处理 Stage（processors）
- 必须实现抽象接口，通过 Registry 注册

## 二、命名规范

| 类型 | 规范 |
|------|------|
| Python 文件 | 全小写 + 下划线 |
| 类 | 大驼峰 |
| 函数 | 动词开头 |
| 数据库表 | 小写 + 下划线，复数（sources / articles / crawl_tasks） |
| API 路径 | 小写，资源复数（`/api/v1/sources`） |

## 三、API / DB 开发流程

```
需求 → 数据库设计 → Schemas(契约) → 各域 models(ORM) → repository → service → api → 测试
```

- 数据库变更走 Alembic 迁移，不直接改表
- 配置值用 `.env`，不硬编码
