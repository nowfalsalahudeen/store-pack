#!/usr/bin/env python3
"""Checks every store image against the published rules (macOS `sips`).

  python3 check_pack.py /abs/store/app.json

  Play icon           512 x 512, <= 1 MB
  Play feature graphic 1024 x 500, no alpha
  Play phone shots    2-8; each side 320-3840 px; long side <= 2x short side; no alpha
  Play 7"/10" tablet  up to 8 each; same pixel rules
  App Store icon      1024 x 1024, no alpha
  App Store shots     exact sizes below, 1-10 each, no alpha
"""
import glob
import json
import os
import subprocess
import sys

CFG = os.path.abspath(sys.argv[1])
ROOT = os.path.dirname(CFG)
cfg = json.load(open(CFG))
problems = []


def info(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", "-g", "hasAlpha", path], capture_output=True, text=True, check=True).stdout
    v = {l.split(":")[0].strip(): l.split(":")[1].strip() for l in out.splitlines() if ":" in l and not l.startswith("/")}
    return int(v["pixelWidth"]), int(v["pixelHeight"]), v["hasAlpha"] == "yes"


def check(ok, msg):
    print(("  ok   " if ok else "  FAIL ") + msg)
    if not ok:
        problems.append(msg)


def rel(x):
    return os.path.relpath(x, ROOT)


def play_pixels_ok(w, h):
    return min(w, h) >= 320 and max(w, h) <= 3840 and max(w, h) <= 2 * min(w, h)


for loc in cfg.get("play", {}).get("locales", []):
    base = os.path.join(ROOT, "google-play", "metadata", "android", loc, "images")
    print(f"Google Play {loc}")
    icon = os.path.join(base, "icon.png")
    if os.path.exists(icon):
        w, h, _ = info(icon)
        check((w, h) == (512, 512) and os.path.getsize(icon) <= 1024 * 1024, f"icon {w}x{h}, {os.path.getsize(icon) // 1024} KB")
    fg = os.path.join(base, "featureGraphic.png")
    if os.path.exists(fg):
        w, h, a = info(fg)
        check((w, h) == (1024, 500) and not a, f"feature graphic {w}x{h}, alpha={a}")
    for folder in ("phoneScreenshots", "sevenInchScreenshots", "tenInchScreenshots"):
        shots = sorted(glob.glob(os.path.join(base, folder, "*.png")))
        if not shots:
            continue
        check(2 <= len(shots) <= 8, f"{folder}: {len(shots)} images (2-8)")
        for s in shots:
            w, h, a = info(s)
            check(play_pixels_ok(w, h) and not a, f"{rel(s)} {w}x{h}, alpha={a}")

apple = cfg.get("apple", {})
if apple or os.path.exists(os.path.join(ROOT, "app-store", "icon")):
    print("App Store")
    icon = os.path.join(ROOT, "app-store", "icon", "app-icon-1024.png")
    if os.path.exists(icon):
        w, h, a = info(icon)
        check((w, h) == (1024, 1024) and not a, f"icon {w}x{h}, alpha={a}")
    for key, folder in (("iphone69", "iphone-6.9"), ("iphone65", "iphone-6.5"), ("ipad13", "ipad-13")):
        if key not in apple:
            continue
        size = tuple(apple[key])
        shots = sorted(glob.glob(os.path.join(ROOT, "app-store", "screenshots", "en-US", folder, "*.png")))
        check(1 <= len(shots) <= 10, f"{folder}: {len(shots)} screenshots (1-10)")
        for s in shots:
            w, h, a = info(s)
            check((w, h) == size and not a, f"{rel(s)} {w}x{h}, alpha={a}")

print()
if problems:
    print(f"{len(problems)} problem(s)")
    sys.exit(1)
print("all images pass")
