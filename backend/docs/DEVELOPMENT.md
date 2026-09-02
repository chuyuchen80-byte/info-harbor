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

## 四、测试规范

> 每次开发/修改接口都需要测试用例。

### 测试工作流

**新接口**：
1. 开发完接口后，等用户确认功能正常
2. 用户确认后再编写测试用例
3. 测试文件放在 `tests/` 目录，文件名 `test_<模块名>.py`

**修改接口**：
1. 在原有测试文件中新增测试用例
2. 新用例需说明与上一版的区别
3. 保留原有测试用例，不删除

### 测试文件组织

```
tests/
├── conftest.py          # 共享 fixtures（client、db_session、auth_headers）
├── test_auth.py         # 认证接口测试
├── test_articles.py     # 文章接口测试
└── test_*.py            # 其他接口测试
```

### 测试命名规范

- 文件：`test_<模块名>.py`
- 类：`Test<接口组名>`
- 方法：`test_<接口名>_<场景>`

```python
class TestLogin:
    async def test_login_success(self, client, auth_headers):
        """正常登录。"""
        ...

    async def test_login_wrong_password(self, client):
        """密码错误。"""
        ...
```

### 接口开发测试要求

**新接口：**
1. 创建对应的测试文件
2. 覆盖正常流程和错误场景
3. 测试认证、权限、边界条件

**修改接口：**
1. 保留原有测试用例
2. 新增测试用例说明与原接口的区别
3. 通过注释标注变更点

```python
async def test_new_behavior(self, client):
    """测试新行为（v2 接口新增功能）。"""
    # 原接口：返回 200
    # 新接口：返回 201 并包含额外字段
    ...
```

### 测试覆盖要求

| 场景 | 必须覆盖 |
|------|----------|
| 正常流程 | ✅ |
| 认证/授权 | ✅ |
| 参数校验 | ✅ |
| 错误码 | ✅ |
| 边界条件 | ✅ |
| 并发/幂等 | 按需 |

### 运行测试

```bash
# 运行所有测试
pytest

# 运行指定文件
pytest tests/test_auth.py

# 运行指定测试方法
pytest tests/test_auth.py::TestLogin::test_login_success

# 查看详细输出
pytest -v
```

