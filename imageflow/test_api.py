#!/usr/bin/env python3
"""Пример использования ImageFlow API."""
import requests
import sys

def test_render_endpoint():
    """Протестировать /render endpoint."""
    url = "http://localhost:8000/render"
    
    payload = {
        "image_url": "https://example.com/test-image.jpg",
        "game_title": "Hot Bonus",
        "provider": "Pragmatic Play"
    }
    
    print(f"Отправка запроса на {url}...")
    try:
        response = requests.post(url, json=payload, timeout=300)
        
        if response.status_code == 200:
            print(f"✓ Успешно! Размер ответа: {len(response.content)} байт")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            
            # Сохраняем результат
            with open("test_output.png", "wb") as f:
                f.write(response.content)
            print("✓ Результат сохранён в test_output.png")
            
            return True
        else:
            print(f"✗ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка запроса: {e}")
        return False

def test_health():
    """Протестировать /health endpoint."""
    url = "http://localhost:8000/health"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✓ Health check: {response.json()}")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("=== Тест ImageFlow API ===\n")
    
    print("1. Проверка health endpoint...")
    if not test_health():
        print("\n⚠ Сервер не запущен или недоступен!")
        print("Запустите сервер командой:")
        print("  python -m imageflow.app")
        sys.exit(1)
    
    print("\n2. Тест render endpoint...")
    if len(sys.argv) > 1:
        # Используем URL из аргументов
        image_url = sys.argv[1]
        print(f"Используем изображение: {image_url}")
        
        payload = {
            "image_url": image_url,
            "game_title": sys.argv[2] if len(sys.argv) > 2 else "Test Game",
            "provider": sys.argv[3] if len(sys.argv) > 3 else "Test Provider"
        }
        
        url = "http://localhost:8000/render"
        response = requests.post(url, json=payload, timeout=300)
        
        if response.status_code == 200:
            with open("test_output.png", "wb") as f:
                f.write(response.content)
            print(f"✓ Результат сохранён в test_output.png")
        else:
            print(f"✗ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
    else:
        print("⚠ Для теста render endpoint укажите URL изображения:")
        print("  python test_api.py <image_url> [game_title] [provider]")




