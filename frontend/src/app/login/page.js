'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/context/AuthContext'
import { TrendingUp, Eye, EyeOff, AlertCircle } from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      router.push('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-semantic-accentBlue">
      <div className="w-full max-w-md animate-fade-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-10 h-10 rounded-xl bg-[#2E7D32]/10 border border-[#2E7D32]/30 flex items-center justify-center">
              <TrendingUp size={20} className="text-[#2E7D32]" />
            </div>
            <span className="font-display font-bold text-2xl tracking-tight">
              Biashara<span className="gradient-text">IQ</span>
            </span>
          </div>
          <p className="text-semantic-textSecondary text-sm">Sign in to your business account</p>
        </div>

        {/* Card */}
        <div className="card p-8">
          {error && (
            <div className="mb-5 flex items-center gap-2 p-3 rounded-lg bg-[#D32F2F]/10 border border-[#D32F2F]/20 text-[#D32F2F] text-sm">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm text-semantic-white mb-1.5 font-medium">Email</label>
              <input
                type="email"
                className="input-dark"
                placeholder="you@business.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="block text-sm text-semantic-white mb-1.5 font-medium">Password</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  className="input-dark pr-10"
                  placeholder="Your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-semantic-textSecondary hover:text-semantic-white"
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button type="submit" className="btn-primary w-full justify-center py-3" disabled={loading}>
              {loading ? (
                <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Signing in...</>
              ) : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-semantic-textSecondary">
            New to BiasharaIQ?{' '}
            <Link href="/register" className="text-[#2E7D32] hover:text-[#2E7D32] font-medium">
              Create account
            </Link>
          </div>
        </div>

        <p className="text-center text-xs text-semantic-textSecondary mt-6">
          Financial intelligence for Kenyan businesses 🇰🇪
        </p>
      </div>
    </div>
  )
}
