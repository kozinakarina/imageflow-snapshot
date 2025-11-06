"""Утилиты для работы с изображениями и цветовыми пространствами."""
import io
import numpy as np
from PIL import Image
from typing import Tuple


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    """Конвертация sRGB в linear RGB."""
    rgb = np.clip(rgb / 255.0, 0, 1)
    mask = rgb <= 0.04045
    rgb[mask] = rgb[mask] / 12.92
    rgb[~mask] = ((rgb[~mask] + 0.055) / 1.055) ** 2.4
    return rgb


def linear_to_srgb(linear: np.ndarray) -> np.ndarray:
    """Конвертация linear RGB в sRGB."""
    mask = linear <= 0.0031308
    linear[mask] = linear[mask] * 12.92
    linear[~mask] = 1.055 * (linear[~mask] ** (1.0 / 2.4)) - 0.055
    return np.clip(linear * 255.0, 0, 255).astype(np.uint8)


def pil_to_bytes(img: Image.Image, format: str = "PNG") -> bytes:
    """Конвертация PIL Image в байты."""
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def fetch_image(url: str) -> Image.Image:
    """Скачать изображение по URL и вернуть PIL Image."""
    import requests
    import sys
    from .retry_utils import safe_request
    
    print(f"[fetch_image] Начало загрузки: {url[:80]}...", flush=True)
    sys.stdout.flush()
    
    try:
        # Используем безопасный запрос с retry
        response = safe_request("GET", url, max_retries=3, timeout=30)
        
        print(f"[fetch_image] HTTP статус: {response.status_code}", flush=True)
        sys.stdout.flush()
        
        print(f"[fetch_image] Изображение загружено, размер: {len(response.content)} байт", flush=True)
        sys.stdout.flush()
        
        img = Image.open(io.BytesIO(response.content))
        print(f"[fetch_image] Изображение открыто: {img.size}, mode={img.mode}", flush=True)
        sys.stdout.flush()
        
        return img
    except requests.exceptions.RequestException as e:
        print(f"[fetch_image] ОШИБКА загрузки: {type(e).__name__}: {e}", flush=True)
        sys.stdout.flush()
        raise
    except Exception as e:
        print(f"[fetch_image] ОШИБКА обработки: {type(e).__name__}: {e}", flush=True)
        sys.stdout.flush()
        raise


def split_game_title(title: str) -> str:
    """
    Разделяет название игры на слова, вставляя пробелы.
    
    Примеры:
    - "15DragonCoins" -> "15 Dragon Coins"
    - "VIPAutoRoulette" -> "VIP Auto Roulette"
    - "HotBonus" -> "Hot Bonus"
    - "VIP" -> "VIP" (не разбивается)
    - "3DSlots" -> "3D Slots"
    - "ABC123Test" -> "ABC 123 Test"
    - "MGS_RedRake_getTheCoins" -> "MGS RedRake getTheCoins" (подчеркивание заменяется на пробел)
    - "MGSRedRakegetTheCoinsRedrake" -> "MGS RedRake get The Coins Redrake"
    
    Правила:
    1. Подчеркивание заменяется на пробел (_ -> пробел)
    2. Пробел между буквой и цифрой (Test123 -> Test 123)
    3. Пробел между цифрой и буквой (15D -> 15 D, но 3D -> 3D как отдельное слово)
    4. Пробел между строчной и заглавной буквой (tB -> t B, getThe -> get The)
    5. Пробел между последовательностью заглавных (2+) и следующей заглавной с строчными (VIPAuto -> VIP Auto)
    6. Пробел между заглавной с строчными и следующей заглавной (RedRakeget -> RedRake get)
    """
    import re
    
    # 0. Заменяем подчеркивания на пробелы (_ -> пробел)
    title = title.replace('_', ' ')
    
    # 1. Пробел между буквой и цифрой (Test123 -> Test 123)
    title = re.sub(r'([A-Za-z])(\d)', r'\1 \2', title)
    
    # 2. Пробел между цифрой и буквой (15Dragon -> 15 Dragon)
    # Но сохраняем паттерны типа "3D" как одно слово, если следующая буква заглавная
    title = re.sub(r'(\d)([A-Za-z])', r'\1 \2', title)
    
    # 3. Пробел между строчной и заглавной буквой (HotBonus -> Hot Bonus, getThe -> get The)
    title = re.sub(r'([a-z])([A-Z])', r'\1 \2', title)
    
    # 4. Пробел между последовательностью заглавных (2+) и следующей заглавной с строчными
    # (VIPAuto -> VIP Auto, но VIP -> VIP)
    title = re.sub(r'([A-Z]{2,})([A-Z][a-z])', r'\1 \2', title)
    
    # 5. Пробел между заглавной+строчными и следующей заглавной (RedRakeget -> RedRake get)
    # Это обрабатывает случаи типа "RedRakegetTheCoins" -> "RedRake get The Coins"
    title = re.sub(r'([A-Z][a-z]+)([A-Z])', r'\1 \2', title)
    
    # Удаляем лишние пробелы
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Конвертация hex цвета в RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Конвертация RGB tuple в hex строку."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"



