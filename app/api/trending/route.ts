import { NextResponse } from "next/server"
import { trending } from "@/lib/mangadex"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const results = await trending()
    return NextResponse.json({ results })
  } catch (err) {
    return NextResponse.json({ results: [], error: String((err as Error).message || err) }, { status: 502 })
  }
}

export function OPTIONS() {
  return new NextResponse(null, { status: 204 })
}
