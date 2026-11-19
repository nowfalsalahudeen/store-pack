#!/usr/bin/env python3
"""Builds every store image for an app from raw screenshots, driven by store/app.json.

  python3 make_pack.py /abs/path/to/store/app.json

Steps: write jobs.json -> flutter test (compose) -> icons (sips) -> verify.
Raw screenshots come from the app itself (device, simulator, browser at 2-3x). This
script only frames them and produces icons; it does not capture anything.

app.json (paths relative to the store/ folder unless absolute)
{
  "name": "My App",
  "style": {"bg": ["#003B28","#004D34"], "text": "#FFF8F6", "accent": "#FED65B", "font": "Roboto", "weight": 800},
  "icon": {"src": "abs/art.png", "srcRect": [x,y,w,h], "bgAt": [x,y], "inset": 0.10},
  "play":  {"locales": ["en-IN"], "phone": [1080,1920], "tablet7": [1200,1920], "tablet10": [1600,2560]},
  "apple": {"iphone69": [1320,2868], "iphone65": [1284,2778], "ipad13": [2064,2752]},   # omit a key to skip it
  "phone":  [{"id": "1_home", "raw": "_work/raw/phone/1_home.png", "caption": {"en": "Headline"}}],
  "tablet": [{"id": "1_home", "raw": "_work/raw/tablet/1_home.png", "caption": {"en": "Headline"}}],
  "feature": {"tagline": {"en": "What it does"}, "screen": "phone:0"},
  "appiconset": "/abs/ios/Runner/Assets.xcassets/AppIcon.appiconset"      # optional
}
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = os.path.abspath(sys.argv[1])
ROOT = os.path.dirname(CFG)
cfg = json.load(open(CFG))


def p(path):
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def lang_of(locale):
    return locale.split("-")[0]


jobs = []
style = cfg.get("style", {})
play = cfg.get("play", {})
apple = cfg.get("apple", {})

# Icon master (flat, full-bleed; the store applies its own mask).
if cfg.get("icon"):
    ic = cfg["icon"]
    jobs.append({
        "type": "icon", "src": p(ic["src"]), "srcRect": ic["srcRect"], "bgAt": ic["bgAt"], "inset": ic.get("inset", 0.10), "fade": ic.get("fade", 0.62),
        "canvas": [1024, 1024], "out": p("_work/icon-1024-alpha.png"),
    })


def framed(shot, size, out, lang, device):
    return {
        "type": "framed", "raw": p(shot["raw"]), "caption": shot["caption"].get(lang) or shot["caption"]["en"],
        "canvas": list(size), "out": out, "style": {**style, "device": device},
    }


for loc in play.get("locales", []):
    lang = lang_of(loc)
    base = p(f"google-play/metadata/android/{loc}/images")
    for s in cfg.get("phone", []):
        if "phone" in play:
            jobs.append(framed(s, play["phone"], f"{base}/phoneScreenshots/{s['id']}.png", lang, "phone"))
    for s in cfg.get("tablet", []):
        if "tablet7" in play:
            jobs.append(framed(s, play["tablet7"], f"{base}/sevenInchScreenshots/{s['id']}.png", lang, "tablet"))
        if "tablet10" in play:
            jobs.append(framed(s, play["tablet10"], f"{base}/tenInchScreenshots/{s['id']}.png", lang, "tablet"))
    if cfg.get("feature") and cfg.get("icon"):
        kind, idx = cfg["feature"].get("screen", "phone:0").split(":")
        screen = cfg[kind][int(idx)]
        jobs.append({
            "type": "feature", "icon": p("_work/icon-1024-alpha.png"), "raw": p(screen["raw"]), "name": cfg["name"],
            "tagline": cfg["feature"]["tagline"].get(lang) or cfg["feature"]["tagline"]["en"],
            "canvas": [1024, 500], "out": f"{base}/featureGraphic.png", "style": {**style, "weight": style.get("weight", 800)},
        })

for key, folder, group, device in (("iphone69", "iphone-6.9", "phone", "phone"), ("iphone65", "iphone-6.5", "phone", "phone"), ("ipad13", "ipad-13", "tablet", "tablet")):
    if key in apple:
        for s in cfg.get(group, []):
            jobs.append(framed(s, apple[key], p(f"app-store/screenshots/en-US/{folder}/{s['id']}.png"), "en", device))

jobs_path = p("_work/jobs.json")
os.makedirs(os.path.dirname(jobs_path), exist_ok=True)
json.dump({"fonts": cfg.get("fonts", []), "jobs": jobs}, open(jobs_path, "w"), indent=1)
print(f"{len(jobs)} image jobs written to {jobs_path}")

env = {**os.environ, "STORE_JOBS": jobs_path}
subprocess.run(["flutter", "test", "test/compose_test.dart", "--timeout", "600s", "--reporter", "failures-only"],
               cwd=os.path.join(HERE, "compose"), env=env, check=True)

if cfg.get("icon"):
    args = [sys.executable, os.path.join(HERE, "build_icons.py"), "--root", ROOT, "--locales", ",".join(play.get("locales", []))]
    if cfg.get("appiconset"):
        args += ["--iconset", cfg["appiconset"]]
    subprocess.run(args, check=True)

subprocess.run([sys.executable, os.path.join(HERE, "check_pack.py"), CFG])
