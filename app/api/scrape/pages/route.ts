import { NextResponse } from "next/server"
import { pages } from "@/lib/mangadex"

export const dynamic = "force-dynamic"

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const chapterId = (searchParams.get("chapterId") || searchParams.get("id") || "").trim()
    if (!chapterId) return NextResponse.json({ pages: [], error: "missing chapterId" }, { status: 400 })
    const result = await pages(chapterId)
    return NextResponse.json({ pages: result })
  } catch (err) {
    return NextResponse.json({ pages: [], error: String((err as Error).message || err) }, { status: 502 })
  }
}

export function OPTIONS() {
  return new NextResponse(null, { status: 204 })
}
