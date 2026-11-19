# How it works

## The skill

`SKILL.md` is a short workflow with the store specs and a blockers checklist. An agent reads it, inspects your app for facts, and runs the scripts. It never invents facts about the app, never uses production data in screenshots, and never submits, commits or deploys.

## The pipeline

1. **Raw screenshots** come from the real app, with invented data.
2. **`make_pack.py`** reads `app.json` and writes `jobs.json`: one job per image (framed screenshot, feature graphic, icon) for each store and locale.
3. **`scripts/compose/`** is a small Flutter test project. It renders each job to an image offscreen (your app is not involved), so it works for any app: Flutter, web, native or hybrid. Output is RGB PNG without alpha, because both stores reject alpha.
4. **`build_icons.py`** makes the store icon sizes, including every size an iOS asset catalog lists.
5. **`check_pack.py`** checks every image against the published rules and prints `ok` or `FAIL` with the rule.
6. **`write_listings.py`** writes the fastlane-layout text files and enforces each character limit.

## Why a Flutter test for the composer

A widget test can lay out text, gradients and a device frame, then capture the result at a chosen pixel size with no window and no GPU, and with the same fonts every time. The composer reads only a JSON file and knows nothing about the app it is making images for.

## What is deliberately not automated

Capturing the raw screenshots (they need your app and judgement), the icon artwork, the console forms, and the final upload. The skill gives you the facts and the checklist for those, and leaves the clicks to you.
