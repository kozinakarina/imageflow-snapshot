"""Удаление фона через rembg."""
import io
import numpy as np
from PIL import Image
from rembg import remove


def remove_background(image: Image.Image, model: str = "u2net") -> tuple[Image.Image, np.ndarray]:
    """
    Удалить фон из изображения используя rembg.
    
    Args:
        image: PIL Image (RGB или RGBA)
        model: Модель rembg для использования
        
    Returns:
        Tuple (foreground_image, mask)
        - foreground_image: RGBA изображение с прозрачным фоном
        - mask: numpy array (H, W) с значениями 0-255 (белый = объект)
    """
    # Конвертируем в RGB если нужно
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Удаляем фон - rembg принимает PIL Image напрямую
    from rembg import new_session
    session = new_session(model)
    foreground = remove(image, session=session)
    
    # Конвертируем в RGBA если нужно
    if foreground.mode != "RGBA":
        foreground = foreground.convert("RGBA")
    
    # Извлекаем альфа-канал как маску
    mask = np.array(foreground.split()[3])  # Альфа канал
    
    return foreground, mask


def extract_alpha_mask(image: Image.Image) -> np.ndarray:
    """
    Извлечь альфа-канал как маску.
    
    Args:
        image: PIL Image с альфа-каналом (RGBA)
        
    Returns:
        numpy array (H, W) с значениями 0-255
    """
    if image.mode != "RGBA":
        raise ValueError("Image must have alpha channel (RGBA mode)")
    
    alpha = np.array(image.split()[3])
    return alpha

