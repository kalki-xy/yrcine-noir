import { NextResponse } from "next/server"

export const dynamic = "force-dynamic"

export async function GET() {
  return NextResponse.json({ ok: true, service: "yrcine-noir-manga", provider: "mangadex", time: Date.now() })
}

export function OPTIONS() {
  return new NextResponse(null, { status: 204 })
}
