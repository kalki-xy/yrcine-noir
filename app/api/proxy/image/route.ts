import { NextResponse } from "next/server"
import { isAllowedImageHost, IMAGE_UA } from "@/lib/mangadex"

export const dynamic = "force-dynamic"

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url)
  const url = searchParams.get("url") || ""
  if (!url || !isAllowedImageHost(url)) {
    return NextResponse.json({ error: "invalid or disallowed url" }, { status: 400 })
  }
  try {
    const upstream = await fetch(url, {
      headers: { "User-Agent": IMAGE_UA, Referer: "https://mangadex.org/" },
      next: { revalidate: 86400 },
    })
    if (!upstream.ok || !upstream.body) {
      return NextResponse.json({ error: `upstream HTTP ${upstream.status}` }, { status: 502 })
    }
    const contentType = upstream.headers.get("content-type") || "image/jpeg"
    return new NextResponse(upstream.body, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "public, max-age=86400, s-maxage=604800, immutable",
        "Access-Control-Allow-Origin": "*",
      },
    })
  } catch (err) {
    return NextResponse.json({ error: String((err as Error).message || err) }, { status: 502 })
  }
}

export function OPTIONS() {
  return new NextResponse(null, { status: 204 })
}
