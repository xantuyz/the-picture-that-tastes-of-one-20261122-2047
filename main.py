#!/usr/bin/env python3
"""Deliver the finished strawberry artwork to the grading harness.

The artwork is drawn by render.py (Pillow) at build time and shipped
here as entry.png; this entrypoint only needs the standard library, so
it runs in the sandbox with nothing installed. It copies entry.png to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png) and only
reports success when the copy's SHA-256 matches the original.
"""

import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ORIGINAL = os.path.join(HERE, "entry.png")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    destination = os.path.join(out_dir, "entry.png")
    shutil.copyfile(ORIGINAL, destination)
    want = sha256_of(ORIGINAL)
    got = sha256_of(destination)
    if want != got:
        sys.stderr.write("entry.png copy failed its digest check\n")
        return 1
    size = os.path.getsize(destination)
    sys.stdout.write("wrote %s (%d bytes, sha256 %s)\n"
                     % (destination, size, got))
    return 0


if __name__ == "__main__":
    sys.exit(main())
