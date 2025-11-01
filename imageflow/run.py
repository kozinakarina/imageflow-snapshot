#!/usr/bin/env python3
"""Скрипт запуска ImageFlow API."""
import os
import sys

# Добавляем текущую директорию в PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    # Загружаем переменные окружения
    env_path = os.path.join(current_dir, ".env")
    load_dotenv(env_path)
    
    port = int(os.getenv("PORT", 8000))
    
    print(f"Запуск ImageFlow API на порту {port}...")
    print(f"Загружены переменные из: {env_path}")
    
    # Запускаем сервер с увеличенными таймаутами
    uvicorn.run(
        "imageflow.app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        timeout_keep_alive=600,  # Увеличено время keep-alive (10 минут)
        timeout_graceful_shutdown=60,  # Время на graceful shutdown
        limit_concurrency=10,  # Максимальное количество одновременных соединений
        limit_max_requests=1000  # Максимальное количество запросов перед перезапуском
    )



