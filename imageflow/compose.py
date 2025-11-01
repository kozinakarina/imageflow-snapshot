"""Композиция изображений с альфа-каналами и масками."""
import numpy as np
from PIL import Image
from typing import Tuple, Optional


def composite_images(
    background: Image.Image,
    foreground: Image.Image,
    mask: np.ndarray,
    x_offset: int = 0,
    y_offset: int = 0
) -> Image.Image:
    """
    Наложить foreground на background используя маску.
    
    Args:
        background: Фоновое изображение (RGB)
        foreground: Переднее изображение (RGBA)
        mask: Маска (numpy array H x W, значения 0-255)
        x_offset: Смещение по X
        y_offset: Смещение по Y
        
    Returns:
        Композитное изображение (RGB)
    """
    # Конвертируем фон в RGBA
    if background.mode != "RGBA":
        background = background.convert("RGBA")
    
    # Конвертируем foreground в RGBA
    if foreground.mode != "RGBA":
        foreground = foreground.convert("RGBA")
    
    # Создаем копию фона
    result = background.copy()
    
    # Если размеры не совпадают, ресайзим foreground
    if foreground.size != background.size:
        foreground = foreground.resize(background.size, Image.Resampling.LANCZOS)
    
    # Конвертируем маску в PIL Image
    mask_pil = Image.fromarray(mask).convert("L")
    if mask_pil.size != background.size:
        mask_pil = mask_pil.resize(background.size, Image.Resampling.LANCZOS)
    
    # Используем маску для композиции
    result.paste(foreground, (x_offset, y_offset), mask_pil)
    
    return result


def apply_gradient_overlay(
    base_image: Image.Image,
    gradient: Image.Image,
    opacity: float = 0.7
) -> Image.Image:
    """
    Наложить градиент поверх изображения с заданной прозрачностью.
    
    Args:
        base_image: Базовое изображение
        gradient: Градиент для наложения
        opacity: Непрозрачность градиента (0.0 - 1.0)
        
    Returns:
        Композитное изображение с градиентом
    """
    # Конвертируем оба в RGBA
    if base_image.mode != "RGBA":
        base_image = base_image.convert("RGBA")
    
    if gradient.mode != "RGBA":
        gradient = gradient.convert("RGBA")
    
    # Ресайзим градиент если нужно
    if gradient.size != base_image.size:
        gradient = gradient.resize(base_image.size, Image.Resampling.LANCZOS)
    
    # Создаем копию градиента с заданной непрозрачностью
    gradient_array = np.array(gradient).astype(float)
    gradient_array[:, :, 3] = gradient_array[:, :, 3] * opacity  # Уменьшаем альфа-канал
    gradient_with_opacity = Image.fromarray(gradient_array.astype(np.uint8), mode='RGBA')
    
    # Композиция
    result = Image.alpha_composite(base_image, gradient_with_opacity)
    
    return result
