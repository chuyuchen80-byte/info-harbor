"""图形验证码生成：Pillow 手绘 PNG（无第三方 captcha 库，见 DECISIONS.md D7）。

- 字符集剔除易混字符（0/O/1/I/l）
- 返回 (code, png_bytes)；验证码与校验逻辑在 service 层（存 Redis，见 core/cache.py）
- 本模块为纯 CPU 同步代码；API 端点声明为 ``def`` 使其跑在 FastAPI 线程池，不阻塞事件循环
"""

from __future__ import annotations

import io
import random

from PIL import Image, ImageDraw, ImageFont

# 剔除易混字符：0/O、1/I/l
CAPTCHA_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"

# 画布尺寸
_WIDTH = 120
_HEIGHT = 48


def _load_font(size: int) -> ImageFont.ImageFont:
    """尝试加载系统等宽字体，失败则用 Pillow 内置位图字体兜底。"""
    for name in ("consola.ttf", "arial.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_captcha(length: int = 4) -> tuple[str, bytes]:
    """生成随机验证码，返回 ``(code, png_bytes)``。

    code 为大写字母/数字；调用方在落 Redis 时统一转小写存储，校验时大小写不敏感。
    """
    code = "".join(random.choices(CAPTCHA_ALPHABET, k=length))

    image = Image.new("RGB", (_WIDTH, _HEIGHT), _random_light_color())
    draw = ImageDraw.Draw(image)
    font = _load_font(30)

    # 干扰线 2~3 条
    for _ in range(random.randint(2, 3)):
        draw.line(
            [
                (random.randint(0, _WIDTH), random.randint(0, _HEIGHT)),
                (random.randint(0, _WIDTH), random.randint(0, _HEIGHT)),
            ],
            fill=_random_light_color(dark=True),
            width=random.randint(1, 2),
        )

    # 逐字符绘制（带微旋转），用整图旋转代替逐字旋转，避免字体对象复制复杂度
    char_x = 10
    for ch in code:
        char_img = Image.new("RGBA", (30, 44), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((2, 4), ch, font=font, fill=_random_dark_color())
        rotated = char_img.rotate(random.randint(-20, 20), expand=1)
        image.paste(rotated, (char_x, random.randint(2, 6)), rotated)
        char_x += 24

    # 噪点
    for _ in range(random.randint(80, 140)):
        draw.point(
            (random.randint(0, _WIDTH - 1), random.randint(0, _HEIGHT - 1)),
            fill=_random_light_color(dark=True),
        )

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return code, buf.getvalue()


def _random_light_color(dark: bool = False) -> tuple[int, int, int]:
    """浅色底/深色噪点。dark=True 生成偏深颜色（字符/干扰线用）。"""
    if dark:
        return (random.randint(30, 120), random.randint(30, 120), random.randint(30, 120))
    return (random.randint(220, 255), random.randint(220, 255), random.randint(220, 255))


def _random_dark_color() -> tuple[int, int, int]:
    return _random_light_color(dark=True)