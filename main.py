"""Entry point for Railway deployment."""
import os
import sys

# Добавляем текущую директорию в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

# Создаём приложение
app = FastAPI(title="ImageFlow API")

# Добавляем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RenderRequest(BaseModel):
    image_url: str
    game_title: str
    provider: str
    filename: Optional[str] = None
    concept: Optional[str] = "v1"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "ImageFlow API is running"}

# Пытаемся импортировать полный пайплайн
full_pipeline = None
pil_to_bytes = None
import_error = None

try:
    from imageflow.pipeline import full_pipeline as fp
    from imageflow.utils import pil_to_bytes as ptb
    full_pipeline = fp
    pil_to_bytes = ptb
    print("✅ Full pipeline imported successfully", file=sys.stderr)
except Exception as e:
    import_error = str(e)
    print(f"⚠️ Pipeline import error: {e}", file=sys.stderr)

@app.post("/render")
def render_image(request: RenderRequest):
    """Обработать изображение."""
    if full_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail=f"Pipeline not available. Import error: {import_error}"
        )
    
    fal_api_key = os.getenv("FAL_API_KEY")
    if not fal_api_key:
        raise HTTPException(
            status_code=500,
            detail="FAL_API_KEY not configured"
        )
    
    try:
        result_image = full_pipeline(
            image_url=request.image_url,
            game_title=request.game_title,
            provider=request.provider,
            fal_api_key=fal_api_key,
            seed=2069714305,
            concept=request.concept or "v1"
        )
        
        png_bytes = pil_to_bytes(result_image, format="PNG")
        
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="result.png"',
            }
        )
    except Exception as e:
        print(f"❌ Render error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on port {port}", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=port)
