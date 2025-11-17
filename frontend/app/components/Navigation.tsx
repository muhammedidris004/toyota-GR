'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import Logo from './Logo'

export default function Navigation() {
  const pathname = usePathname()

  const navItems = [
    { href: '/', label: 'Home' },
    { href: '/console', label: 'Console' },
    { href: '/comparison', label: 'Comparison' },
    { href: '/replay', label: 'Replay' },
  ]

  return (
    <nav className="bg-gr-asphalt/80 backdrop-blur-md border-b border-gr-grey/50 sticky top-0 z-50 shadow-gr">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <Link href="/" className="flex items-center group">
            <Logo size="md" showText={true} className="group-hover:opacity-80 transition-opacity" />
          </Link>
          <div className="flex items-center space-x-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-300 ${
                    isActive
                      ? 'bg-gr-red-gradient text-white shadow-gr-red'
                      : 'text-gr-grey hover:text-white hover:bg-gr-grey/50'
                  }`}
                >
                  {item.label}
                  {isActive && (
                    <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-gr-neon rounded-full animate-pulse" />
                  )}
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}

