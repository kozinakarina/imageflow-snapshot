"""Entry point for Railway deployment."""
import os
import sys

# Добавляем текущую директорию в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Импортируем приложение из imageflow пакета
try:
    from imageflow.app import app
except Exception as e:
    print(f"ERROR: Failed to import app: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=port)

