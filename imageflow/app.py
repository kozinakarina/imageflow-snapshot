"""FastAPI приложение для обработки изображений."""
import os
import io
import re
import requests
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
    import time
    import sys
    import traceback
    
    # Валидация входных данных
    if not request.image_url or not request.image_url.strip():
        raise HTTPException(status_code=400, detail="image_url не может быть пустым")
    
    if not request.game_title or not request.game_title.strip():
        raise HTTPException(status_code=400, detail="game_title не может быть пустым")
    
    if not request.provider or not request.provider.strip():
        raise HTTPException(status_code=400, detail="provider не может быть пустым")
    
    # Валидация URL
    if not request.image_url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="image_url должен быть валидным HTTP/HTTPS URL")
    
    # Получаем API ключ из переменных окружения
    fal_api_key = os.getenv("FAL_API_KEY")
    if not fal_api_key:
        raise HTTPException(
            status_code=500,
            detail="FAL_API_KEY не настроен в переменных окружения"
        )
    
    try:
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
        
        if result_image is None:
            raise RuntimeError("Пайплайн вернул None вместо изображения")
        
        print(f"[API] Пайплайн завершен за {time.time() - pipeline_start:.2f}с, размер изображения: {result_image.size}", flush=True)
        
        # Конвертируем в PNG байты
        convert_start = time.time()
        try:
            png_bytes = pil_to_bytes(result_image, format="PNG")
        except Exception as e:
            print(f"[API] Ошибка конвертации в PNG: {type(e).__name__}: {e}", flush=True)
            raise RuntimeError(f"Ошибка конвертации изображения в PNG: {e}") from e
        
        if not png_bytes or len(png_bytes) == 0:
            raise RuntimeError("Конвертация в PNG вернула пустой результат")
        
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
    
    except HTTPException:
        # Пробрасываем HTTPException как есть
        raise
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Ошибка сетевого запроса: {type(e).__name__}: {str(e)}"
        print(f"[API] {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=503, detail=error_msg)
    
    except ValueError as e:
        error_msg = f"Ошибка валидации данных: {str(e)}"
        print(f"[API] {error_msg}", flush=True)
        raise HTTPException(status_code=400, detail=error_msg)
    
    except RuntimeError as e:
        error_msg = f"Ошибка выполнения пайплайна: {str(e)}"
        print(f"[API] {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=error_msg)
    
    except Exception as e:
        error_msg = f"Неожиданная ошибка обработки изображения: {type(e).__name__}: {str(e)}"
        print(f"[API] {error_msg}", flush=True)
        print(traceback.format_exc(), flush=True)
        raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

