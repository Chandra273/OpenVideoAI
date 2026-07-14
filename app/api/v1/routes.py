from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path

from app.services.t2v import generate_video_from_text
from app.services.did_client import generate_video_with_did
from app.core.config import settings

router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    duration: int = 10
    fps: int = 24
    reuse: bool = True


@router.get("/")
def root():
    return {"message": "Text-to-Video API v1"}


@router.post("/generate")
def generate(req: GenerateRequest):
    """Generate a video for the given prompt.

    If `DID_API_KEY` is configured, attempts to use the external provider.
    Otherwise falls back to the local MoviePy generator (non-actor prototype).
    """
    out_name = None
    try:
        # If external provider configured, prefer it
        if getattr(settings, "DID_API_KEY", None) or "DID_API_KEY" in __import__("os").environ:
            safe = "".join(c for c in req.prompt if c.isalnum() or c in (" ","-","_"))[:40].rstrip().replace(" ", "_") or "video"
            if req.reuse:
                out_name = f"{safe}.mp4"
            else:
                from time import time
                out_name = f"{safe}_{int(time())}.mp4"
            out_path = Path(settings.DOWNLOADS_DIR) / out_name
            # Pass the prompt/dialogue to D-ID client (placeholder implementation)
            generate_video_with_did(req.prompt, req.prompt, out_path, reuse=req.reuse)
            return {"path": str(out_path), "provider": "d-id"}
        else:
            # fallback to local generator
            out_path = generate_video_from_text(req.prompt, duration=req.duration, fps=req.fps, reuse=req.reuse)
            return {"path": str(out_path), "provider": "local"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
