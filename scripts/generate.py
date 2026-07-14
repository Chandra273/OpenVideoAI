import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path when running the script directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.t2v import generate_video_from_text


def main():
    parser = argparse.ArgumentParser(description="Generate a simple video from text prompt and save to Downloads.")
    parser.add_argument("--prompt", "-p", required=True, help="Text prompt for the video")
    parser.add_argument("--duration", "-d", type=int, default=5, help="Duration in seconds")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second")
    args = parser.parse_args()

    try:
        out = generate_video_from_text(args.prompt, duration=args.duration, fps=args.fps)
        print(f"Generated video: {out}")
    except Exception as e:
        print("Failed to generate video:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
