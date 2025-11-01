"""Интеграция с Seedream (Fal AI) API для очистки изображений."""
import time
import requests
from PIL import Image
from typing import Optional
from .utils import fetch_image


def run_seedream(
    image_url: str,
    prompt: str,
    api_key: str,
    size: str = "square_hd",
    seed: int = 2069714305,
    timeout: int = 300
) -> Image.Image:
    """
    Вызвать Seedream API для очистки изображения.
    
    Args:
        image_url: URL исходного изображения
        prompt: Промпт для очистки
        api_key: FAL API ключ
        size: Размер выходного изображения (square_hd = 2048x2048)
        seed: Фиксированный seed для детерминизма
        timeout: Таймаут в секундах
        
    Returns:
        PIL Image очищенного изображения
        
    Raises:
        RuntimeError: Если задача завершилась с ошибкой
        requests.RequestException: При ошибках HTTP запросов
    """
    endpoint = "https://queue.fal.run/fal-ai/bytedance/seedream/v4/edit"
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "image_size": size,
        "image_urls": [image_url],
        "seed": seed
    }
    
    print(f"[Seedream] Отправка запроса для очистки изображения...")
    response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    
    result = response.json()
    status_url = result.get("status_url")
    if not status_url:
        raise RuntimeError("Seedream не вернул status_url")
    
    print(f"[Seedream] Получен status_url, начинаем опрос...")
    
    # Опрос статуса
    start_time = time.time()
    poll_count = 0
    
    while True:
        if time.time() - start_time > timeout:
            raise RuntimeError(f"Seedream timeout после {timeout} секунд")
        
        poll_count += 1
        status_response = requests.get(status_url, headers=headers, timeout=30)
        status_response.raise_for_status()
        status_data = status_response.json()
        
        status = status_data.get("status")
        
        if status == "COMPLETED":
            print(f"[Seedream] Задача завершена за {poll_count} опросов")
            response_url = status_data.get("response_url")
            if not response_url:
                raise RuntimeError("Seedream не вернул response_url")
            
            # Получаем результат
            result_response = requests.get(response_url, headers=headers, timeout=60)
            result_response.raise_for_status()
            result_data = result_response.json()
            
            images = result_data.get("images", [])
            if not images:
                raise RuntimeError("Seedream не вернул изображений")
            
            image_url = images[0].get("url")
            if not image_url:
                raise RuntimeError("Seedream не вернул URL изображения")
            
            print(f"[Seedream] Скачивание результата...")
            return fetch_image(image_url)
        
        elif status == "FAILED":
            error_msg = status_data.get("error", "Unknown error")
            raise RuntimeError(f"Seedream job failed: {error_msg}")
        
        elif status in ("IN_QUEUE", "IN_PROGRESS"):
            print(f"[Seedream] Статус: {status}, опрос #{poll_count}...")
            time.sleep(3)
        else:
            raise RuntimeError(f"Неизвестный статус Seedream: {status}")




