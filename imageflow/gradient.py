"""Генерация градиентного фона с linear RGB интерполяцией."""
import numpy as np
from PIL import Image
from typing import Tuple
from .utils import srgb_to_linear, linear_to_srgb, hex_to_rgb


def create_gradient_background(
    width: int,
    height: int,
    start_color: str,
    end_color: str,
    direction: str = "vertical",
    interpolation: str = "linear_rgb"
) -> Image.Image:
    """
    Создать градиентный фон.
    
    Args:
        width: Ширина изображения
        height: Высота изображения
        start_color: Начальный цвет (hex)
        end_color: Конечный цвет (hex)
        direction: Направление градиента ("vertical" или "horizontal")
        interpolation: Тип интерполяции ("linear_rgb" или "srgb")
        
    Returns:
        PIL Image (RGB) с градиентом
    """
    # Конвертируем hex в RGB
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    
    # Создаём массив для градиента
    gradient = np.zeros((height, width, 3), dtype=np.float32)
    
    if direction == "vertical":
        # Вертикальный градиент
        for y in range(height):
            t = y / (height - 1) if height > 1 else 0
            
            if interpolation == "linear_rgb":
                # Конвертируем в linear RGB
                start_linear = srgb_to_linear(np.array(start_rgb))
                end_linear = srgb_to_linear(np.array(end_rgb))
                
                # Интерполяция в linear пространстве
                color_linear = start_linear * (1 - t) + end_linear * t
                
                # Конвертируем обратно в sRGB
                color_srgb = linear_to_srgb(color_linear)
                gradient[y, :] = color_srgb
            else:
                # Простая интерполяция в sRGB
                color = np.array(start_rgb) * (1 - t) + np.array(end_rgb) * t
                gradient[y, :] = color
    
    elif direction == "horizontal":
        # Горизонтальный градиент
        for x in range(width):
            t = x / (width - 1) if width > 1 else 0
            
            if interpolation == "linear_rgb":
                start_linear = srgb_to_linear(np.array(start_rgb))
                end_linear = srgb_to_linear(np.array(end_rgb))
                color_linear = start_linear * (1 - t) + end_linear * t
                color_srgb = linear_to_srgb(color_linear)
                gradient[:, x] = color_srgb
            else:
                color = np.array(start_rgb) * (1 - t) + np.array(end_rgb) * t
                gradient[:, x] = color
    
    else:
        raise ValueError(f"Unknown direction: {direction}")
    
    # Конвертируем в uint8 и создаём PIL Image
    gradient_uint8 = gradient.astype(np.uint8)
    return Image.fromarray(gradient_uint8, "RGB")




