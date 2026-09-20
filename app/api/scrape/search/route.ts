import { NextResponse } from "next/server"
import { search } from "@/lib/mangadex"

export const dynamic = "force-dynamic"

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const query = (searchParams.get("query") || searchParams.get("q") || "").trim()
    const results = await search(query)
    return NextResponse.json({ results })
  } catch (err) {
    return NextResponse.json({ results: [], error: String((err as Error).message || err) }, { status: 502 })
  }
}

export function OPTIONS() {
  return new NextResponse(null, { status: 204 })
}
