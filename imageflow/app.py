"""FastAPI приложение для обработки изображений."""
import os
import io
import re
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from .pipeline import full_pipeline
from .utils import pil_to_bytes

# Загружаем переменные окружения
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(title="ImageFlow API", description="ComfyUI workflow as API service")


def sanitize_filename(text: str) -> str:
    """
    Очистить текст для использования в имени файла.
    Удаляет или заменяет специальные символы.
    """
    # Заменяем пробелы и специальные символы на подчеркивания
    text = re.sub(r'[^\w\s-]', '', text)  # Удаляем все кроме букв, цифр, пробелов и дефисов
    text = re.sub(r'[-\s]+', '_', text)  # Заменяем пробелы и дефисы на подчеркивания
    text = text.strip('_')  # Убираем подчеркивания в начале и конце
    return text


class RenderRequest(BaseModel):
    """Запрос на рендеринг изображения."""
    image_url: str
    game_title: str
    provider: str
    filename: Optional[str] = None  # Опциональное имя файла


@app.get("/health")
def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "ok"}


@app.post("/render")
def render_image(request: RenderRequest):
    """
    Обработать изображение по полному пайплайну.
    
    Возвращает PNG изображение как бинарные данные.
    """
    # Получаем API ключ из переменных окружения
    fal_api_key = os.getenv("FAL_API_KEY")
    if not fal_api_key:
        raise HTTPException(
            status_code=500,
            detail="FAL_API_KEY не настроен в переменных окружения"
        )
    
    try:
        import time
        import sys
        
        print(f"[API] Начало обработки запроса: image_url={request.image_url[:50]}...", flush=True)
        
        # Запускаем пайплайн
        pipeline_start = time.time()
        result_image = full_pipeline(
            image_url=request.image_url,
            game_title=request.game_title,
            provider=request.provider,
            fal_api_key=fal_api_key,
            seed=2069714305
        )
        print(f"[API] Пайплайн завершен за {time.time() - pipeline_start:.2f}с, размер изображения: {result_image.size}", flush=True)
        
        # Конвертируем в PNG байты
        convert_start = time.time()
        png_bytes = pil_to_bytes(result_image, format="PNG")
        print(f"[API] Конвертация в PNG завершена за {time.time() - convert_start:.2f}с, размер: {len(png_bytes)} байт", flush=True)
        sys.stdout.flush()
        
        # Генерируем имя файла: игра__провайдер (двойное подчеркивание для уникального разделения)
        if request.filename:
            # Если имя файла передано, используем его (но очищаем от спецсимволов)
            filename = sanitize_filename(request.filename)
        else:
            # Автоматически генерируем из game_title и provider
            game_clean = sanitize_filename(request.game_title)
            provider_clean = sanitize_filename(request.provider)
            filename = f"{game_clean}__{provider_clean}"  # Двойное подчеркивание для уникального разделения
        
        # Добавляем расширение если его нет
        if not filename.endswith('.png'):
            filename = f"{filename}.png"
        
        print(f"[API] Подготовка ответа: filename={filename}, размер={len(png_bytes)} байт", flush=True)
        sys.stdout.flush()
        
        # Возвращаем бинарные данные PNG с правильным именем файла
        response = Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(png_bytes))
            }
        )
        
        print(f"[API] Ответ подготовлен, отправка...", flush=True)
        sys.stdout.flush()
        
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки изображения: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

