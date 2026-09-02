"""注册接口测试。"""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


def test_register_success(client: TestClient, sample_captcha_response: dict, mock_redis):
    """成功注册，返回 201。"""
    with patch("app.domain.users.service.auth.UserRepository") as mock_repo_cls:
        mock_repo = AsyncMock()
        mock_repo.exists = AsyncMock(return_value=False)
        mock_repo.create = AsyncMock(return_value=MagicMock(
            id="uid", username="testuser", email="test@example.com",
            role="user", status="active", last_login_at=None,
        ))
        mock_repo_cls.return_value = mock_repo

        resp = client.post("/api/v1/auth/register", json={
            "username": "testuser", "email": "test@example.com",
            "password": "password123", "captcha_id": sample_captcha_response["captcha_id"],
            "captcha_code": "x",
        })

    assert resp.status_code == 201
    assert resp.json()["username"] == "testuser"


def test_register_captcha_missing(client: TestClient):
    resp = client.post("/api/v1/auth/register", json={
        "username": "test", "email": "a@b.com", "password": "123456",
        "captcha_id": "", "captcha_code": "",
    })
    assert resp.status_code == 400


def test_register_captcha_wrong(client: TestClient, sample_captcha_response: dict, mock_redis):
    mock_redis.consume = AsyncMock(return_value=False)
    resp = client.post("/api/v1/auth/register", json={
        "username": "testuser", "email": "test@example.com",
        "password": "password123", "captcha_id": sample_captcha_response["captcha_id"],
        "captcha_code": "wrong",
    })
    assert resp.status_code == 400


def test_register_duplicate(client: TestClient, sample_captcha_response: dict):
    with patch("app.domain.users.service.auth.UserRepository") as mock_repo_cls:
        mock_repo = AsyncMock()
        mock_repo.exists = AsyncMock(return_value=True)
        mock_repo_cls.return_value = mock_repo

        resp = client.post("/api/v1/auth/register", json={
            "username": "existing", "email": "a@b.com",
            "password": "123456", "captcha_id": sample_captcha_response["captcha_id"],
            "captcha_code": "x",
        })
    assert resp.status_code == 409


def test_register_invalid_email(client: TestClient):
    resp = client.post("/api/v1/auth/register", json={
        "username": "testuser", "email": "bad",
        "password": "123456", "captcha_id": "x", "captcha_code": "x",
    })
    assert resp.status_code == 422