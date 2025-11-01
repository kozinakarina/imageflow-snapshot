"""Утилиты для повторных попыток и обработки ошибок."""
import time
import functools
from typing import Callable, TypeVar, Any
import requests

T = TypeVar('T')


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    log_errors: bool = True
):
    """
    Декоратор для повторных попыток при ошибках.
    
    Args:
        max_retries: Максимальное количество попыток
        delay: Начальная задержка между попытками (секунды)
        backoff: Множитель для увеличения задержки
        exceptions: Кортеж исключений, при которых делать retry
        log_errors: Логировать ошибки
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        if log_errors:
                            print(f"[Retry] Попытка {attempt + 1}/{max_retries} неудачна: {type(e).__name__}: {e}", flush=True)
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        if log_errors:
                            print(f"[Retry] Все {max_retries} попыток исчерпаны: {type(e).__name__}: {e}", flush=True)
            
            raise last_exception
        return wrapper
    return decorator


def safe_request(
    method: str,
    url: str,
    max_retries: int = 3,
    timeout: int = 30,
    **kwargs
) -> requests.Response:
    """
    Безопасный HTTP запрос с retry логикой.
    
    Args:
        method: HTTP метод (GET, POST, etc.)
        url: URL для запроса
        max_retries: Максимальное количество попыток
        timeout: Таймаут запроса
        **kwargs: Дополнительные параметры для requests
        
    Returns:
        Response объект
        
    Raises:
        requests.RequestException: При ошибках HTTP запросов
    """
    last_exception = None
    delay = 1.0
    
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except (requests.RequestException, requests.Timeout) as e:
            last_exception = e
            if attempt < max_retries - 1:
                print(f"[SafeRequest] Попытка {attempt + 1}/{max_retries} неудачна: {type(e).__name__}: {e}", flush=True)
                time.sleep(delay)
                delay *= 2
            else:
                print(f"[SafeRequest] Все {max_retries} попыток исчерпаны: {type(e).__name__}: {e}", flush=True)
    
    raise last_exception

