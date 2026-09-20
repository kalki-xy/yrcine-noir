const ENDPOINTS = [
  { path: "/api/health", desc: "Connection check used by the app status pill" },
  { path: "/api/trending", desc: "Trending manga grid" },
  { path: "/api/scrape/search?query=", desc: "Search by title" },
  { path: "/api/scrape/info?id=", desc: "Series detail + chapter list" },
  { path: "/api/scrape/pages?chapterId=", desc: "Page image URLs for a chapter" },
  { path: "/api/proxy/image?url=", desc: "Image proxy for covers and pages" },
]

export default function Home() {
  return (
    <main
      style={{
        maxWidth: 640,
        margin: "0 auto",
        padding: "56px 20px 80px",
        display: "flex",
        flexDirection: "column",
        gap: 28,
      }}
    >
      <header style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: ".14em",
            textTransform: "uppercase",
            color: "#f5b942",
          }}
        >
          <span style={{ width: 8, height: 8, borderRadius: 99, background: "#22c55e" }} aria-hidden />
          Online
        </span>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em" }}>
          YRcine Noir · Manga Backend
        </h1>
        <p style={{ margin: 0, color: "#9a9aa6", fontSize: 15, lineHeight: 1.6 }}>
          The manga API for the YRcine Noir app, powered by the public{" "}
          <a href="https://mangadex.org" style={{ color: "#f5b942" }}>
            MangaDex
          </a>{" "}
          catalog. Point the app&apos;s backend URL at this origin.
        </p>
      </header>

      <section
        style={{
          border: "1px solid #21212b",
          borderRadius: 14,
          overflow: "hidden",
          background: "#101018",
        }}
        aria-label="Available endpoints"
      >
        {ENDPOINTS.map((e, i) => (
          <div
            key={e.path}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 4,
              padding: "14px 16px",
              borderTop: i === 0 ? "none" : "1px solid #1b1b24",
            }}
          >
            <code style={{ fontSize: 13, color: "#e7e7ee", fontWeight: 700 }}>{e.path}</code>
            <span style={{ fontSize: 13, color: "#77777f" }}>{e.desc}</span>
          </div>
        ))}
      </section>

      <p style={{ margin: 0, color: "#5a5a63", fontSize: 12, lineHeight: 1.6 }}>
        Content is served from MangaDex. This service only relays public catalog data and does not host any files.
      </p>
    </main>
  )
}
