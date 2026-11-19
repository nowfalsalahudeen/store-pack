#!/usr/bin/env python3
"""Writes every store listing text file (fastlane layout) from store/listings.json and enforces limits.

  python3 write_listings.py /abs/store/listings.json

listings.json
{
  "play":  { "en-IN": {"title": "...", "short": "...", "full": "...", "changelog": "..."} },
  "apple": { "name": "...", "subtitle": "...", "promo": "...", "keywords": "a,b,c", "full": "...", "release": "...",
             "support_url": "...", "marketing_url": "...", "privacy_url": "...",
             "primary_category": "BUSINESS", "secondary_category": "PRODUCTIVITY", "copyright": "2026 Name" },
  "version_code": 2
}
Limits: Play title 30, short 80, full 4000, changelog 500. App Store name 30, subtitle 30, promo 170,
keywords 100, description 4000, release notes 4000.
"""
import json
import os
import sys

CFG = os.path.abspath(sys.argv[1])
ROOT = os.path.dirname(CFG)
cfg = json.load(open(CFG))

LIM = {"title": 30, "short": 80, "full": 4000, "changelog": 500, "name": 30, "subtitle": 30, "promo": 170, "keywords": 100, "release": 4000}
ok_all = True


def check(label, text, key):
    global ok_all
    n = len(text)
    ok = n <= LIM[key]
    ok_all &= ok
    print(f"  {'ok  ' if ok else 'OVER'} {label:34s} {n:5d} / {LIM[key]}")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.strip("\n") + "\n")


print("Google Play")
for loc, d in cfg.get("play", {}).items():
    base = os.path.join(ROOT, "google-play", "metadata", "android", loc)
    for k, label in (("title", "title"), ("short", "short description"), ("full", "full description"), ("changelog", "release notes")):
        check(f"{loc} {label}", d[k], k)
    write(os.path.join(base, "title.txt"), d["title"])
    write(os.path.join(base, "short_description.txt"), d["short"])
    write(os.path.join(base, "full_description.txt"), d["full"])
    write(os.path.join(base, "changelogs", f"{cfg.get('version_code', 1)}.txt"), d["changelog"])

a = cfg.get("apple")
if a:
    print("App Store (en-US)")
    for k, label in (("name", "name"), ("subtitle", "subtitle"), ("promo", "promotional text"), ("keywords", "keywords"), ("full", "description"), ("release", "release notes")):
        check(label, a[k], k)
    base = os.path.join(ROOT, "app-store", "metadata", "en-US")
    for fn, k in (("name.txt", "name"), ("subtitle.txt", "subtitle"), ("promotional_text.txt", "promo"), ("keywords.txt", "keywords"),
                  ("description.txt", "full"), ("release_notes.txt", "release"), ("support_url.txt", "support_url"),
                  ("marketing_url.txt", "marketing_url"), ("privacy_url.txt", "privacy_url")):
        write(os.path.join(base, fn), a[k])
    shared = os.path.join(ROOT, "app-store", "metadata")
    for fn, k in (("primary_category.txt", "primary_category"), ("secondary_category.txt", "secondary_category"), ("copyright.txt", "copyright")):
        if a.get(k):
            write(os.path.join(shared, fn), a[k])

if not ok_all:
    sys.exit("a text is over its limit")
print("all within limits")
