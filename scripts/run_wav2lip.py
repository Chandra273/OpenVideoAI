#!/usr/bin/env python
"""Run a minimal local pipeline: TTS (gTTS) -> Wav2Lip inference -> move MP4 to Downloads.

Requirements (manual before running):
- Clone Wav2Lip into `tools/Wav2Lip`.
- Download the Wav2Lip checkpoint (e.g. `wav2lip_gan.pth`) into `tools/Wav2Lip/weights/`.
- Install `gTTS` and the appropriate `torch`/`torchvision` for your GPU.
- Ensure `ffmpeg` is installed and on PATH.

Example:
  .\.venv\Scripts\Activate.ps1
  pip install gTTS
  # install torch per your CUDA (see https://pytorch.org)
  git clone https://github.com/Rudrabha/Wav2Lip.git tools\Wav2Lip
  # download weights into tools\Wav2Lip\weights\wav2lip_gan.pth

Usage:
  python scripts/run_wav2lip.py --prompt "Your Telugu text here" --image input_face.jpg
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from gtts import gTTS
except Exception as e:
    print("Missing gTTS. Install with: pip install gTTS")
    raise

from app.core.config import settings


def run(cmd, **kwargs):
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, **kwargs)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", "-p", required=True, help="Text to speak")
    p.add_argument("--image", "-i", default="input_face.jpg", help="Input face image path")
    p.add_argument("--lang", default="te", help="TTS language (default: te for Telugu)")
    p.add_argument("--wav2lip-dir", default="tools/Wav2Lip", help="Path to Wav2Lip clone")
    p.add_argument("--weights", default=None, help="Path to wav2lip weights (overrides default)")
    p.add_argument("--outfile", default=None, help="Output filename (defaults to result_wav2lip.mp4)")
    args = p.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    wav2lip_dir = (repo_root / args.wav2lip_dir).resolve()
    if not wav2lip_dir.exists():
        print(f"Wav2Lip directory not found: {wav2lip_dir}")
        print("Please clone Wav2Lip into tools/Wav2Lip: git clone https://github.com/Rudrabha/Wav2Lip.git tools/Wav2Lip")
        sys.exit(1)

    # prepare audio files
    audio_mp3 = repo_root / "tmp_audio.mp3"
    audio_wav = repo_root / "tmp_audio.wav"

    print("Generating TTS audio (gTTS)...")
    tts = gTTS(args.prompt, lang=args.lang)
    tts.save(str(audio_mp3))

    # convert mp3 -> wav using ffmpeg
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin:
        print("ffmpeg not found on PATH. Install ffmpeg and ensure it's available on PATH.")
        sys.exit(1)

    run([ffmpeg_bin, "-y", "-i", str(audio_mp3), str(audio_wav)])

    # locate weights
    if args.weights:
        weights_path = Path(args.weights).resolve()
    else:
        weights_path = wav2lip_dir / "weights" / "wav2lip_gan.pth"

    if not weights_path.exists():
        print(f"Wav2Lip weights not found at {weights_path}")
        print("Download the pretrained weights and place them into tools/Wav2Lip/weights/")
        sys.exit(1)

    # run inference
    inference_py = wav2lip_dir / "inference.py"
    if not inference_py.exists():
        print(f"Inference script not found at {inference_py}. Make sure the repo is cloned correctly.")
        sys.exit(1)

    out_name = args.outfile or "result_wav2lip.mp4"
    out_local = repo_root / out_name

    cmd = [sys.executable, str(inference_py),
           "--checkpoint_path", str(weights_path),
           "--face", str(Path(args.image).resolve()),
           "--audio", str(audio_wav),
           "--outfile", str(out_local)]

    print("Running Wav2Lip inference (this may take a while)...")
    run(cmd)

    # move result to Downloads
    downloads = Path(settings.DOWNLOADS_DIR)
    downloads.mkdir(parents=True, exist_ok=True)
    dest = downloads / out_local.name
    shutil.move(str(out_local), str(dest))
    print(f"Saved result to: {dest}")

    # cleanup
    try:
        audio_mp3.unlink()
        audio_wav.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    main()
