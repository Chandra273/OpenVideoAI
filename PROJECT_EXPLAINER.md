Project Explainer — OpenVideoAI

Purpose
- This document explains the key files in the repository, what each does, and where to look for the behavior you saw (local text video vs provider-driven talking-head). It also lists small cleanup actions I recommend and the next steps.

How to read this file
- I explain files by purpose and then call out the important functions/lines to inspect.
- I did not expand literally every source line-by-line (that would be very long). If you want a full per-line walk-through for any single file (e.g., `app/services/t2v.py` or `app/services/did_client.py`), tell me which file and I will produce a line-by-line version for it.

---

**Files & Explanation**

- `app/main.py`
  - Purpose: FastAPI app bootstrap.
  - Key lines:
    - `app = FastAPI(...)` — creates the app instance.
    - `app.include_router(v1_router, prefix="/api/v1")` — mounts the API routes.
    - `@app.on_event("startup")` logs `settings.APP_ENV` and `settings.DOWNLOADS_DIR` on startup.
  - Why it matters: if the server starts and logs the Downloads dir, the app is running and routes are available.

- `app/api/v1/routes.py`
  - Purpose: API surface for generation and simple health.
  - Key elements:
    - `GenerateRequest` — pydantic model with `prompt`, `duration`, `fps`, `reuse`.
    - `POST /generate` — core route. Behavior:
      - If `DID_API_KEY` is present in environment or `settings`, it uses `generate_video_with_did(...)` (external provider). It builds `out_name` (filesystem-safe) and `out_path` (Downloads) before calling the provider.
      - Else, calls local fallback `generate_video_from_text(...)` which creates a text-driven MP4 (non-speaking slide-based video).
    - Error handling wraps exceptions into HTTP 500 with the exception message.
  - Where to change: adapt the provider selection, request shape, or the returned JSON here.

