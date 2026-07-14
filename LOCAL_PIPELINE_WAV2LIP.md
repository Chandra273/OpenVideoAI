Local Pipeline: Wav2Lip + TTS — Step-by-step

Purpose
- A minimal, local procedure to produce a talking avatar from a single image and text using: TTS (gTTS) -> Wav2Lip lip-sync.
- This guide assumes Windows + PowerShell and the project repo at the workspace root.

Safety & consent
- Only animate a real person's face with explicit consent.

Prerequisites
- Python 3.8–3.11 and a venv. Use the project's `.venv` if you already created one.
- `ffmpeg` installed and available on PATH. Download from https://ffmpeg.org and add to PATH.
- A GPU is strongly recommended for reasonable performance (you have an NVIDIA RTX A2000, good).
- Visual C++ Build Tools on Windows may be required for some Python packages.

Overview
1. Activate venv
2. Install Python packages: `gTTS` and the correct `torch`/`torchvision` for your CUDA
3. Clone Wav2Lip into `tools/Wav2Lip`
4. Download pretrained Wav2Lip weights to `tools/Wav2Lip/weights/wav2lip_gan.pth`
5. Prepare an input face image and the text prompt
6. Run `scripts/run_wav2lip.py` (wrapper added to this repo)

Detailed Steps (Windows PowerShell)

1) Activate virtual environment
```powershell
cd C:\Users\Z0202879\openvideoAI\OpenVideoAI
.\.venv\Scripts\Activate.ps1
```

2) Install minimal Python packages
```powershell
pip install gTTS
# Install torch matching your GPU/CUDA. Visit https://pytorch.org/get-started/locally/ and pick the proper command.
# Example for CUDA 11.8 (adjust if you have different CUDA):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Notes on `torch`:
- Use the PyTorch instructions page to choose the correct wheel for your GPU. Installing CPU-only torch is possible but very slow.

3) Install ffmpeg
- Download a static build from https://ffmpeg.org and extract it.
- Add the folder containing `ffmpeg.exe` to your system PATH. Open a new PowerShell and run `ffmpeg -version` to verify.

4) Clone Wav2Lip
```powershell
git clone https://github.com/Rudrabha/Wav2Lip.git tools\Wav2Lip
cd tools\Wav2Lip
pip install -r requirements.txt
```
- If some requirements fail on Windows (dlib, face-alignment), follow Wav2Lip README Windows notes. You may need Visual Studio Build Tools.

5) Download Wav2Lip weights
- The project requires pretrained weights (commonly named `wav2lip_gan.pth` or `wav2lip.pth`).
- The Wav2Lip README contains links (Google Drive). Download the weights and place them at:
  `tools\Wav2Lip\weights\wav2lip_gan.pth`

6) Prepare your inputs
- Place a frontal face image in the repo root (e.g., `input_face.jpg`). Prefer close-up, neutral expression.
- Decide your text prompt. For Telugu use proper UTF-8 text (or romanized if needed).

7) Run the wrapper script (added to this repo)
- This script automates gTTS -> ffmpeg convert -> Wav2Lip inference -> move output to Downloads.
```powershell
python scripts/run_wav2lip.py --prompt "మీరు ఇడ్లిని పిండి చేసే ముందు దాల్‌ను ఫ్రిజ్‌లో పెట్టండి" --image input_face.jpg
```
- The script will:
  - create `tmp_audio.mp3` via gTTS,
  - convert it to WAV with ffmpeg,
  - run `tools\Wav2Lip\inference.py` using the configured weights,
  - move `result_wav2lip.mp4` to your Downloads folder (from `app.core.config.settings.DOWNLOADS_DIR`).

Troubleshooting
- If `ffmpeg` not found: check PATH and open a new terminal.
- If `torch` import fails: you likely installed the wrong wheel for your CUDA; reinstall per PyTorch site.
- If `inference.py` crashes on missing face detection libs: install missing requirements or use a simpler face image (high-resolution frontal image helps).
- If Wav2Lip is slow or times out: ensure GPU drivers & CUDA are correct, and that `torch.cuda.is_available()` returns True.

Optional improvements
- Replace `gTTS` with Coqui TTS or other higher-quality TTS for better naturalness.
- Use First‑Order Motion Model or AnimateDiff to add head motion (complex, separate step).
- Use a short driver video and First‑Order Motion to add natural head turns.

Limitations
- Wav2Lip only lip-syncs the mouth; facial expressiveness and natural head movements are limited.
- Output is lower fidelity than commercial providers; expect to iterate on face image, audio, and model checkpoints.

If you want me to automate further
- I can add commands to automatically download the Wav2Lip weights (if you provide a direct URL) and try to bootstrap the tools folder. Reply: "auto-download weights".
- I can add a sample `input_face.jpg` (consenting stock avatar) and a test Telugu prompt to run a smoke test (you must still download weights and install torch). Reply: "add sample test".

End of procedure.
