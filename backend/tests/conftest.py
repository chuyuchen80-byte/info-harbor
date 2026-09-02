"""测试配置：自动 mock Redis，无需每个测试单独处理。"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_redis():
    """自动 mock 所有 get_cache 引用，无需每个测试单独处理。"""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.setex = AsyncMock()
    mock.delete = AsyncMock()
    mock.consume = AsyncMock(return_value=True)
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    # patch 所有导入了 get_cache 的模块
    with patch("app.core.cache.get_cache", return_value=mock), \
         patch("app.domain.users.api.router.get_cache", return_value=mock), \
         patch("app.domain.users.service.auth.get_cache", return_value=mock):
        yield mock


@pytest.fixture
def client() -> TestClient:
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_captcha_response(client: TestClient) -> dict:
    resp = client.get("/api/v1/auth/captcha")
    assert resp.status_code == 200
    return resp.json()
