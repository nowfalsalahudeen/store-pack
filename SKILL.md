---
name: store-pack
description: Build a Google Play and App Store submission pack for an app (icons, framed screenshots in the exact store sizes, feature graphic, listing text with character limits, console form answers, blocker analysis) into a store/ folder in the project. Use when asked to make an app "Play Store / App Store ready" or to prepare store assets, listings or console form answers.
---

# store-pack

Produces `store/` in the project root: icons, framed screenshots, a feature graphic, listing text, console form answers and a README of blockers. Never submit, commit or deploy; leave that to the user.

Requirements: Python 3, the Flutter SDK (the image composer is a Flutter test, no app needed), and macOS (`sips` for image checks and icon sizes). Raw screenshots come from the app itself.

## Workflow

1. **Inspect the app for facts** (never invent): package/bundle ID, version, permissions (AndroidManifest, Info.plist), SDKs in pubspec, Cargo.toml or package.json (ads, analytics, crash reporting, billing, sign-in), how accounts and payments work, privacy-policy and support URLs, signing config, device families. Read the project's own contributor docs for its rules.
2. **Raw screenshots.** Capture from the real app with realistic *invented* data. Never use production data or a production account.
   - Flutter: a widget-test harness with real fonts (`debugDisableShadows = false`, or shadows render as hard outlines); phone 440x956 at 3x = 1320x2868.
   - Web, desktop or hybrid apps: run the app's own server on a scratch database, seed it through the API, and drive it with a browser automation tool. Use a separate browser context with `deviceScaleFactor` 3 (phone, viewport 440x956) or 2 (tablet, 1032x1376), and hide scrollbars with `*::-webkit-scrollbar{display:none!important}*{scrollbar-width:none!important}` before each shot.
   - Kill only the process listening on your own scratch port (`lsof -ti tcp:PORT -sTCP:LISTEN`), never by name.
   - Check each shot by eye. Drop screens that are broken at that width and tell the user.
3. **`store/app.json`** (see `docs/config-reference.md`), then run `python3 scripts/make_pack.py store/app.json`. It frames screens on a brand gradient with a caption, builds a feature graphic and icons, and runs `scripts/check_pack.py`.
   - Icon: usually only art with baked-in rounded corners or text exists; the `icon` job crops the mark onto a flat full-bleed background. Tell the user a vector or clean 1024 px source is still needed.
4. **Listing text:** `store/listings.json`, then `python3 scripts/write_listings.py store/listings.json` (fastlane layout, limits enforced). Describe only what the build really does and what the platform build includes.
5. **Docs:** `store/README.md` (blockers table first), `google-play/console-forms.md`, `app-store/connect-forms.md`.

## Store specs (confirm in the consoles; Apple's page may not load)

- Play: icon 512 px (<= 1 MB); feature graphic 1024x500, no alpha; 2-8 phone shots, each side 320-3840 px and long side <= 2x short side (use 1080x1920); optional 7"/10" tablet shots (1200x1920, 1600x2560); title 30, short 80, full 4000.
- App Store: iPhone 6.9" 1320x2868 (required), 6.5" 1284x2778; iPad 13" 2064x2752 if iPad is supported; up to 10 each; **no alpha**; icon 1024 px, no alpha; name 30, subtitle 30, promo 170, keywords 100.
- Both reject screenshots with an alpha channel; the composer writes RGB PNG.

## Blockers to look for in every app (learned)

- **Payments:** selling digital unlocks or licences through a web payment provider inside the app breaks Play Billing / Apple IAP rules. For iOS ship without purchase UI, or add StoreKit. No prices or buy links in mobile builds.
- **Account deletion:** any app that creates accounts needs an in-app delete path and (Play) a public web URL describing it.
- **Sign in with Apple:** required wherever Google or other third-party sign-in is offered on iOS.
- **Test ad IDs** left in a release; missing real IDs.
- **Play App Signing:** add Play's app-signing SHA-1 to Google OAuth Android clients, or sign-in fails on Play installs.
- **Restricted or declared permissions:** `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`, foreground-service types (need a declaration and a video), location (even with `maxSdkVersion`), Bluetooth `neverForLocation`.
- **Reviewer access:** apps that need a server or licence need a demo server, PIN and steps (Play App access, Apple guideline 2.1).
- **Privacy policy URL** must exist; contact address and phone for trader status (EU/UK).
- **Release signing** configured; version bump; AAB for Play; Apple team and bundle ID; `ITSAppUsesNonExemptEncryption`; privacy manifest.
- **New personal Play accounts:** a 12-tester, 14-day closed test is required before production.
- **Data safety:** "processed ephemerally" only for data used in memory and never stored (for example a photo sent to an AI service); email or IDs kept on a server are not ephemeral. Advertising ID: answer "No" only if no ad or conversion SDK is present and the advertising-ID permission is removed.
- **Target audience** 18+ unless the app is truly for children.
- **A minimum-size shrinker (R8) can fail on optional libraries:** if a release build fails with "Missing classes", add `-dontwarn` rules for the named packages.

## Files

- `scripts/make_pack.py` runs everything; `scripts/compose/` is the Flutter composer (`STORE_JOBS=jobs.json flutter test`); `scripts/build_icons.py`; `scripts/check_pack.py`; `scripts/write_listings.py`.
- `templates/app.example.json`, `templates/listings.example.json` - configs to copy. `examples/` - a complete worked example with a fictional app and its output.
- `docs/` - getting started, config reference, how it works.
