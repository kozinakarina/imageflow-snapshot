"""Основной пайплайн обработки изображений."""
import time
import requests
import cv2
import numpy as np
from PIL import Image
from .seedream_api import run_seedream
from .rmbg import remove_background
from .masks import grow_mask_and_blur, invert_mask
from .inpaint import inpaint_pil_image
from .colors import extract_main_colors, colors_to_hex
from .colors_simple import extract_corner_colors
from .gradient import create_gradient_background
from .compose import composite_images
from .textdraw import add_watermark, add_centered_text
from .utils import split_game_title


def full_pipeline(
    image_url: str,
    game_title: str,
    provider: str,
    fal_api_key: str,
    seed: int = 2069714305
) -> Image.Image:
    """
    Полный пайплайн обработки изображения по ComfyUI workflow.
    
    Args:
        image_url: URL исходного изображения
        game_title: Название игры (верхний текст)
        provider: Провайдер (нижний текст)
        fal_api_key: FAL API ключ для Seedream
        seed: Фиксированный seed для Seedream
        
    Returns:
        Финальное обработанное изображение (PIL Image)
    """
    print("[Pipeline] Начало обработки...", flush=True)
    start_time = time.time()
    
    # Шаг 0: Загрузка изображения (для Seedream)
    print("[Pipeline] Шаг 0: Загрузка исходного изображения...", flush=True)
    import sys
    sys.stdout.flush()
    
    from .utils import fetch_image
    try:
        original_image = fetch_image(image_url)
    except Exception as e:
        print(f"[Pipeline] ОШИБКА загрузки изображения: {type(e).__name__}: {e}", flush=True)
        sys.stdout.flush()
        raise
    
    if original_image.mode != "RGB":
        original_image = original_image.convert("RGB")
    
    # Resize для Seedream (как в JSON: ImageResize+ 512x512)
    if original_image.size != (512, 512):
        original_image = original_image.resize((512, 512), Image.Resampling.NEAREST)
    print(f"[Pipeline] Исходное изображение подготовлено: {original_image.size}", flush=True)
    
    # Шаг 1: Seedream очистка
    print("[Pipeline] Шаг 1: Seedream очистка...", flush=True)
    seedream_start = time.time()
    seedream_prompt = "Remove signatures and text from this image, as well as frames and labels. Place the foreground in the center of the image."
    cleaned_image = run_seedream(image_url, seedream_prompt, fal_api_key, "square_hd", seed)
    print(f"[Pipeline] Seedream завершён за {time.time() - seedream_start:.2f}с", flush=True)
    print(f"[Pipeline] Seedream результат: {cleaned_image.size} {cleaned_image.mode}", flush=True)
    
    # Ресайз очищенного изображения до 1024x1024 (nearest-exact как в ComfyUI)
    if cleaned_image.size != (1024, 1024):
        cleaned_image = cleaned_image.resize((1024, 1024), Image.Resampling.NEAREST)
        print(f"[Pipeline] Resized to: {cleaned_image.size}", flush=True)
    
    # Конвертируем в RGB (Images to RGB в ComfyUI)
    if cleaned_image.mode != "RGB":
        cleaned_image = cleaned_image.convert("RGB")
        print(f"[Pipeline] Converted to RGB: {cleaned_image.mode}", flush=True)
    
    # Шаг 2: Удаление фона (RMBG)
    print("[Pipeline] Шаг 2: Удаление фона...", flush=True)
    rmbg_start = time.time()
    try:
        foreground_rgba, alpha_mask = remove_background(cleaned_image, model="u2net")
        print(f"[Pipeline] Удаление фона завершено за {time.time() - rmbg_start:.2f}с", flush=True)
    except Exception as e:
        import traceback
        print(f"[ERROR] Ошибка удаления фона: {e}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise
    
    # Шаг 3: Инверсия маски и обработка (grow + blur)
    print("[Pipeline] Шаг 3: Обработка маски...", flush=True)
    mask_start = time.time()
    inverted_mask = invert_mask(alpha_mask)
    processed_mask = grow_mask_and_blur(inverted_mask, grow_pixels=7, blur_size=5)
    print(f"[Pipeline] Обработка маски завершена за {time.time() - mask_start:.2f}с", flush=True)
    
    # Шаг 4: Инпейнтинг БЕЗ blur (blur применим только к фону!)
    print("[Pipeline] Шаг 4: Инпейнтинг...", flush=True)
    inpaint_start = time.time()
    inpainted_image = inpaint_pil_image(
        cleaned_image.convert("RGB"),
        processed_mask,
        method=cv2.INPAINT_TELEA,
        inpaint_radius=64,
        blur_after=0  # НЕ блюрим здесь - блюрим только фон позже!
    )
    print(f"[Pipeline] Инпейнтинг завершён за {time.time() - inpaint_start:.2f}с")
    
    # ========================================================================
    # РАЗДЕЛЕНИЕ НА ДВЕ ВЕТКИ: ФОН И ПЕРСОНАЖ
    # ========================================================================
    
    # ВЕТКА ФОНА: inpainted_image → masked blur → извлечение цветов → градиент → маска-переход → background_with_gradient
    
    # Шаг 4.5: фон после инпейнта + masked blur по маске фона
    print("[Pipeline] Шаг 4.5: Masked blur фона (processed_mask: белое=фон, flush=True)...")
    colors_start = time.time()
    
    # === фон после инпейнта + masked blur по маске фона ===
    bg_arr = np.array(inpainted_image)  # RGB, HxWx3
    m = np.array(processed_mask).astype(np.float32) / 255.0  # 1=фон (processed_mask из grow+blur)
    bg_blurred = cv2.GaussianBlur(bg_arr, (11, 11), 0)       # мягкий фон
    bg_only = (bg_arr * (1 - m[..., None]) + bg_blurred * m[..., None]).astype(np.uint8)
    bg_image = Image.fromarray(bg_only, "RGB")
    print(f"[Pipeline] Masked blur фона применен (processed_mask: белое=фон, flush=True)")
    
    # === извлекаем цвета ТОЛЬКО из фона ===
    print("[Pipeline] Шаг 5: Извлечение цветов строго из фона...", flush=True)
    dominant_colors = extract_main_colors(
        bg_image,
        num_colors=2,
        random_state=42,
        algorithm="elkan",
        mask=processed_mask  # белое=фон
    )
    color_hexes = colors_to_hex(dominant_colors)
    print(f"[Pipeline] Доминантные цвета из фона: {color_hexes}, за {time.time() - colors_start:.2f}с")
    
    # Шаг 6: Canvas 1024x1280: фон + нижняя панель
    print("[Pipeline] Шаг 6: Создание canvas с фоном и панелью...", flush=True)
    color_panel = Image.new("RGB", (1024, 256), color_hexes[0])
    bg_with_panel = Image.new("RGB", (1024, 1280))
    bg_with_panel.paste(bg_image, (0, 0))
    bg_with_panel.paste(color_panel, (0, 1024))
    print(f"[Pipeline] Canvas создан: {bg_with_panel.size}", flush=True)
    
    # Шаг 7: Foreground (персонаж) кладём НА ФОН до градиента
    print("[Pipeline] Шаг 7: Композиция персонажа на фон...", flush=True)
    compose_start = time.time()
    fg_rgba = foreground_rgba
    if fg_rgba.size != (1024, 1024):
        fg_rgba = fg_rgba.resize((1024, 1024), Image.Resampling.LANCZOS)
    
    alpha_a = alpha_mask
    if alpha_a.shape[:2] != (1024, 1024):
        # Конвертируем в PIL для resize
        alpha_pil = Image.fromarray(alpha_a, mode="L")
        alpha_pil = alpha_pil.resize((1024, 1024), Image.Resampling.BILINEAR)
        alpha_a = np.array(alpha_pil)
    
    base_rgba = bg_with_panel.convert("RGBA")
    base_rgba.paste(fg_rgba, (0, 0), Image.fromarray(alpha_a, mode="L"))  # персонаж уже подложен
    print(f"[Pipeline] Персонаж наложен на фон за {time.time() - compose_start:.2f}с")
    
    # Шаг 8: Создание двух градиентов
    print("[Pipeline] Шаг 8: Создание градиентов...", flush=True)
    gradient_start = time.time()
    # Градиент 1: 1024x768 (color_1 → color_1, одинаковый цвет!)
    gradient_top = create_gradient_background(
        1024, 768,
        color_hexes[0], color_hexes[0],  # Одинаковые цвета!
        direction="vertical",
        interpolation="linear_rgb"
    )
    # Градиент 2: 1024x512 (color_1 → color_2)
    gradient_bottom = create_gradient_background(
        1024, 512,
        color_hexes[0],
        color_hexes[1] if len(color_hexes) > 1 else color_hexes[0],
        direction="vertical",
        interpolation="linear_rgb"
    )
    # Склеиваем градиенты вертикально → 1024x1280
    full_gradient = Image.new("RGB", (1024, 1280))
    full_gradient.paste(gradient_top, (0, 0))
    full_gradient.paste(gradient_bottom, (0, 768))
    print(f"[Pipeline] Градиенты созданы за {time.time() - gradient_start:.2f}с, размер: {full_gradient.size}")
    
    # Шаг 9: Расплывчатый градиент сверху на всё изображение
    print("[Pipeline] Шаг 9: Создание расплывчатой маски градиента...", flush=True)
    # маска: 0 = показываем базу (фон+персонаж), 255 = показываем градиент
    mask = np.zeros((1280, 1024), dtype=np.uint8)
    transition_start = 360  # Поднято выше (было 460)
    transition_end = 960    # Расширена зона перехода (было 860)
    
    for y in range(1280):
        if y < transition_start:
            mask[y, :] = 0
        elif y > transition_end:
            mask[y, :] = 255
        else:
            t = (y - transition_start) / (transition_end - transition_start)
            mask[y, :] = int(t * 255)
    
    # СИЛЬНО размягчаем именно маску для максимально плавной границы
    from .masks import blur_mask
    mask = blur_mask(mask, blur_size=300)  # Увеличено с 220 до 300 для более плавного перехода
    gradient_mask = Image.fromarray(mask, "L")
    print(f"[Pipeline] Расплывчатая маска создана: Y 0-{transition_start}=база, {transition_start}-{transition_end}=переход, {transition_end}-1280=градиент", flush=True)
    
    # Шаг 10: Наложение расплывчатого градиента (вуаль поверх базы)
    print("[Pipeline] Шаг 10: Наложение расплывчатого градиента...", flush=True)
    gradient_start = time.time()
    # слегка размываем сам градиент (не фон)
    grad_rgba = full_gradient.convert("RGBA")
    grad_array = np.array(grad_rgba)
    grad_blurred = cv2.GaussianBlur(grad_array, (31, 31), 0)
    grad_rgba = Image.fromarray(grad_blurred.astype(np.uint8), "RGBA")
    
    # вуаль поверх базы
    grad_rgba.putalpha(gradient_mask)
    result_with_gradient = Image.alpha_composite(base_rgba, grad_rgba).convert("RGB")
    print(f"[Pipeline] Расплывчатый градиент наложен за {time.time() - gradient_start:.2f}с")
    
    result = result_with_gradient
    
    # Шаг 12: Resize до 512x640 (КАК В JSON - ДО текстов!)
    print("[Pipeline] Шаг 12: Resize до 512x640...", flush=True)
    resize_start = time.time()
    result_resized = result.resize((512, 640), Image.Resampling.LANCZOS)
    print(f"[Pipeline] Resize завершен за {time.time() - resize_start:.2f}с, размер: {result_resized.size}")
    
    # Шаг 13: Добавление текстов с правильными отступами
    print("[Pipeline] Шаг 13: Добавление текстов...", flush=True)
    text_start = time.time()
    # Конвертируем для добавления текста
    result_for_text = result_resized.convert("RGB")
    
    # Получаем размеры для расчета позиций
    img_width, img_height = result_for_text.size  # 512 x 640
    
    # Фиксированные размеры шрифтов
    game_font_size = 50   # Размер текста игры
    provider_font_size = 18  # Размер текста провайдера
    
    # Вычисляем высоты текстов для правильного позиционирования
    # Примерные высоты текстов (приблизительно 1.2x от размера шрифта)
    game_text_height = int(game_font_size * 1.2)
    provider_text_height = int(provider_font_size * 1.2)
    
    # Позиционирование: оба текста 50px от низа (центр текста)
    # Провайдер: центр текста на 50px от низа
    provider_y = img_height - 50  # 50px от низа (центр текста)
    
    # Игра: расстояние между текстами - 34 пикселя между центрами
    game_y = provider_y - 34  # 34px расстояние между центрами текстов
    
    # Контейнер игры: ограничен 100px от краев изображения
    # Ширина контейнера = img_width - 200 (100px с каждой стороны)
    max_game_width = img_width - 200  # 100px отступы слева и справа
    
    # Обрабатываем название игры: добавляем пробелы для читаемости
    processed_game_title = split_game_title(game_title)
    print(f"[Pipeline] Название игры обработано: '{game_title}' -> '{processed_game_title}'", flush=True)
    
    # Текст 1: game_title - 50px, жирный шрифт Inter Bold, центрирован по X
    result_with_text = add_centered_text(
        result_for_text,
        processed_game_title,  # Используем обработанное название с пробелами
        y_position=game_y,
        font_size=game_font_size,
        color="#FFFFFF",
        font_name="/usr/share/fonts/truetype/inter/Inter-Bold.ttf",
        opacity=1.0,
        bold=False,  # Шрифт уже жирный
        max_width=max_game_width  # Ограничение контейнера
    )
    
    # Текст 2: provider - 18px, обычный шрифт Inter Regular, центрирован по X, ниже первого текста
    result = add_centered_text(
        result_with_text,
        provider,
        y_position=provider_y,
        font_size=provider_font_size,
        color="#FFFFFF",
        font_name="/usr/share/fonts/truetype/inter/Inter-Regular.ttf",
        opacity=1.0
    )
    print(f"[Pipeline] Тексты добавлены: игра Y={game_y} (60px, flush=True), провайдер Y={provider_y} (40px), за {time.time() - text_start:.2f}с")
    
    total_time = time.time() - start_time
    print(f"[Pipeline] Обработка завершена за {total_time:.2f}с", flush=True)
    
    return result

