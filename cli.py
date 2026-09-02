"""
cli.py
------
Batch/terminal version of the pipeline, for scripting or cron jobs
where a UI isn't needed.

Usage:
    python cli.py --input ./raw_photos --output ./studio_photos
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

from image_fixer import SUPPORTED_EXTS, process_image


def process_folder(input_dir: Path, output_dir: Path, canvas_size: int, padding: float) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in input_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTS)

    if not files:
        sys.exit(f"No JPEG/PNG/WEBP files found in {input_dir}")

    for path in files:
        print(f"Processing {path.name} ...")
        try:
            original = Image.open(path)
            result = process_image(original, canvas_size=canvas_size, padding_ratio=padding)
            out_path = output_dir / f"{path.stem}_studio.jpg"
            result.save(out_path, quality=95)
        except Exception as exc:
            print(f"  Failed: {exc}")

    print(f"\nDone. Studio images saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="CV background remover + studio compositor (batch mode)")
    parser.add_argument("--input", required=True, help="Folder of raw product photos")
    parser.add_argument("--output", required=True, help="Folder to save studio-finished photos")
    parser.add_argument("--canvas", type=int, default=1600, help="Output canvas size in pixels (square)")
    parser.add_argument("--padding", type=float, default=0.10, help="Padding ratio around the product (0-0.4)")
    args = parser.parse_args()
    process_folder(Path(args.input), Path(args.output), args.canvas, args.padding)


if __name__ == "__main__":
    main()
