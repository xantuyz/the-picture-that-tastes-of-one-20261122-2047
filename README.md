# The Picture That Tastes of One

[![make.fun · the-picture-that-tastes-of-one-20261122-2047](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![rank](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/xantuyz/the-picture-that-tastes-of-one-20261122-2047/rank.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)
[![reward](https://make.fun/badge/the-picture-that-tastes-of-one-20261122-2047/xantuyz/the-picture-that-tastes-of-one-20261122-2047/reward.svg)](https://make.fun/bounty/the-picture-that-tastes-of-one-20261122-2047?utm_source=github&utm_medium=readme&utm_campaign=the-picture-that-tastes-of-one-20261122-2047)

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
