"""验证码接口测试。"""

import base64
from fastapi.testclient import TestClient


def test_get_captcha_success(client: TestClient):
    """成功获取验证码，返回 captcha_id 和 image_base64。"""
    resp = client.get("/api/v1/auth/captcha")
    assert resp.status_code == 200
    data = resp.json()
    assert "captcha_id" in data
    assert "image_base64" in data
    assert len(data["captcha_id"]) == 32


def test_captcha_image_is_valid_png(client: TestClient):
    """验证码图片是有效的 PNG base64。"""
    resp = client.get("/api/v1/auth/captcha")
    data = resp.json()
    image_bytes = base64.b64decode(data["image_base64"])
    assert image_bytes[:8] == b"\x89PNG\r\n\x1a\n"
