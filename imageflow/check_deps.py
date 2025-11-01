#!/usr/bin/env python3
"""Скрипт для проверки установки зависимостей."""
import sys

def check_imports():
    """Проверить наличие всех необходимых модулей."""
    required_modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "uvicorn"),
        ("dotenv", "python-dotenv"),
        ("requests", "requests"),
        ("PIL", "Pillow"),
        ("numpy", "numpy"),
        ("cv2", "opencv-python"),
        ("rembg", "rembg"),
        ("sklearn", "scikit-learn"),
        ("pydantic", "pydantic"),
    ]
    
    missing = []
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} (не установлен)")
            missing.append(package_name)
    
    if missing:
        print(f"\n❌ Отсутствуют модули: {', '.join(missing)}")
        print("Установите их командой:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("\n✓ Все зависимости установлены!")
        return True

if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)




