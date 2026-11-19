#!/usr/bin/env python3
"""Makes every icon the stores need from store/_work/icon-1024-alpha.png (macOS `sips` only).

  python3 build_icons.py --root /abs/store [--locales en-IN,ml-IN] [--iconset /abs/AppIcon.appiconset]

Writes
  <root>/app-store/icon/app-icon-1024.png                  opaque (no alpha), for App Store Connect
  <root>/google-play/metadata/android/<locale>/images/icon.png    512 x 512, for Play Console
  <iconset>/*                                              every size in the iOS asset catalog's Contents.json
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--locales", default="")
ap.add_argument("--iconset", default="")
a = ap.parse_args()

SRC = os.path.join(a.root, "_work", "icon-1024-alpha.png")
if not os.path.exists(SRC):
    sys.exit(f"missing {SRC}: run make_pack.py first (it makes the master)")


def sips(*args):
    subprocess.run(["sips", *args], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def opaque_copy(src, dst):
    """Apple rejects icons with an alpha channel; a JPEG round trip drops it."""
    with tempfile.TemporaryDirectory() as tmp:
        jpg = os.path.join(tmp, "i.jpg")
        sips("-s", "format", "jpeg", "-s", "formatOptions", "100", src, "--out", jpg)
        sips("-s", "format", "png", jpg, "--out", dst)


master = os.path.join(a.root, "app-store", "icon", "app-icon-1024.png")
os.makedirs(os.path.dirname(master), exist_ok=True)
opaque_copy(SRC, master)

for loc in [l for l in a.locales.split(",") if l]:
    d = os.path.join(a.root, "google-play", "metadata", "android", loc, "images")
    os.makedirs(d, exist_ok=True)
    sips("-z", "512", "512", master, "--out", os.path.join(d, "icon.png"))

if a.iconset and os.path.isdir(a.iconset):
    contents = json.load(open(os.path.join(a.iconset, "Contents.json")))
    n = 0
    for img in contents["images"]:
        name = img.get("filename")
        if not name:
            continue
        px = round(float(img["size"].split("x")[0]) * int(img["scale"].rstrip("x")))
        dst = os.path.join(a.iconset, name)
        if px == 1024:
            shutil.copyfile(master, dst)
        else:
            sips("-z", str(px), str(px), master, "--out", dst)
        n += 1
    print("iOS AppIcon set rewritten:", n, "files")
print("icons done")
