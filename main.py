"""Entry point for Railway deployment."""
import os
import sys

# Добавляем текущую директорию в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from fastapi import FastAPI

# Создаём минимальное приложение для проверки
minimal_app = FastAPI(title="ImageFlow API")

@minimal_app.get("/health")
def health():
    return {"status": "ok"}

@minimal_app.get("/")
def root():
    return {"message": "ImageFlow API is running"}

# Пытаемся импортировать полное приложение
try:
    from imageflow.app import app
    print("✅ Full app imported successfully", file=sys.stderr)
except Exception as e:
    print(f"⚠️ Using minimal app due to import error: {e}", file=sys.stderr)
    app = minimal_app

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on port {port}", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=port)
