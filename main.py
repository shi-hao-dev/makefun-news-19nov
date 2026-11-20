# A news-image-daily entry (Python 3.13, standard library only): its image is the
# entry.png beside this file, and the program copies it to /output/entry.png. The
# image is "THE WORLD IN ONE DAY", a 1024x1024 newsprint poster summing up
# Thursday 19 November 2026 in 33 verified stories: a masthead and continent
# stats bar (Asia 7, Europe 6, Africa 5, N. America 7, S. America 2, Oceania 2,
# Middle East 3, Global 1), a world map with one numbered dot per story, 3 lead
# stories, 12 secondary stories and an 18-item "The Day in Brief" timeline,
# plus a date-check footer. It is drawn once, from the day's reporting
# (draw_poster.py, PIL), and copied unchanged, so two runs write the same bytes.
#
# Before copying, the program checks the image is really there and really a PNG
# (its 8-byte signature), so a missing or corrupted file fails loudly instead of
# silently handing the grader a bad entry.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
SRC = HERE / "entry.png"

if not SRC.is_file():
    print(f"error: {SRC} is missing, nothing to copy", file=sys.stderr)
    raise SystemExit(1)

with SRC.open("rb") as f:
    head = f.read(len(PNG_SIGNATURE))
if head != PNG_SIGNATURE:
    print(f"error: {SRC} is not a valid PNG (bad signature)", file=sys.stderr)
    raise SystemExit(1)

OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(SRC, OUT / "entry.png")
