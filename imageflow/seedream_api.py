"""Интеграция с Seedream (Fal AI) API для очистки изображений."""
import time
import requests
from PIL import Image
from typing import Optional
from .utils import fetch_image
from .retry_utils import safe_request


def run_seedream(
    image_url: str,
    prompt: str,
    api_key: str,
    size: str = "square_hd",
    seed: int = 2069714305,
    timeout: int = 300,
    max_retries: int = 2
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
        max_retries: Максимальное количество попыток при ошибках
        
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
    
    # Повторные попытки для создания задачи
    last_exception = None
    for attempt in range(max_retries):
        try:
            print(f"[Seedream] Отправка запроса для очистки изображения (попытка {attempt + 1}/{max_retries})...", flush=True)
            response = safe_request("POST", endpoint, json=payload, headers=headers, max_retries=2, timeout=60)
            
            result = response.json()
            status_url = result.get("status_url")
            if not status_url:
                raise RuntimeError("Seedream не вернул status_url")
            
            print(f"[Seedream] Получен status_url, начинаем опрос...", flush=True)
            break
            
        except (requests.RequestException, requests.Timeout) as e:
            last_exception = e
            if attempt < max_retries - 1:
                print(f"[Seedream] Ошибка при создании задачи, повтор через 2 секунды...", flush=True)
                time.sleep(2)
            else:
                raise RuntimeError(f"Не удалось создать задачу Seedream после {max_retries} попыток: {e}") from e
    
    # Опрос статуса с retry для запросов статуса
    start_time = time.time()
    poll_count = 0
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        if time.time() - start_time > timeout:
            raise RuntimeError(f"Seedream timeout после {timeout} секунд")
        
        try:
            poll_count += 1
            status_response = safe_request("GET", status_url, headers=headers, max_retries=2, timeout=30)
            status_data = status_response.json()
            consecutive_errors = 0  # Сбрасываем счетчик ошибок при успехе
            
        except (requests.RequestException, requests.Timeout) as e:
            consecutive_errors += 1
            if consecutive_errors >= max_consecutive_errors:
                raise RuntimeError(f"Слишком много ошибок подряд при опросе статуса Seedream: {e}") from e
            
            print(f"[Seedream] Ошибка при опросе статуса ({consecutive_errors}/{max_consecutive_errors}), повтор через 3 секунды...", flush=True)
            time.sleep(3)
            continue
        
        status = status_data.get("status")
        
        if status == "COMPLETED":
            print(f"[Seedream] Задача завершена за {poll_count} опросов")
            response_url = status_data.get("response_url")
            if not response_url:
                raise RuntimeError("Seedream не вернул response_url")
            
            # Получаем результат с retry
            try:
                result_response = safe_request("GET", response_url, headers=headers, max_retries=3, timeout=60)
                result_data = result_response.json()
            except requests.exceptions.HTTPError as e:
                # Проверяем статус ошибки
                if e.response.status_code == 422:
                    # 422 Unprocessable Entity - Seedream не может обработать это изображение
                    error_msg = f"Seedream не может обработать изображение (422): {e.response.text[:200] if hasattr(e.response, 'text') else str(e)}"
                    print(f"[Seedream] {error_msg}", flush=True)
                    raise RuntimeError(error_msg) from e
                else:
                    raise RuntimeError(f"Ошибка при получении результата Seedream: {e}") from e
            except requests.RequestException as e:
                raise RuntimeError(f"Ошибка при получении результата Seedream: {e}") from e
            
            images = result_data.get("images", [])
            if not images:
                raise RuntimeError("Seedream не вернул изображений")
            
            image_url_result = images[0].get("url")
            if not image_url_result:
                raise RuntimeError("Seedream не вернул URL изображения")
            
            print(f"[Seedream] Скачивание результата...")
            return fetch_image(image_url_result)
        
        elif status == "FAILED":
            error_msg = status_data.get("error", "Unknown error")
            raise RuntimeError(f"Seedream job failed: {error_msg}")
        
        elif status in ("IN_QUEUE", "IN_PROGRESS"):
            print(f"[Seedream] Статус: {status}, опрос #{poll_count}...")
            time.sleep(3)
        else:
            raise RuntimeError(f"Неизвестный статус Seedream: {status}")
