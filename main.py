# A news-image-daily entry (Python 3.13, standard library only): its image is the
# entry.png beside this file, and the program copies it to /output/entry.png. The
# image sums up Thursday 19 November 2026's world news: the first Trump-Xi-Putin
# summit in Shenzhen, the ICJ's ruling on the Rohingya case, Ukraine's strike on
# the Crimean Bridge, COP31's final stretch in Antalya, Anthropic's record IPO
# and Cyclone Akvan. It is drawn once, from the day's reporting, and copied
# unchanged, so two runs write the same bytes.
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
