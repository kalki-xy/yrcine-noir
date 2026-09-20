import { NextResponse } from "next/server"
import { info } from "@/lib/mangadex"

export const dynamic = "force-dynamic"

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const id = (searchParams.get("id") || "").trim()
    if (!id) return NextResponse.json({ error: "missing id" }, { status: 400 })
    const data = await info(id)
    return NextResponse.json({ data })
  } catch (err) {
    return NextResponse.json({ error: String((err as Error).message || err) }, { status: 502 })
  }
}

export function OPTIONS() {
  return new NextResponse(null, { status: 204 })
}
