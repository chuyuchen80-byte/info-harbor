"""获取当前用户接口测试。"""

from unittest.mock import AsyncMock, MagicMock, patch

import jwt
from fastapi.testclient import TestClient


def test_me_success(client: TestClient):
    mock_user = MagicMock(
        id="uid", username="testuser", email="a@b.com",
        role="user", status="active", last_login_at=None,
    )
    from app.domain.users.api.deps import get_current_user
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: mock_user
    try:
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer tok"})
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_me_no_token(client: TestClient):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_invalid_token(client: TestClient):
    with patch("app.domain.users.api.deps.decode_access_token", side_effect=jwt.InvalidTokenError):
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer bad"})
    assert resp.status_code == 401


def test_me_expired_token(client: TestClient):
    with patch("app.domain.users.api.deps.decode_access_token", side_effect=jwt.ExpiredSignatureError):
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer exp"})
    assert resp.status_code == 401


def test_me_user_not_found(client: TestClient):
    from app.domain.users.service.auth import InvalidCredentialsError
    with patch("app.domain.users.api.deps.decode_access_token", return_value={"sub": "x"}):
        with patch("app.domain.users.api.deps.get_auth_service") as mock_svc:
            mock_svc.return_value.get_user = AsyncMock(
                side_effect=InvalidCredentialsError("不存在")
            )
            resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer tok"})
    assert resp.status_code == 401
