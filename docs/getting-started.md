# Getting started

From "I have an app" to a `store/` folder you can upload from.

## 0. What you need

- The app running somewhere you can screenshot it (a simulator, a device, a browser, a widget test).
- Python 3 and the Flutter SDK on the machine (the composer is a Flutter test; your app does not have to be Flutter).
- macOS for the image checks and icon sizes (`sips`).
- Art for the icon (a logo image at least 1024 px is best).

## 1. Install

See the [README](../README.md#install).

## 2. Capture raw screenshots

Use realistic **invented** data; never production data or a real customer's account.

- **Flutter:** a widget-test harness with real fonts and shadows on, at 440x956 logical pixels and 3x (1320x2868).
- **Web, desktop or hybrid:** run your server against a scratch database, seed it through the API, and drive a browser at 440x956 with `deviceScaleFactor` 3 (phone) or 1032x1376 at 2 (tablet). Hide scrollbars before each shot.
- Look at every shot. Drop any screen that is broken at that width.

Save them as `store/_work/raw/phone/<id>.png` (and `.../tablet/` if you want tablet sets).

## 3. Describe the pack

Copy `templates/app.example.json` to `store/app.json` and fill it in: the app name, a style (two or three gradient colours, text and accent colours), which store sizes you want, and one entry per screenshot with its caption. See [config-reference.md](config-reference.md).

## 4. Build the images

```bash
python3 scripts/make_pack.py store/app.json
```

This writes the framed screenshots, the feature graphic and the icons, then runs the checks. Every line is `ok` or `FAIL` with the rule it broke (for example, Play needs at least two phone screenshots).

## 5. Write the listings

Copy `templates/listings.example.json` to `store/listings.json`, fill it in, and run:

```bash
python3 scripts/write_listings.py store/listings.json
```

It writes the fastlane-layout text files and prints each text against its limit; anything over fails the run.

## 6. Read the blockers

Open the blockers list in `SKILL.md` and go through it against your app: account deletion, Sign in with Apple, payments, test ad IDs, permission declarations, reviewer access, privacy policy URL, signing, new-account testing rules and the data-safety form. An agent does this for you and writes `store/README.md` with a blockers table first.

## 7. Upload

Upload from `store/google-play/` and `store/app-store/` (by hand, or with fastlane `supply` and `deliver`). The skill never submits for you.
