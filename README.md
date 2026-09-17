# YRcine Noir

A personal, single-file cinematic streaming & entertainment app — movies, TV, anime, videos and AI — wrapped in an Android WebView APK.

The entire app is **one HTML file** (no build step, no server, offline-first). The `apk-kit/` wraps that file into a signed, installable Android APK with a native request interceptor that injects referers/UA for stream and media sources and rewrites HLS manifests through an internal proxy.

## What's inside

- **Movies & TV** — full TMDB hub: trending hero, In Theaters, Popular, Top Rated, Upcoming, genres, multi-search, detail pages with cast & trailers, Where-to-Watch (India), favorites, Continue Watching with resume + share + "because you watched" recommendations
- **Otaku** — zero-setup anime streaming (AniList catalog with Jikan fallback) · MegaPlay HLS streams · auto subtitles · manga reader with chapter search and per-source detail tabs
- **Videos** — YouTube-first (trending, music, gaming, movies) with Dailymotion fallback
- **AI** — Groq / Gemini / OpenAI chat with live model discovery, image attachments, history
- **Vault, themes, music, library** — PIN private vault, theme picker, music player, watch history
- **Smart networking** — request serialization, rate-limit auto-retry, response caching, direct→proxy fallback chains, image-proxy fallbacks for ISP-blocked CDNs

## Repo layout

```
├── README.md
├── BUILD.md               # step-by-step APK build instructions
├── apk-kit/
│   ├── AndroidManifest.xml
│   └── src/.../MainActivity.java
└── (app HTML + APK live in the Releases section)
```

Each version ships as a **Release asset** rather than a git blob — grab `YRcine_Noir_VoidVerse-38.0.html` (or the latest) from [Releases](../../releases).

## Building the APK

See [BUILD.md](BUILD.md). Requirements: JDK 17, Android SDK platform-34 + build-tools 34. Keep the same `yrcine.keystore` (in release assets) and keep bumping `versionCode` so updates install over the old build. Current: **versionCode 61 / v38.0**.

> Personal-use app. Content comes from third-party public sites and APIs; sources can change or break independently.
