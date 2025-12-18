"""ImageFlow API for Railway - Simplified test."""
import os
import sys
import io
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from PIL import Image

app = FastAPI(title="ImageFlow API")

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
    return {"status": "ok", "version": "simple-test"}

@app.get("/")
def root():
    return {"message": "ImageFlow API - Simple Test Mode"}

@app.post("/render")
def render_image(request: RenderRequest):
    """Простой тест - загружает изображение и возвращает его."""
    try:
        print(f"Downloading: {request.image_url}", file=sys.stderr)
        
        # Скачиваем изображение
        response = requests.get(request.image_url, timeout=30)
        response.raise_for_status()
        
        # Открываем как PIL Image
        img = Image.open(io.BytesIO(response.content))
        print(f"Image loaded: {img.size} {img.mode}", file=sys.stderr)
        
        # Конвертируем в PNG
        output = io.BytesIO()
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
        img.save(output, format='PNG')
        png_bytes = output.getvalue()
        
        print(f"Returning: {len(png_bytes)} bytes", file=sys.stderr)
        
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={"Content-Disposition": 'attachment; filename="result.png"'}
        )
        
    except requests.RequestException as e:
        print(f"Download error: {e}", file=sys.stderr)
        raise HTTPException(status_code=400, detail=f"Failed to download image: {e}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting on port {port}", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=port)
