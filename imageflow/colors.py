"""Извлечение доминантных цветов через KMeans."""
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
from typing import List, Tuple


def extract_main_colors(
    image: Image.Image,
    num_colors: int = 2,
    random_state: int = 42,
    algorithm: str = "elkan",
    mask: np.ndarray = None
) -> List[Tuple[int, int, int]]:
    """
    Извлечь доминантные цвета из изображения через KMeans.
    
    Args:
        image: PIL Image
        num_colors: Количество цветов для извлечения
        random_state: Фиксированный seed для детерминизма
        algorithm: Алгоритм KMeans ("elkan" или "lloyd")
        mask: Опциональная маска (numpy array H×W) - берутся только пиксели где mask > 0
        
    Returns:
        Список RGB tuples (r, g, b) отсортированных по частоте
    """
    # Конвертируем в RGB если нужно
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Преобразуем изображение в массив пикселей
    img_array = np.array(image)
    
    if mask is not None:
        # Используем маску - берем только нужные пиксели
        mask_bool = mask > 128  # Порог для альфа-маски
        pixels = img_array[mask_bool]
        print(f"[Colors] С маской: {len(pixels)} пикселей из {img_array.shape[0] * img_array.shape[1]}")
    else:
        pixels = img_array.reshape(-1, 3)
    
    # МИНИМАЛЬНАЯ фильтрация - убираем только совсем чёрные/белые (артефакты)
    brightness = pixels.mean(axis=1)
    valid_mask = (brightness > 10) & (brightness < 245)
    pixels = pixels[valid_mask]
    
    if len(pixels) < num_colors * 10:
        # Если слишком мало пикселей - берём все
        if mask is not None:
            pixels = img_array[mask > 128]
        else:
            pixels = img_array.reshape(-1, 3)
        print(f"[Colors] Используем все пиксели (после фильтрации осталось мало)")
    
    # Применяем KMeans
    kmeans = KMeans(
        n_clusters=num_colors,
        random_state=random_state,
        algorithm=algorithm,
        n_init=10
    )
    kmeans.fit(pixels)
    
    # Получаем центры кластеров (цвета)
    colors = kmeans.cluster_centers_.astype(int)
    
    # Сортируем по частоте (количество пикселей в кластере)
    labels = kmeans.labels_
    label_counts = np.bincount(labels)
    sorted_indices = np.argsort(label_counts)[::-1]  # От большего к меньшему
    
    sorted_colors = [tuple(colors[i]) for i in sorted_indices]
    
    return sorted_colors


def colors_to_hex(colors: List[Tuple[int, int, int]]) -> List[str]:
    """Конвертировать список RGB tuples в hex строки."""
    return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in colors]


