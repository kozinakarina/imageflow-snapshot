"""Minimal FastAPI app for Railway."""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "ImageFlow API is running", "version": "minimal"}

@app.post("/render")
def render_image(request: RenderRequest):
    """Placeholder render endpoint."""
    return {
        "status": "received",
        "image_url": request.image_url,
        "game_title": request.game_title,
        "provider": request.provider,
        "message": "Full pipeline not yet configured. This is a test response."
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
