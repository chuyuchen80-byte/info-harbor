"""分层配置中心：pydantic-settings 管基础配置，YAML 管业务规则配置（§5）。

- 基础配置：环境变量 / .env 覆盖，前缀 `HARBOR_`
- 业务规则（评分权重/筛选规则/管道拓扑）：在仓库根 `config/` 下，可热加载
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py 往上 3 级 = 仓库根
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = PROJECT_ROOT / "config"


class Settings(BaseSettings):
    """基础配置。"""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_prefix="HARBOR_",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "info-harbor"
    debug: bool = False
    api_prefix: str = "/api/v1"

    cors_origins: list[str] = ["http://localhost:5173"]

    # 日志
    log_level: str = "INFO"
    log_json: bool = False

    # 数据源配置目录（config/sources/*.yaml，seed 引导用）
    source_config_dir: str = str(CONFIG_DIR / "sources")

    # 存储（本机 MySQL，用户 root/root，库 info_harbor）
    database_url: str = "mysql+aiomysql://root:root@127.0.0.1:3306/info_harbor"
    redis_url: str = "redis://localhost:6379/0"

    # 任务
    task_queue_url: str = "redis://localhost:6379/1"

    # 对象存储（原始快照）
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "harbor"
    minio_secret_key: str = "harbor-secret"
    minio_bucket: str = "harbor-raw"


@lru_cache
def get_settings() -> Settings:
    return Settings()
