# YRcine Noir

A personal, single-file cinematic streaming & entertainment app — movies, anime, manga and AI — wrapped in an Android WebView APK. Built by Yash Raj.

The entire app is **one HTML file** (no build step, no server, offline-first). The `apk-kit/` wraps that file into a signed, installable Android APK with a native request interceptor that injects referers/UA for stream and manga sources and rewrites HLS manifests through an internal proxy.

## What's inside

- **Movies** — TMDB browsing + embed playback
- **Otaku** — zero-setup anime (AniList with automatic MyAnimeList failover) → AniKoto episodes → MegaPlay HLS streams; three manga sources (Mangapill / WeebCentral / MangaFire) with a unified reader, chapter search, per-source detail tabs
- **Miru-style settings** — theme mode (dark/light/system) + 7 accent colors, home layout reorder, adult content toggle, anime API picker
- **Smart networking** — request serialization, rate-limit auto-retry, response caching, AniList↔MAL auto-failover, direct→native-proxy→corsproxy fallback chains for images and streams

## Repo layout

```
├── README.md
├── BUILD.md                     # step-by-step APK build instructions
├── apk-kit/
│   ├── AndroidManifest.xml      # versionCode 32 / versionName 27.0
│   └── src/.../MainActivity.java  # WebView shell + request interceptor + m3u8 rewriting proxy
├── build/
│   ├── v27-patch.py             # patcher that generates the v27 app build script
│   └── smoke_v27.js             # headless regression smoke test (node)
└── (app HTML + APK live in the Releases section)
```

The app HTML is ~1 MB, so each version ships as a **Release asset** rather than a git blob: grab `YRcine_Noir_VoidVerse-27.html` and `YRcine-Noir-v27-Failover.apk` from the [latest release](../../releases).

## Building the APK

See [BUILD.md](BUILD.md). Requirements: JDK 17, Android SDK platform-34 + build-tools 34.0.0. Keep the same `yrcine.keystore` (in release assets) and keep bumping `versionCode` so updates install over the old build.

## Update cadence

Each app version is a superset of the previous one-file HTML; the patcher chain in `build/` documents the evolution (v20 base → v27). The full patch chain is kept out of git for size — the release assets are the source of truth for each version.

> Personal-use app. Content comes from third-party public sites and APIs; sources can change or break independently.
