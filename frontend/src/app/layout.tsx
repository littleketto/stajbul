import type { Metadata } from 'next'
import { Navbar } from '@/components/Navbar'
import './globals.css'

export const metadata: Metadata = {
  title: 'StajBul - Akıllı Staj Platformu',
  description: 'Türkiye\'deki tüm staj fırsatlarını keşfet, filtrele ve başvur.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="tr">
      <body className="font-sans antialiased bg-gray-50 text-gray-900">
        <Navbar />
        <main className="min-h-screen">{children}</main>
      </body>
    </html>
  )
}
