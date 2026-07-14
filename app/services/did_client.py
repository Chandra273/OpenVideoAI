"""Minimal D-ID provider client (placeholder).

This client implements a simple HTTP call to D-ID's API. To actually use it,
set `DID_API_KEY` in your environment or `.env` and ensure you agree to the
provider's terms. This function is a placeholder that demonstrates how to
integrate; it will raise an error if no API key is configured.
"""
import os
import time
import requests
from pathlib import Path
from typing import Optional

from app.core.config import settings


def generate_video_with_did(prompt: str, dialogue: Optional[str], out_path: Path, reuse: bool = False, timeout: int = 300) -> Path:
    """Generate a video using D-ID (or compatible) provider.

    This function implements a minimal job-submit + poll + download flow.
    It expects the provider to accept a POST to `settings.DID_API_URL` and
    return either a direct video URL or a job `id` that can be polled at
    `{DID_API_URL}/{id}` to obtain a `result_url` or similar field.

    The exact payload may need adjustment per provider; this implementation
    provides a sensible default for D-ID-like APIs.
    """
    api_key = os.getenv("DID_API_KEY") or settings.DID_API_KEY
    if not api_key:
        raise RuntimeError("DID_API_KEY not configured. Set DID_API_KEY in your environment to use the provider.")

    endpoint = os.getenv("DID_API_URL") or settings.DID_API_URL
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "script": {"type": "text", "input": dialogue or prompt},
        "config": {"resolution": "1080p"},
    }

    resp = requests.post(endpoint, json=payload, headers=headers, timeout=60)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Provider API error: {resp.status_code} {resp.text}")

    data = resp.json()

    # If provider returned a direct URL, download it.
    video_url = data.get("video_url") or data.get("result_url") or data.get("url")
    job_id = data.get("id") or data.get("jobId")

    if not video_url and not job_id:
        # Some providers may return an object with nested fields; attempt common keys
        for k in ("result", "data"):
            maybe = data.get(k) if isinstance(data, dict) else None
            if isinstance(maybe, dict):
                video_url = video_url or maybe.get("video_url") or maybe.get("result_url") or maybe.get("url")
                job_id = job_id or maybe.get("id")

    if video_url:
        # Direct download
        return _download_url_to_path(video_url, out_path)

    if not job_id:
        raise RuntimeError("Provider response did not include a job id or video URL; adapt integration to provider API")

    # Poll job status
    poll_url = f"{endpoint.rstrip('/')}/{job_id}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(poll_url, headers=headers, timeout=30)
        if r.status_code not in (200, 201):
            time.sleep(2)
            continue
        info = r.json()
        status = info.get("status") or info.get("state")
        # provider-specific: status values might be 'done', 'succeeded', 'completed'
        if status and status.lower() in ("done", "succeeded", "completed", "finished"):
            video_url = info.get("result_url") or info.get("video_url") or info.get("url")
            if video_url:
                return _download_url_to_path(video_url, out_path)
            # maybe nested
            for k in ("result", "data"):
                maybe = info.get(k)
                if isinstance(maybe, dict):
                    video_url = maybe.get("result_url") or maybe.get("video_url") or maybe.get("url")
                    if video_url:
                        return _download_url_to_path(video_url, out_path)
        # Not ready yet
        time.sleep(2)

    raise RuntimeError("Timed out waiting for provider to finish rendering video")


def _download_url_to_path(url: str, out_path: Path) -> Path:
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return out_path
