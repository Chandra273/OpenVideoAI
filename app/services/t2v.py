from pathlib import Path
import textwrap
import tempfile
import time
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
# Import ImageSequenceClip from moviepy. Some installs expose it under
# `moviepy.editor`, others put it at `moviepy.video.io.ImageSequenceClip`.
try:
    from moviepy.editor import ImageSequenceClip
except Exception:
    from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

from app.core.config import settings


def _make_frame(text: str, size=(1280, 720), bg_color=(20, 20, 20), fg_color=(240, 240, 240)) -> Image.Image:
    """Create a single PIL Image with the prompt text centered and wrapped.

    This is the primitive used to synthesize frames for a simple text-driven video.
    """
    img = Image.new("RGB", size, color=bg_color)
    draw = ImageDraw.Draw(img)

    # Use a default font. On Windows the default may vary; ImageFont.load_default()
    # is always available but small. We attempt a larger truetype fallback when possible.
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except Exception:
        font = ImageFont.load_default()

    # Wrap text to fit width
    max_width = size[0] - 120
    lines = []
    for paragraph in text.split("\n"):
        lines.extend(textwrap.wrap(paragraph, width=40))

    # Compute total text height robustly across Pillow versions
    try:
        bbox = draw.textbbox((0, 0), "A", font=font)
        single_height = bbox[3] - bbox[1]
    except Exception:
        try:
            single_height = font.getsize("A")[1]
        except Exception:
            single_height = font.getmask("A").size[1]
    line_height = single_height + 10
    total_height = line_height * len(lines)

    y = (size[1] - total_height) // 2
    for line in lines:
        try:
            tb = draw.textbbox((0, 0), line, font=font)
            w = tb[2] - tb[0]
            h = tb[3] - tb[1]
        except Exception:
            try:
                w, h = font.getsize(line)
            except Exception:
                w, h = font.getmask(line).size
        x = (size[0] - w) // 2
        draw.text((x, y), line, font=font, fill=fg_color)
        y += line_height

    return img


def generate_video_from_text(prompt: str, duration: int = 5, fps: int = 24, filename: Optional[str] = None, reuse: bool = False) -> Path:
    """Generate a simple MP4 video from a text prompt.

    - Renders a sequence of frames with centered text (the prompt).
    - Writes an MP4 to the user's Downloads directory (from settings.DOWNLOADS_DIR).

    Returns the Path of the written MP4.
    """
    # Ensure downloads dir exists
    downloads = Path(settings.DOWNLOADS_DIR)
    downloads.mkdir(parents=True, exist_ok=True)

    if filename is None:
        # Create a deterministic, filesystem-safe filename from the prompt when reuse is requested.
        safe = "".join(c for c in prompt if c.isalnum() or c in (" ","-","_"))[:40].rstrip()
        safe = safe.replace(" ", "_") or "video"
        if reuse:
            filename = f"{safe}.mp4"
        else:
            timestamp = int(time.time())
            filename = f"{safe}_{timestamp}.mp4"

    out_path = downloads / filename

    # Number of frames
    total_frames = int(duration * fps)

    # Create frames in a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        frames = []
        for i in range(total_frames):
            # Optionally animate: we can vary brightness or offset for simple effect
            img = _make_frame(prompt)
            frame_path = Path(tmpdir) / f"frame_{i:04d}.png"
            img.save(frame_path)
            frames.append(str(frame_path))

        # Create a clip from images
        clip = ImageSequenceClip(frames, fps=fps)

        # Write the video file. moviepy will use ffmpeg (ensure ffmpeg is installed).
        # Avoid passing logger/verbose kwargs for maximum compatibility across versions.
        clip.write_videofile(str(out_path), codec="libx264", audio=False)

    return out_path
