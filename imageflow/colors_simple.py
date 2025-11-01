"""Простое извлечение цветов из углов изображения (где фон)"""
import numpy as np
from PIL import Image
from typing import List, Tuple


def extract_corner_colors(image: Image.Image, sample_size: int = 100) -> List[Tuple[int, int, int]]:
    """
    Извлечь цвета из углов изображения (там обычно фон).
    
    Args:
        image: PIL Image (RGB)
        sample_size: Размер области для сэмплирования в каждом углу
        
    Returns:
        Список RGB tuples - [самый_частый_цвет, второй_по_частоте]
    """
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    arr = np.array(image)
    h, w = arr.shape[:2]
    
    # Берем пиксели из всех 4 углов
    corners = []
    corners.append(arr[0:sample_size, 0:sample_size])  # Левый верхний
    corners.append(arr[0:sample_size, -sample_size:])  # Правый верхний
    corners.append(arr[-sample_size:, 0:sample_size])  # Левый нижний
    corners.append(arr[-sample_size:, -sample_size:])  # Правый нижний
    
    # Объединяем все угловые пиксели
    all_corner_pixels = np.concatenate([corner.reshape(-1, 3) for corner in corners], axis=0)
    
    # Применяем KMeans для нахождения 2 доминантных цветов
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=2, random_state=42, algorithm="elkan", n_init=10)
    kmeans.fit(all_corner_pixels)
    
    # Получаем цвета
    colors = kmeans.cluster_centers_.astype(int)
    
    # Сортируем по частоте
    labels = kmeans.labels_
    label_counts = np.bincount(labels)
    sorted_indices = np.argsort(label_counts)[::-1]
    sorted_colors = [tuple(colors[i]) for i in sorted_indices]
    
    print(f"[Colors] Извлечено из углов: {sorted_colors}")
    
    return sorted_colors


def colors_to_hex(colors: List[Tuple[int, int, int]]) -> List[str]:
    """Конвертировать список RGB tuples в hex строки."""
    return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in colors]