- `app/core/config.py`
  - Purpose: central settings (pydantic `BaseSettings`). Loads `.env` by default.
  - Important fields:
    - `DOWNLOADS_DIR` — where MP4s are written (defaults to the user's Downloads folder).
    - `DID_API_KEY` and `DID_API_URL` — provider configuration. Set `DID_API_KEY` in `.env` to enable provider path.
  - Tip: edit `.env` with `DID_API_KEY=...` and restart uvicorn to use the provider.

- `app/db/session.py`
  - Purpose: SQLAlchemy engine & DB session factory used for persistence (currently not heavily used).
  - Note: SQLite fallback used for local dev; Postgres DSN supported via `DATABASE_URL`.
  - If you do not plan DB persistence right now, this file can be left as-is.

- `app/services/t2v.py`
  - Purpose: local prototype generator that renders frames with centered text and encodes an MP4 using MoviePy.
  - Key functions:
    - `_make_frame(text, size, ...)` — returns a PIL Image with wrapped, centered text. Handles font fallback and Pillow API differences.
    - `generate_video_from_text(prompt, duration, fps, filename, reuse)` — creates a temporary folder of PNG frames, builds an `ImageSequenceClip`, and writes MP4 using ffmpeg (MoviePy). Returns the written file path.
  - Why you saw a non-speaking video: this module creates slides (text images), not an animated human.
  - Common runtime issues: ensure `ffmpeg` is installed and on PATH (MoviePy calls ffmpeg). If ffmpeg not present, write_videofile will fail.

- `app/services/did_client.py`
  - Purpose: placeholder D‑ID-style provider client. Implements: submit job → poll → download result.
  - How it is used: `routes.generate` passes the prompt to `generate_video_with_did(prompt, prompt, out_path, reuse=...)`.
  - Why it might produce silent video:
    - If `DID_API_KEY` is missing or invalid the provider path is not used and the local fallback is used.
    - The placeholder payload (`{"script": {"type":"text","input":...}}`) may need to be adjusted to the exact provider API fields (avatar selection, voice, language, `input` vs `script`, etc.). Providers differ in required JSON.
  - What to change to get talking avatars:
    - Add provider-specific keys (avatar id, voice id, language) to `payload` before POST.
    - Ensure the API key is valid and the account supports the selected avatar/voice.

- `scripts/generate.py` and `scripts/generate_prompt_video.py`
  - Purpose: CLI helpers to run the local generator from terminal. Useful for quick tests without HTTP.
  - Keep them — they are small and helpful for debugging offline.

- `requirements.txt` and `.env.example` and `README.md`
  - `requirements.txt` lists runtime packages: `moviepy`, `Pillow`, `requests`, `fastapi`, `uvicorn`, `pydantic<2`, `SQLAlchemy`, etc. `pydantic<2` pinned for compatibility.
  - `.env.example` shows where to set `DID_API_KEY`.
  - `README.md` contains run instructions and project vision notes.

---

**Files I recommend *not* touching / keep**
- `app/main.py` — keep as bootstrap.
- `app/api/v1/routes.py` — keep as API surface.
- `app/core/config.py` — keep and edit `.env` values there.
- `app/services/t2v.py` — keep as local fallback and demo generator.
- `app/services/did_client.py` — keep and adapt payload for exact provider.
- `scripts/*` — keep for CLI testing.

**Files I recommend removing or ignoring (suggestions)**
- Remove committed `__pycache__` and `.pyc` files from the repo and add or update `.gitignore` to exclude them. These are build artifacts and should not be committed.
- Do not delete your `.venv` folder from the repo — but do not commit it to source control. If it is in your repo, add `.venv/` to `.gitignore`.

If you want me to perform deletions, say so and I will remove only files that are safe (e.g., `__pycache__` directories). I will not delete `.venv` automatically unless you confirm.

---

Quick answers to what produced the silent slide video you saw:
- The local fallback in `app/services/t2v.py` creates centered text frames (so the video is slides with captions). That is what you saw.
- To produce a realistic talking person you must use a provider (D‑ID or similar) and ensure `DID_API_KEY` is configured and the request payload includes avatar/voice details per the provider docs.

---

Next steps (point-by-point)
1. If you have an API key: add `DID_API_KEY` to `.env` (project root) and restart the server. Then POST to `/api/v1/generate` again. This is the fastest way to get a talking avatar.
2. If you do not have a key and want me to help obtain one: I can give step-by-step signup instructions for a chosen provider (D‑ID / Synthesia / Hour One). You must follow the provider signup and paste the key into `.env` locally (do not paste secrets into chat).
3. If you must run fully local and cannot use a provider: I can outline and help build a local pipeline using open-source tools (Wav2Lip + First-Order-Motion + TTS). This requires a GPU for reasonable speed and is a multi-day setup.
4. Improve provider integration: I can update `app/services/did_client.py` to include explicit avatar and voice IDs and any authentication header changes required by your chosen provider. For that I need either provider API docs or the name of the provider (I can look up public docs for D‑ID if you want).
5. Cleanup repo: remove `__pycache__` and `.pyc` files and update `.gitignore` — confirm and I will remove them.
6. Optional: stream the MP4 back in the HTTP response instead of returning a filepath, so callers immediately download the resulting MP4.

---

How I can proceed now (pick one)
- "Line-by-line for X": I will produce a per-line annotated version of a single file you choose (e.g., `app/services/did_client.py` or `app/services/t2v.py`).
- "Finalize provider payload for D‑ID": I will adapt `did_client.py` to D‑ID docs (requires you to set key locally afterwards).
- "Cleanup now": I will delete `__pycache__` directories from the repo and add `.gitignore` entries.

Reply with which of the three actions above you want next, or say "I need full line-by-line for all files" (and I will suggest a reasonable batching plan since that is large).

---

File created: `PROJECT_EXPLAINER.md` (this file). You can open it to review.
