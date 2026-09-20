// Thin wrapper around the public MangaDex API (https://api.mangadex.org).
// All manga "providers" the app sends are routed here.

const API = "https://api.mangadex.org"
const UPLOADS = "https://uploads.mangadex.org"

// A descriptive User-Agent is requested by MangaDex; sending one avoids throttling.
const UA = "YRcineNoir/1.0 (+https://github.com/kalki-xy/yrcine-noir)"

const CONTENT_RATINGS = ["safe", "suggestive", "erotica"]

type MdEntity = {
  id: string
  type: string
  attributes?: Record<string, any>
  relationships?: MdEntity[]
}

export type MangaItem = {
  id: string
  title: string
  coverUrl: string
  status?: string
  format?: string
  url: string
}

export type ChapterItem = {
  id: string
  number: string
  title: string
}

async function mdFetch(path: string): Promise<any> {
  const res = await fetch(API + path, {
    headers: { "User-Agent": UA, Accept: "application/json" },
    // These are live catalog reads; let the platform cache briefly.
    next: { revalidate: 60 },
  })
  if (!res.ok) throw new Error(`MangaDex HTTP ${res.status}`)
  return res.json()
}

function pickTitle(attrs: Record<string, any> = {}): string {
  const t = attrs.title || {}
  if (t.en) return t.en
  const first = Object.values(t)[0]
  if (typeof first === "string") return first
  const alt = (attrs.altTitles || []).find((a: any) => a.en)
  return (alt && alt.en) || "Untitled"
}

function pickDescription(attrs: Record<string, any> = {}): string {
  const d = attrs.description || {}
  if (d.en) return d.en
  const first = Object.values(d)[0]
  return typeof first === "string" ? first : ""
}

function coverFromRelationships(id: string, rels: MdEntity[] = [], size: 256 | 512 = 512): string {
  const cover = rels.find((r) => r.type === "cover_art")
  const fileName = cover?.attributes?.fileName
  if (!fileName) return ""
  return `${UPLOADS}/covers/${id}/${fileName}.${size}.jpg`
}

function toItem(entity: MdEntity): MangaItem {
  const attrs = entity.attributes || {}
  return {
    id: entity.id,
    title: pickTitle(attrs),
    coverUrl: coverFromRelationships(entity.id, entity.relationships),
    status: attrs.status,
    format: "MANGA",
    url: `https://mangadex.org/title/${entity.id}`,
  }
}

function ratingParams(): string {
  return CONTENT_RATINGS.map((r) => `contentRating[]=${r}`).join("&")
}

export async function trending(): Promise<MangaItem[]> {
  const json = await mdFetch(
    `/manga?limit=24&includes[]=cover_art&order[followedCount]=desc&hasAvailableChapters=true&${ratingParams()}`,
  )
  return (json.data || []).map(toItem)
}

export async function search(query: string): Promise<MangaItem[]> {
  if (!query) return trending()
  const json = await mdFetch(
    `/manga?limit=24&title=${encodeURIComponent(query)}&includes[]=cover_art&order[relevance]=desc&${ratingParams()}`,
  )
  return (json.data || []).map(toItem)
}

export async function info(
  id: string,
): Promise<{ title: string; description: string; status: string; coverUrl: string; chapters: ChapterItem[] }> {
  const detail = await mdFetch(`/manga/${id}?includes[]=cover_art`)
  const entity: MdEntity = detail.data
  const attrs = entity.attributes || {}

  const chapters = await feed(id)

  return {
    title: pickTitle(attrs),
    description: pickDescription(attrs),
    status: attrs.status || "",
    coverUrl: coverFromRelationships(id, entity.relationships),
    chapters,
  }
}

async function feed(id: string): Promise<ChapterItem[]> {
  const collected: MdEntity[] = []
  let offset = 0
  // MangaDex caps feed at 500 per page; two pages covers the vast majority of series.
  for (let page = 0; page < 2; page++) {
    const json = await mdFetch(
      `/manga/${id}/feed?limit=500&offset=${offset}` +
        `&translatedLanguage[]=en&order[chapter]=asc&includeExternalUrl=0&includeEmptyPages=0&${ratingParams()}`,
    )
    const data: MdEntity[] = json.data || []
    collected.push(...data)
    const total = json.total || 0
    offset += 500
    if (offset >= total) break
  }

  // Multiple scanlation groups can publish the same chapter number; keep the first of each.
  const seen = new Set<string>()
  const out: ChapterItem[] = []
  for (const c of collected) {
    const attrs = c.attributes || {}
    if (attrs.externalUrl) continue
    if (!attrs.pages || attrs.pages <= 0) continue
    const num = String(attrs.chapter ?? "")
    const key = num || c.id
    if (seen.has(key)) continue
    seen.add(key)
    out.push({
      id: c.id,
      number: num,
      title: attrs.title || (num ? `Chapter ${num}` : "Oneshot"),
    })
  }
  return out
}

export async function pages(chapterId: string): Promise<string[]> {
  const json = await mdFetch(`/at-home/server/${chapterId}`)
  const baseUrl = json.baseUrl
  const hash = json.chapter?.hash
  const files: string[] = json.chapter?.data || []
  if (!baseUrl || !hash) return []
  return files.map((f) => `${baseUrl}/data/${hash}/${f}`)
}

// Only allow proxying MangaDex-owned hosts so the endpoint can't be used as an open proxy.
export function isAllowedImageHost(url: string): boolean {
  try {
    const u = new URL(url)
    if (u.protocol !== "https:") return false
    const host = u.hostname
    return (
      host === "uploads.mangadex.org" ||
      host === "api.mangadex.org" ||
      host.endsWith(".mangadex.network") ||
      host.endsWith(".mangadex.org")
    )
  } catch {
    return false
  }
}

export const IMAGE_UA = UA
