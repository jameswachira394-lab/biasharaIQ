'use client'
import Link from 'next/link'
import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { TrendingUp, Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react'
import GoogleAuthButton from '@/components/GoogleAuthButton'

function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const { login } = useAuth()
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    if (searchParams.get('reset') === 'success') {
      setSuccessMsg('Your password has been reset successfully. You can now log in.')
    }
  }, [searchParams])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccessMsg('')
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
    <div className="min-h-screen flex items-center justify-center px-4 bg-cream-300">
      <div className="w-full max-w-md animate-fade-in">
        {/* Back to Home */}
        <div className="mb-4">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-sm text-semantic-textSecondary hover:text-[#8B5E3C] transition-colors"
          >
            ← Back to Home
          </Link>
        </div>

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-10 h-10 rounded-xl bg-[#8B5E3C]/10 border border-[#8B5E3C]/30 flex items-center justify-center">
              <TrendingUp size={20} className="text-[#8B5E3C]" />
            </div>
            <span className="font-display font-bold text-2xl tracking-tight">
              Biashara<span className="gradient-text">IQ</span>
            </span>
          </div>
          <p className="text-semantic-textSecondary text-sm">Sign in to your business account</p>
        </div>

        {/* Card */}
        <div className="card p-8">
          {successMsg && (
            <div className="mb-5 flex items-center gap-2 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm">
              <CheckCircle size={16} />
              {successMsg}
            </div>
          )}

          {error && (
            <div className="mb-5 flex items-center gap-2 p-3 rounded-lg bg-[#D32F2F]/10 border border-[#D32F2F]/20 text-[#D32F2F] text-sm">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <div className="mb-6">
            <GoogleAuthButton onError={(msg) => setError(msg)} buttonText="Continue with Google" />
          </div>

          <div className="relative my-6 text-center">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-semantic-border" />
            </div>
            <span className="relative bg-cream-100 px-3 text-xs text-semantic-textSecondary uppercase font-medium">
              OR
            </span>
          </div>

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
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-sm text-semantic-white font-medium">Password</label>
                <Link
                  href="/forgot-password"
                  className="text-xs text-[#8B5E3C] hover:text-[#6F4A2D] font-medium transition-colors"
                >
                  Forgot Password?
                </Link>
              </div>
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
            <Link href="/register" className="text-[#8B5E3C] hover:text-[#6F4A2D] font-medium">
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

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="w-8 h-8 border-2 border-[#8B5E3C]/30 border-t-[#8B5E3C] rounded-full animate-spin" /></div>}>
      <LoginForm />
    </Suspense>
  )
}
