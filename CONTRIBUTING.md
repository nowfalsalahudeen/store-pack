# Contributing

Issues and pull requests are welcome, especially:

- **Spec changes.** Store sizes, limits and rules move; if something in `SKILL.md` or `check_pack.py` is out of date, say what the console shows now and link the source.
- **New blockers** you hit on a real submission (add a line to the blockers list in `SKILL.md`).
- **Cross-platform checks.** `check_pack.py` and `build_icons.py` use macOS `sips`; a version using Pillow or ImageMagick would help Linux and Windows users.
- **Layouts** for the composer (more frame styles, tablet and desktop frames).

Please keep the skill app-neutral: no brand names, accounts or customer data in examples. Use fictional apps and placeholders.

Before sending a change to `scripts/`, run `python3 scripts/make_pack.py examples/store/app.json` and `python3 scripts/write_listings.py examples/store/listings.json` and look at the output.
