from pathlib import Path
import sys
import argparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.t2v import generate_video_from_text


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", "-p", required=True)
    p.add_argument("--duration", "-d", type=int, default=5)
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--reuse", action="store_true", help="Reuse deterministic filename for the prompt (overwrite)")
    args = p.parse_args()

    out = generate_video_from_text(args.prompt, duration=args.duration, fps=args.fps, reuse=args.reuse)
    print("Saved:", out)


if __name__ == '__main__':
    main()
