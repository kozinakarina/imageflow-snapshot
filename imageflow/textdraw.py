"""Добавление текстовых оверлеев."""
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple


def find_font(font_name: str, fallback_size: int = 100) -> ImageFont.FreeTypeFont:
    """
    Найти шрифт или использовать fallback.
    
    Args:
        font_name: Имя файла шрифта (например, "blackrumbleregular.ttf")
        fallback_size: Размер для fallback шрифта
        
    Returns:
        ImageFont объект
    """
    # Возможные пути к шрифтам
    font_paths = [
        font_name,  # Текущая директория
        f"/usr/share/fonts/truetype/{font_name}",
        f"/usr/share/fonts/{font_name}",
        f"./fonts/{font_name}",
        f"fonts/{font_name}",
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, fallback_size)
            except Exception:
                continue
    
    # Fallback на встроенный шрифт
    try:
        return ImageFont.truetype("arial.ttf", fallback_size)
    except:
        return ImageFont.load_default()


def add_text_overlay(
    image: Image.Image,
    text: str,
    position: Tuple[int, int],
    font_size: int = 100,
    color: str = "#FFFFFF",
    font_name: Optional[str] = "blackrumbleregular.ttf",
    opacity: float = 1.0
) -> Image.Image:
    """
    Добавить текстовый оверлей на изображение.
    
    Args:
        image: PIL Image для модификации
        text: Текст для отображения
        position: (x, y) позиция текста
        font_size: Размер шрифта
        color: Цвет текста (hex)
        font_name: Имя файла шрифта или None для default
        opacity: Прозрачность (0.0-1.0)
        
    Returns:
        Изображение с добавленным текстом
    """
    # Создаём копию изображения
    result = image.copy()
    
    # Конвертируем в RGBA для работы с прозрачностью
    if result.mode != "RGBA":
        result = result.convert("RGBA")
    
    # Создаём отдельный слой для текста
    text_layer = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    
    # Загружаем шрифт
    if font_name:
        font = find_font(font_name, font_size)
    else:
        font = ImageFont.load_default()
    
    # Получаем размеры текста
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Конвертируем цвет в RGBA с учётом opacity
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    rgba = (*rgb, int(255 * opacity))
    
    # Рисуем текст
    x, y = position
    draw.text((x, y), text, font=font, fill=rgba)
    
    # Композит текстового слоя на изображение
    result = Image.alpha_composite(result, text_layer)
    
    # Конвертируем обратно в RGB
    return result.convert("RGB")


def find_fit_font_size(
    text: str,
    max_width: int,
    font_name: Optional[str],
    initial_size: int = 100,
    min_size: int = 10
) -> int:
    """
    Найти максимальный размер шрифта, при котором текст помещается в заданную ширину.
    
    Args:
        text: Текст для измерения
        max_width: Максимальная ширина в пикселях
        font_name: Имя файла шрифта
        initial_size: Начальный размер шрифта для поиска
        min_size: Минимальный размер шрифта
        
    Returns:
        Оптимальный размер шрифта
    """
    # Создаем временный ImageDraw для измерения
    temp_img = Image.new("RGB", (100, 100))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Используем бинарный поиск для нахождения оптимального размера
    low = min_size
    high = initial_size
    best_size = min_size
    
    while low <= high:
        mid = (low + high) // 2
        try:
            if font_name:
                font = find_font(font_name, mid)
            else:
                font = ImageFont.load_default()
            
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width * 0.95:  # Оставляем небольшой запас (95%)
                best_size = mid
                low = mid + 1
            else:
                high = mid - 1
        except Exception:
            high = mid - 1
    
    return best_size


def add_centered_text(
    image: Image.Image,
    text: str,
    y_position: int,
    font_size: int = 48,
    color: str = "#FFFFFF",
    font_name: Optional[str] = "blackrumbleregular.ttf",
    opacity: float = 1.0,
    bold: bool = False,
    auto_fit: bool = False,
    max_width: Optional[int] = None
) -> Image.Image:
    """
    Добавить центрированный текст на изображение.
    
    Args:
        image: PIL Image для добавления текста
        text: Текст для добавления
        y_position: Y координата центра текста
        font_size: Размер шрифта
        color: Цвет текста в hex формате
        font_name: Имя файла шрифта
        opacity: Прозрачность текста (0.0 - 1.0)
        bold: Если True, текст будет жирным (используется stroke)
        auto_fit: Если True, автоматически подгоняет размер шрифта под ширину изображения
        
    Returns:
        PIL Image с добавленным текстом
    """
    # Определяем максимальную ширину для контейнера
    if max_width is None:
        container_width = image.width
    else:
        container_width = max_width
    
    # Автоматически подгоняем размер шрифта под ширину контейнера
    if auto_fit:
        max_text_width = int(container_width * 0.95)  # 95% ширины контейнера для запаса
        font_size = find_fit_font_size(text, max_text_width, font_name, initial_size=font_size)
    
    # Создаем копию изображения
    result = image.copy()
    
    # Конвертируем в RGBA для работы с прозрачностью
    if result.mode != "RGBA":
        result = result.convert("RGBA")
    
    # Создаём отдельный слой для текста
    text_layer = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    
    # Загружаем шрифт
    if font_name:
        font = find_font(font_name, font_size)
    else:
        font = ImageFont.load_default()
    
    # Получаем размеры текста
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Проверяем, не превышает ли текст максимальную ширину контейнера
    if text_width > container_width:
        # Если текст шире контейнера, уменьшаем размер шрифта
        scale_factor = container_width / text_width
        font_size = int(font_size * scale_factor * 0.95)  # 95% для запаса
        if font_name:
            font = find_font(font_name, font_size)
        else:
            font = ImageFont.load_default()
        # Пересчитываем размеры
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    
    # ТОЧНОЕ центрирование по X и Y
    x_position = image.width // 2  # Центр изображения
    text_y = y_position  # Используем y_position как baseline
    
    # Конвертируем цвет в RGBA с учётом opacity
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    rgba = (*rgb, int(255 * opacity))
    
    # Рисуем текст БЕЗ обводки (stroke_width=0)
    draw.text(
        (x_position, text_y), 
        text, 
        font=font, 
        fill=rgba,
        anchor="mm"  # middle-middle: текст центрирован по X и Y
    )
    
    # Композит текстового слоя на изображение
    result = Image.alpha_composite(result, text_layer)
    
    # Конвертируем обратно в RGB
    return result.convert("RGB")


def add_watermark(
    image: Image.Image,
    text: str,
    x_offset: int,
    y_offset: int,
    font_size: int,
    color: str = "#FFFFFF",
    font_name: Optional[str] = "blackrumbleregular.ttf",
    opacity: float = 1.0
) -> Image.Image:
    """
    Удобная обёртка для добавления водяного знака (совместимость с ComfyUI workflow).
    
    Args:
        image: PIL Image
        text: Текст
        x_offset: Смещение по X
        y_offset: Смещение по Y
        font_size: Размер шрифта
        color: Цвет (hex)
        font_name: Имя шрифта
        opacity: Прозрачность
        
    Returns:
        Изображение с водяным знаком
    """
    return add_text_overlay(
        image,
        text,
        (x_offset, y_offset),
        font_size,
        color,
        font_name,
        opacity
    )


