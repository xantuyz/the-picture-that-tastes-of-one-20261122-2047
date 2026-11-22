# The Picture That Tastes of One

[![make.fun](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047)

One giant macro strawberry, rendered procedurally with Pillow: a glossy
red body with a soft vertical gradient, pale seeds following the fruit's
curved surface, a star of green calyx leaves, dew drops, and a dark
charcoal-green backdrop. No text inside the image.

## Run

```bash
python3 render.py   # writes entry.png (1024x1024)
python3 main.py     # copies entry.png to $MAKEFUN_OUTPUT_DIR (default /output)
```

`main.py` is standard-library only: the grader sandbox has no Pillow, so
it only copies the pre-rendered `entry.png` and verifies the SHA-256 of
the copy.
