'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'

export default function Home() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      router.replace(user ? '/dashboard' : '/login')
    }
  }, [user, loading, router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-[#0F6B4F] border-t-transparent animate-spin" />
        <span className="text-[#9CA3AF]">Loading BiasharaIQ...</span>
      </div>
    </div>
  )
}
