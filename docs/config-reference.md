# `app.json` reference

Paths are relative to the `store/` folder (the JSON file's folder) unless absolute. A working file is `examples/store/app.json`.

```json
{
  "name": "My App",
  "style": { "bg": ["#003B28", "#004D34"], "text": "#FFF8F6", "accent": "#FED65B", "font": "Roboto", "weight": 800 },
  "icon":  { "src": "/abs/art.png", "srcRect": [0, 0, 512, 512], "bgAt": [4, 4], "inset": 0.10 },
  "play":  { "locales": ["en-US"], "phone": [1080, 1920], "tablet7": [1200, 1920], "tablet10": [1600, 2560] },
  "apple": { "iphone69": [1320, 2868], "iphone65": [1284, 2778], "ipad13": [2064, 2752] },
  "phone":  [{ "id": "1_home", "raw": "_work/raw/phone/1_home.png", "caption": { "en": "Headline" } }],
  "tablet": [{ "id": "1_home", "raw": "_work/raw/tablet/1_home.png", "caption": { "en": "Headline" } }],
  "feature": { "tagline": { "en": "What it does" }, "screen": "phone:0" },
  "appiconset": "/abs/ios/Runner/Assets.xcassets/AppIcon.appiconset"
}
```

Leave out any key you do not need (no `apple` means no App Store images; no `tablet` means no tablet sets).

## Keys

| Key | Meaning |
|---|---|
| `name` | App name, used on the feature graphic. |
| `style` | `bg` (2-3 gradient colours), `text` (caption colour), `accent` (tagline and highlight), `bezel`, `font` (default Roboto), `weight` (100-900, default 800), `scale` (caption size, default 1), `align` (`left` or `center`). |
| `fonts` | Optional custom fonts: `[{ "family": "Brand", "files": ["/abs/Brand-Bold.ttf"] }]`, then use `"font": "Brand"` in `style`. |
| `icon` | The art for the icon. `src` image, `srcRect` the part to keep `[x, y, w, h]`, `bgAt` a pixel whose colour becomes the flat background, `inset` margin as a fraction (default 0.10), `fade` how far the art stays opaque (default 0.62). Needed for the feature graphic and the icon files. |
| `play` | `locales` (for example `["en-US", "ml-IN"]`) and the pixel sizes for `phone`, `tablet7`, `tablet10`. |
| `apple` | Sizes for `iphone69`, `iphone65`, `ipad13`. |
| `phone`, `tablet` | One entry per screenshot: `id` (file name), `raw` (the raw screenshot), `caption` per language (`en` required). |
| `feature` | The feature graphic: `tagline` per language and `screen` (`phone:0` means the first phone screenshot). |
| `appiconset` | Optional path to an iOS asset catalog; every icon size it lists is written. |

## Outputs

```
google-play/metadata/android/<locale>/images/   phoneScreenshots/, sevenInchScreenshots/, tenInchScreenshots/, featureGraphic.png, icon.png
app-store/screenshots/en-US/                    iphone-6.9/, iphone-6.5/, ipad-13/
app-store/icon/app-icon-1024.png                opaque, for App Store Connect
```

## `listings.json`

See `templates/listings.example.json`. Limits enforced: Play title 30, short 80, full 4000, release notes 500; App Store name 30, subtitle 30, promo 170, keywords 100, description 4000, release notes 4000. `version_code` names the changelog file.

## Checks

`scripts/check_pack.py` verifies: Play icon 512x512 and at most 1 MB; feature graphic 1024x500 with no alpha; 2-8 phone shots with each side 320-3840 px and long side at most twice the short; tablet sets the same; App Store icon 1024x1024 with no alpha; App Store screenshots at exact sizes, 1-10 each, no alpha.
