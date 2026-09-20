import type { Metadata, Viewport } from "next"
import type { ReactNode } from "react"
import "./globals.css"

export const metadata: Metadata = {
  title: "YRcine Noir · Manga Backend",
  description: "Manga API backend for the YRcine Noir app, powered by the MangaDex API.",
}

export const viewport: Viewport = {
  themeColor: "#0a0a0f",
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
