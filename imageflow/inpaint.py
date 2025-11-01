"""Инпейнтинг с использованием OpenCV."""
import numpy as np
import cv2
from PIL import Image


def inpaint_image(
    image: np.ndarray,
    mask: np.ndarray,
    method: int = cv2.INPAINT_TELEA,
    inpaint_radius: int = 64,
    blur_after: int = 5
) -> np.ndarray:
    """
    Выполнить инпейнтинг по маске.
    
    Args:
        image: numpy array (H, W, 3) RGB изображение
        mask: numpy array (H, W) маска для инпейнтинга (белое = закрасить)
        method: Метод инпейнтинга (cv2.INPAINT_TELEA или cv2.INPAINT_NS)
        inpaint_radius: Радиус инпейнтинга
        blur_after: Размер размытия после инпейнтинга (0 = без размытия)
        
    Returns:
        Обработанное изображение (H, W, 3) RGB
    """
    import sys
    
    print(f"[inpaint_image] Начало инпейнтинга: image shape={image.shape}, mask shape={mask.shape}, radius={inpaint_radius}", flush=True)
    sys.stdout.flush()
    
    # Конвертируем маску в uint8 если нужно
    if mask.dtype != np.uint8:
        print(f"[inpaint_image] Конвертация маски из {mask.dtype} в uint8", flush=True)
        sys.stdout.flush()
        mask = mask.astype(np.uint8)
    
    # Проверяем размеры
    if image.shape[:2] != mask.shape[:2]:
        raise ValueError(f"Размеры изображения {image.shape[:2]} и маски {mask.shape[:2]} не совпадают")
    
    # Проверяем процент закрашиваемой области
    mask_pixels = np.sum(mask > 0)
    total_pixels = mask.shape[0] * mask.shape[1]
    mask_percent = (mask_pixels / total_pixels) * 100
    
    print(f"[inpaint_image] Маска: {mask_pixels}/{total_pixels} пикселей ({mask_percent:.1f}%)", flush=True)
    sys.stdout.flush()
    
    # Если маска слишком большая, оптимизируем процесс
    if mask_percent > 50:
        print(f"[inpaint_image] ВНИМАНИЕ: Маска очень большая ({mask_percent:.1f}%), применяем оптимизации", flush=True)
        sys.stdout.flush()
        
        # Для очень больших масок (>90%) уменьшаем радиус и используем более быстрый подход
        if mask_percent > 90:
            # Для маски 100%: уменьшаем радиус и используем более быстрое заполнение
            optimized_radius = min(inpaint_radius, 32)  # Максимум 32 вместо 64
            print(f"[inpaint_image] Оптимизация: уменьшен радиус с {inpaint_radius} до {optimized_radius}", flush=True)
            sys.stdout.flush()
            inpaint_radius = optimized_radius
            
            # Если маска почти 100%, можно сначала уменьшить размер для скорости
            # затем увеличить обратно (это намного быстрее)
            if mask_percent > 95:
                scale_factor = 0.5  # Уменьшаем до 50% размера
                h, w = image.shape[:2]
                small_h, small_w = int(h * scale_factor), int(w * scale_factor)
                
                print(f"[inpaint_image] Оптимизация: уменьшаем изображение до {small_w}x{small_h} для ускорения", flush=True)
                sys.stdout.flush()
                
                # Уменьшаем изображение и маску
                small_image = cv2.resize(image, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
                small_mask = cv2.resize(mask, (small_w, small_h), interpolation=cv2.INTER_NEAREST)
                
                # Инпейнтинг на уменьшенном изображении
                small_inpainted = cv2.inpaint(small_image, small_mask, inpaint_radius, method)
                
                # Увеличиваем обратно
                inpainted = cv2.resize(small_inpainted, (w, h), interpolation=cv2.INTER_LINEAR)
                
                print(f"[inpaint_image] Оптимизированный инпейнтинг завершен, результат увеличен до {w}x{h}", flush=True)
                sys.stdout.flush()
                
                # Размытие после инпейнтинга (если указано)
                if blur_after > 0:
                    if blur_after % 2 == 0:
                        blur_after += 1
                    print(f"[inpaint_image] Применение blur после инпейнтинга: {blur_after}x{blur_after}", flush=True)
                    sys.stdout.flush()
                    inpainted = cv2.GaussianBlur(inpainted, (blur_after, blur_after), 0)
                    print(f"[inpaint_image] Blur применен", flush=True)
                    sys.stdout.flush()
                
                return inpainted
    
    print(f"[inpaint_image] Запуск cv2.inpaint с методом {method}, radius={inpaint_radius}...", flush=True)
    sys.stdout.flush()
    
    # Инпейнтинг
    import time
    inpaint_start = time.time()
    
    # Дополнительная проверка: если маска все еще очень большая, но не 100%
    # уменьшаем радиус для ускорения
    if mask_percent > 80 and mask_percent <= 95:
        optimized_radius = min(inpaint_radius, 32)
        if optimized_radius < inpaint_radius:
            print(f"[inpaint_image] Оптимизация: уменьшен радиус с {inpaint_radius} до {optimized_radius} для ускорения", flush=True)
            sys.stdout.flush()
            inpaint_radius = optimized_radius
    
    inpainted = cv2.inpaint(image, mask, inpaint_radius, method)
    inpaint_time = time.time() - inpaint_start
    
    print(f"[inpaint_image] cv2.inpaint завершен за {inpaint_time:.2f}с, результат shape={inpainted.shape}", flush=True)
    sys.stdout.flush()
    
    # Размытие после инпейнтинга (если указано)
    if blur_after > 0:
        if blur_after % 2 == 0:
            blur_after += 1
        print(f"[inpaint_image] Применение blur после инпейнтинга: {blur_after}x{blur_after}", flush=True)
        sys.stdout.flush()
        inpainted = cv2.GaussianBlur(inpainted, (blur_after, blur_after), 0)
        print(f"[inpaint_image] Blur применен", flush=True)
        sys.stdout.flush()
    
    return inpainted


def inpaint_pil_image(
    pil_image: Image.Image,
    mask: np.ndarray,
    method: int = cv2.INPAINT_TELEA,
    inpaint_radius: int = 64,
    blur_after: int = 5
) -> Image.Image:
    """
    Инпейнтинг для PIL Image.
    
    Args:
        pil_image: PIL Image (RGB)
        mask: numpy array (H, W) маска
        method: Метод инпейнтинга
        inpaint_radius: Радиус инпейнтинга
        blur_after: Размер размытия после инпейнтинга
        
    Returns:
        PIL Image (RGB) после инпейнтинга
    """
    import sys
    
    print(f"[inpaint_pil_image] Начало: PIL image size={pil_image.size}, mask shape={mask.shape}", flush=True)
    sys.stdout.flush()
    
    # Конвертируем PIL в numpy
    img_array = np.array(pil_image.convert("RGB"))
    print(f"[inpaint_pil_image] Конвертировано в numpy: shape={img_array.shape}", flush=True)
    sys.stdout.flush()
    
    # Инпейнтинг
    result_array = inpaint_image(img_array, mask, method, inpaint_radius, blur_after)
    
    print(f"[inpaint_pil_image] Инпейнтинг завершен, конвертация обратно в PIL...", flush=True)
    sys.stdout.flush()
    
    # Конвертируем обратно в PIL
    result = Image.fromarray(result_array, "RGB")
    
    print(f"[inpaint_pil_image] Готово: результат size={result.size}", flush=True)
    sys.stdout.flush()
    
    return result



