"""Добавление текстовых оверлеев."""
import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, List


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


def add_centered_multiline_text(
    image: Image.Image,
    text: str,
    bottom_y_position: int,  # Позиция нижней строки (центр строки)
    font_size: int = 48,
    color: str = "#FFFFFF",
    font_name: Optional[str] = None,
    opacity: float = 1.0,
    max_width: Optional[int] = None,
    min_font_size: int = 30,
    line_spacing: float = 1.2
) -> Image.Image:
    """
    Добавить центрированный многострочный текст с фиксированной нижней границей.
    
    Args:
        image: PIL Image для добавления текста
        text: Текст для добавления
        bottom_y_position: Y координата нижней строки (центр строки) - фиксированная позиция
        font_size: Начальный размер шрифта
        color: Цвет текста в hex формате
        font_name: Имя файла шрифта
        opacity: Прозрачность текста (0.0 - 1.0)
        max_width: Максимальная ширина контейнера
        min_font_size: Минимальный размер шрифта (если меньше - переносим на новую строку)
        line_spacing: Множитель для межстрочного интервала (1.2 = 20% от высоты строки)
        
    Returns:
        PIL Image с добавленным текстом
    """
    # Определяем максимальную ширину для контейнера
    if max_width is None:
        container_width = image.width
    else:
        container_width = max_width
    
    # Разбиваем текст на строки
    lines, final_font_size = split_text_to_lines(text, container_width, font_name, font_size, min_font_size)
    
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
        font = find_font(font_name, final_font_size)
    else:
        font = ImageFont.load_default()
    
    # Вычисляем высоты всех строк
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
    
    # Вычисляем позиции строк снизу вверх
    # bottom_y_position - это центр нижней строки
    x_position = image.width // 2  # Центр изображения
    
    # Конвертируем цвет в RGBA с учётом opacity
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    rgba = (*rgb, int(255 * opacity))
    
    # Рисуем строки снизу вверх, начиная с нижней строки
    current_y = bottom_y_position  # Центр нижней строки
    
    for i in range(len(lines) - 1, -1, -1):  # Идем от последней строки к первой
        line = lines[i]
        line_height = line_heights[i]
        
        # Центрируем строку по Y относительно её высоты
        line_y = current_y - line_height // 2
        
        draw.text(
            (x_position, line_y),
            line,
            font=font,
            fill=rgba,
            anchor="mm"  # middle-middle: текст центрирован по X и Y
        )
        
        # Переходим к следующей строке выше (если есть)
        if i > 0:
            # Поднимаемся на высоту текущей строки + межстрочный интервал
            spacing = int(line_height * (line_spacing - 1.0))
            current_y = current_y - line_height - spacing
    
    # Композит текстового слоя на изображение
    result = Image.alpha_composite(result, text_layer)
    
    # Конвертируем обратно в RGB
    return result.convert("RGB")


def split_text_to_lines(
    text: str,
    max_width: int,
    font_name: Optional[str],
    font_size: int,
    min_font_size: int = 30
) -> Tuple[List[str], int]:
    """
    Разбить текст на строки, если он не помещается с минимальным размером шрифта.
    
    Args:
        text: Текст для разбиения
        max_width: Максимальная ширина контейнера
        font_name: Имя файла шрифта
        font_size: Начальный размер шрифта
        min_font_size: Минимальный размер шрифта (если меньше - переносим на новую строку)
        
    Returns:
        Tuple[list[str], int]: (список строк, финальный размер шрифта)
    """
    # Создаем временный ImageDraw для измерения
    temp_img = Image.new("RGB", (1000, 1000))
    temp_draw = ImageDraw.Draw(temp_img)
    
    # Проверяем, помещается ли текст с минимальным размером
    if font_name:
        min_font = find_font(font_name, min_font_size)
    else:
        min_font = ImageFont.load_default()
    
    # Разбиваем текст на слова
    words = text.split()
    
    # Проверяем, помещается ли весь текст с минимальным размером
    full_text_width = temp_draw.textbbox((0, 0), text, font=min_font)[2] - temp_draw.textbbox((0, 0), text, font=min_font)[0]
    
    # Если помещается с минимальным размером, возвращаем как есть
    if full_text_width <= max_width:
        # Подбираем оптимальный размер шрифта
        optimal_size = find_fit_font_size(text, max_width, font_name, initial_size=font_size, min_size=min_font_size)
        return [text], optimal_size
    
    # Если не помещается, разбиваем на строки
    lines = []
    current_line = []
    
    for word in words:
        # Проверяем ширину слова с пробелом
        test_line = ' '.join(current_line + [word]) if current_line else word
        bbox = temp_draw.textbbox((0, 0), test_line, font=min_font)
        word_width = bbox[2] - bbox[0]
        
        if word_width <= max_width:
            current_line.append(word)
        else:
            # Сохраняем текущую строку и начинаем новую
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    # Добавляем последнюю строку
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines, min_font_size


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


