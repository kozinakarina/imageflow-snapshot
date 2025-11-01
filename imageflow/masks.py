"""Обработка масок: рост и размытие."""
import numpy as np
import cv2


def grow_mask(mask: np.ndarray, grow_pixels: int = 7) -> np.ndarray:
    """
    Расширить маску (дилатация).
    
    Args:
        mask: numpy array (H, W) с значениями 0-255
        grow_pixels: Количество пикселей для расширения
        
    Returns:
        Расширенная маска (H, W, 0-255)
    """
    kernel = np.ones((grow_pixels * 2 + 1, grow_pixels * 2 + 1), np.uint8)
    dilated = cv2.dilate(mask, kernel, iterations=1)
    return dilated


def blur_mask(mask: np.ndarray, blur_size: int = 5) -> np.ndarray:
    """
    Размыть маску (Gaussian blur).
    
    Args:
        mask: numpy array (H, W) с значениями 0-255
        blur_size: Размер ядра размытия (должен быть нечётным)
        
    Returns:
        Размытая маска (H, W, 0-255)
    """
    if blur_size % 2 == 0:
        blur_size += 1
    
    blurred = cv2.GaussianBlur(mask, (blur_size, blur_size), 0)
    return blurred


def grow_mask_and_blur(mask: np.ndarray, grow_pixels: int = 7, blur_size: int = 0) -> np.ndarray:
    """
    Комбинированная операция: расширение + размытие маски.
    
    Args:
        mask: numpy array (H, W) с значениями 0-255
        grow_pixels: Количество пикселей для расширения
        blur_size: Размер ядра размытия
        
    Returns:
        Обработанная маска (H, W, 0-255)
    """
    grown = grow_mask(mask, grow_pixels)
    blurred = blur_mask(grown, blur_size)
    return blurred


def invert_mask(mask: np.ndarray) -> np.ndarray:
    """
    Инвертировать маску (белое -> чёрное, чёрное -> белое).
    
    Args:
        mask: numpy array (H, W) с значениями 0-255
        
    Returns:
        Инвертированная маска (H, W, 0-255)
    """
    return 255 - mask


