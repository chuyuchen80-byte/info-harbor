"""登录接口测试。"""

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient


def test_login_success(client: TestClient, sample_captcha_response: dict):
    mock_user = MagicMock(
        id="uid", username="testuser", email="test@example.com",
        password_hash="$2b$12$...", role="user", status="active",
    )
    with patch("app.domain.users.service.auth.UserRepository") as mock_repo_cls:
        mock_repo = AsyncMock()
        mock_repo.get_by_account = AsyncMock(return_value=mock_user)
        mock_repo_cls.return_value = mock_repo
        with patch("app.domain.users.service.auth.verify_password", return_value=True):
            with patch("app.domain.users.service.auth.create_access_token", return_value="tok"):
                resp = client.post("/api/v1/auth/login", json={
                    "account": "testuser", "password": "pw",
                    "captcha_id": sample_captcha_response["captcha_id"], "captcha_code": "x",
                })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_captcha_wrong(client: TestClient, sample_captcha_response: dict, mock_redis):
    mock_redis.consume = AsyncMock(return_value=False)
    resp = client.post("/api/v1/auth/login", json={
        "account": "testuser", "password": "pw",
        "captcha_id": sample_captcha_response["captcha_id"], "captcha_code": "wrong",
    })
    assert resp.status_code == 400


def test_login_user_not_found(client: TestClient, sample_captcha_response: dict):
    with patch("app.domain.users.service.auth.UserRepository") as mock_repo_cls:
        mock_repo = AsyncMock()
        mock_repo.get_by_account = AsyncMock(return_value=None)
        mock_repo_cls.return_value = mock_repo
        resp = client.post("/api/v1/auth/login", json={
            "account": "none", "password": "pw",
            "captcha_id": sample_captcha_response["captcha_id"], "captcha_code": "x",
        })
    assert resp.status_code == 401


def test_login_wrong_password(client: TestClient, sample_captcha_response: dict):
    mock_user = MagicMock(password_hash="$2b$...", status="active")
    with patch("app.domain.users.service.auth.UserRepository") as mock_repo_cls:
        mock_repo = AsyncMock()
        mock_repo.get_by_account = AsyncMock(return_value=mock_user)
        mock_repo_cls.return_value = mock_repo
        with patch("app.domain.users.service.auth.verify_password", return_value=False):
            resp = client.post("/api/v1/auth/login", json={
                "account": "testuser", "password": "wrong",
                "captcha_id": sample_captcha_response["captcha_id"], "captcha_code": "x",
            })
    assert resp.status_code == 401


def test_login_account_locked(client: TestClient, sample_captcha_response: dict, mock_redis):
    mock_redis.get = AsyncMock(return_value="5")
    resp = client.post("/api/v1/auth/login", json={
        "account": "locked", "password": "pw",
        "captcha_id": sample_captcha_response["captcha_id"], "captcha_code": "x",
    })
    assert resp.status_code == 429


def test_login_account_disabled(client: TestClient, sample_captcha_response: dict):
    mock_user = MagicMock(password_hash="$2b$...", status="disabled")
    with patch("app.domain.users.service.auth.UserRepository") as mock_repo_cls:
        mock_repo = AsyncMock()
        mock_repo.get_by_account = AsyncMock(return_value=mock_user)
        mock_repo_cls.return_value = mock_repo
        with patch("app.domain.users.service.auth.verify_password", return_value=True):
            resp = client.post("/api/v1/auth/login", json={
                "account": "disabled", "password": "pw",
                "captcha_id": sample_captcha_response["captcha_id"], "captcha_code": "x",
            })
    assert resp.status_code == 401
