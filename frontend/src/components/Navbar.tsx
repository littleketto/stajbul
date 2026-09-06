import Link from 'next/link'

export function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white shadow-sm">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Link href="/" className="flex-shrink-0 text-xl font-bold text-gray-900">
              Staj<span className="text-primary-600">Bul</span>
            </Link>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <Link href="/" className="rounded-md px-3 py-2 text-sm font-medium text-gray-900 hover:bg-gray-50">
                  İlanları Keşfet
                </Link>
                <Link href="#" className="rounded-md px-3 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 hover:text-gray-900">
                  Şirketler
                </Link>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button className="text-sm font-medium text-gray-700 hover:text-gray-900">
              Giriş Yap
            </button>
            <button className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700">
              Kayıt Ol
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
