"""ImageFlow API for Railway - Full pipeline."""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'imageflow'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

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

# Предзагрузка пайплайна при старте
pipeline_ready = False
pipeline_error = None

print("🔄 Loading pipeline...", file=sys.stderr)
try:
    from imageflow.pipeline import full_pipeline
    from imageflow.utils import pil_to_bytes
    pipeline_ready = True
    print("✅ Pipeline ready", file=sys.stderr)
except Exception as e:
    pipeline_error = str(e)
    print(f"❌ Pipeline error: {e}", file=sys.stderr)

@app.get("/health")
def health():
    return {"status": "ok", "pipeline": pipeline_ready, "error": pipeline_error}

@app.get("/")
def root():
    return {"message": "ImageFlow API", "ready": pipeline_ready}

@app.post("/render")
def render_image(request: RenderRequest):
    """Обработать изображение через полный пайплайн."""
    
    if not pipeline_ready:
        raise HTTPException(status_code=503, detail=f"Pipeline not ready: {pipeline_error}")
    
    fal_api_key = os.getenv("FAL_API_KEY")
    if not fal_api_key:
        raise HTTPException(status_code=500, detail="FAL_API_KEY not set")
    
    try:
        print(f"🎨 Processing: {request.game_title} / {request.provider}", file=sys.stderr)
        
        result = full_pipeline(
            image_url=request.image_url,
            game_title=request.game_title,
            provider=request.provider,
            fal_api_key=fal_api_key,
            seed=2069714305,
            concept=request.concept or "v1"
        )
        
        png_bytes = pil_to_bytes(result, format="PNG")
        print(f"✅ Done: {len(png_bytes)} bytes", file=sys.stderr)
        
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={"Content-Disposition": 'attachment; filename="result.png"'}
        )
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting on port {port}", file=sys.stderr)
    # Увеличенный таймаут
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=300)
