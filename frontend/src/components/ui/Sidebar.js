'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import {
  LayoutDashboard, ArrowLeftRight, Lightbulb, Bot,
  BarChart3, Settings, LogOut, TrendingUp, Menu, X
} from 'lucide-react'
import { useState } from 'react'
import clsx from 'clsx'

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/transactions', label: 'Transactions', icon: ArrowLeftRight },
  { href: '/insights', label: 'Insights', icon: Lightbulb },
  { href: '/ai', label: 'AI Advisor', icon: Bot },
  { href: '/reports', label: 'Reports', icon: BarChart3 },
  { href: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)

  const NavContent = () => (
    <>
      {/* Logo */}
      <div className="px-5 py-5 border-b border-[#0A2540]/30">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#2E7D32]/20 border border-[#2E7D32]/40 flex items-center justify-center flex-shrink-0">
            <TrendingUp size={16} className="text-[#2E7D32]" />
          </div>
          <span className="font-display font-bold text-lg tracking-tight text-semantic-white">
            Biashara<span className="gradient-text">IQ</span>
          </span>
        </div>
        {user && (
          <div className="mt-3">
            <p className="text-xs text-semantic-textSecondary truncate">{user.business_name}</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || (href !== '/dashboard' && pathname?.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              onClick={() => setMobileOpen(false)}
              className={clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                active
                  ? 'bg-[#2E7D32]/15 text-[#2E7D32] border border-[#2E7D32]/30'
                  : 'text-semantic-textSecondary hover:text-semantic-white hover:bg-white/[0.04]'
              )}
            >
              <Icon size={17} />
              {label}
              {href === '/ai' && (
                <span className="ml-auto text-[10px] bg-[#2E7D32]/25 text-[#2E7D32] px-1.5 py-0.5 rounded-full font-semibold border border-[#2E7D32]/30">
                  AI
                </span>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Bottom */}
      <div className="px-3 py-4 border-t border-[#0A2540]/30">
        {user && (
          <div className="px-3 mb-2">
            <p className="text-xs font-medium text-semantic-white truncate">{user.owner_name || user.email}</p>
            <p className="text-xs text-semantic-textMuted truncate">{user.email}</p>
          </div>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-semantic-textSecondary hover:text-[#D32F2F] hover:bg-[#D32F2F]/5 transition-all w-full"
        >
          <LogOut size={17} />
          Sign Out
        </button>
      </div>
    </>
  )

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-56 min-h-screen bg-[#121821] border-r border-[#0A2540]/30 fixed left-0 top-0 bottom-0 z-30">
        <NavContent />
      </aside>

      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 bg-[#121821] border-b border-[#0A2540]/30 px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-[#2E7D32]/20 border border-[#2E7D32]/40 flex items-center justify-center">
            <TrendingUp size={14} className="text-[#2E7D32]" />
          </div>
          <span className="font-display font-bold text-lg tracking-tight text-semantic-white">
            Biashara<span className="gradient-text">IQ</span>
          </span>
        </div>
        <button onClick={() => setMobileOpen(!mobileOpen)} className="text-semantic-textSecondary hover:text-semantic-white p-1">
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/70" onClick={() => setMobileOpen(false)} />
          <aside className="absolute left-0 top-0 bottom-0 w-64 bg-[#121821] border-r border-[#0A2540]/30 flex flex-col">
            <NavContent />
          </aside>
        </div>
      )}
    </>
  )
}
