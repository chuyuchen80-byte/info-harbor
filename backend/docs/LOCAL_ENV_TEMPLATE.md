# 本机环境笔记（模板）

> 复制为 `LOCAL_ENV_<机器名>.md`（如 `LOCAL_ENV_MAC.md` / `LOCAL_ENV_WINDOWS.md`）后填写。
> `LOCAL_ENV_*.md` 已被 `.gitignore` 忽略，**只留在你自己的机器上，不提交**。
> 填写原则：这里只写「这台机器怎么装、怎么启动」；端口 / 库名等公共约定以 `DOCKER.md` 为准，不在此重复。

## 机器信息

- 机器标识：
- 系统：
- 项目路径：

## MySQL

- 安装方式：
- 启动 / 停止命令：
- 配置文件 / 数据目录：
- 已建库：`info_harbor`（迁移：`alembic upgrade head`）

## Redis

- 安装方式：
- 启动 / 停止命令：
- 是否自启：
- 验证：`redis-cli ping` → `PONG`

## Python / 前端

- Python 版本与来源（pyenv / 官方安装包）：
- venv 位置与激活命令：
- 依赖安装命令：`pip install -e ".[storage,auth,dev,tasks]"`
- Node 版本管理：

## 其他 / 坑

- （例：Redis 不自启重启后要手动起；防火墙 / 杀软拦端口；代理影响 pip……）
