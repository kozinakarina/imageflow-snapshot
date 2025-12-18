"""Entry point for Railway deployment."""
import os
import sys

# Добавляем текущую директорию и imageflow в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'imageflow'))

# Теперь импортируем приложение
try:
    from imageflow.app import app
except ImportError:
    # Fallback: попробуем импортировать напрямую
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from imageflow import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

