'use client'
import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { TrendingUp, Lock, Eye, EyeOff, AlertCircle, CheckCircle, Loader2, ShieldAlert } from 'lucide-react'
import { authApi } from '@/utils/api'

function ResetPasswordForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token') || ''
  const email = searchParams.get('email') || ''

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  // Redirect if token or email is missing
  useEffect(() => {
    if (!token || !email) {
      router.replace('/forgot-password')
    }
  }, [token, email, router])

  const passwordStrength = (() => {
    if (password.length === 0) return null
    if (password.length < 8) return { label: 'Too short', color: '#D32F2F', width: '25%' }
    const hasUpper = /[A-Z]/.test(password)
    const hasNumber = /[0-9]/.test(password)
    const hasSpecial = /[^A-Za-z0-9]/.test(password)
    const score = [hasUpper, hasNumber, hasSpecial].filter(Boolean).length
    if (score === 0) return { label: 'Weak', color: '#F9A825', width: '40%' }
    if (score === 1) return { label: 'Fair', color: '#F9A825', width: '60%' }
    if (score === 2) return { label: 'Good', color: '#2E7D32', width: '80%' }
    return { label: 'Strong', color: '#2E7D32', width: '100%' }
  })()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.')
      return
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match. Please check and try again.')
      return
    }

    setLoading(true)
    try {
      await authApi.resetPassword(token, email, password)
      setSuccess(true)
      // Redirect to login with success banner after short delay
      setTimeout(() => router.push('/login?reset=success'), 2500)
    } catch (err) {
      const msg = err.response?.data?.detail
      setError(msg || 'This reset link is invalid or has expired. Please request a new one.')
    } finally {
      setLoading(false)
    }
  }

  if (!token || !email) return null

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-cream-300">
      <div className="w-full max-w-md animate-fade-in">

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
          <p className="text-semantic-textSecondary text-sm">Financial intelligence for Kenyan businesses 🇰🇪</p>
        </div>

        {/* Card */}
        <div className="card p-8">

          {success ? (
            /* ── Success State ── */
            <div className="text-center py-4">
              <div className="w-16 h-16 rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center mx-auto mb-5">
                <CheckCircle size={32} className="text-green-400" />
              </div>
              <h1 className="font-display font-bold text-xl text-semantic-white mb-3">Password reset!</h1>
              <p className="text-semantic-textSecondary text-sm leading-relaxed mb-4">
                Your password has been reset successfully. Redirecting you to login…
              </p>
              <div className="w-6 h-6 border-2 border-[#8B5E3C]/30 border-t-[#8B5E3C] rounded-full animate-spin mx-auto" />
            </div>
          ) : (
            /* ── Form State ── */
            <>
              <div className="mb-7">
                <div className="w-12 h-12 rounded-xl bg-[#8B5E3C]/10 border border-[#8B5E3C]/30 flex items-center justify-center mb-4">
                  <Lock size={22} className="text-[#8B5E3C]" />
                </div>
                <h1 className="font-display font-bold text-xl text-semantic-white mb-2">Create new password</h1>
                <p className="text-semantic-textSecondary text-sm">
                  Choose a strong password for{' '}
                  <span className="text-[#8B5E3C] font-medium">{email}</span>.
                </p>
              </div>

              {error && (
                <div className="mb-5 flex items-start gap-2 p-3 rounded-lg bg-[#D32F2F]/10 border border-[#D32F2F]/20 text-[#D32F2F] text-sm">
                  <ShieldAlert size={16} className="flex-shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* New Password */}
                <div>
                  <label htmlFor="new-password" className="block text-sm text-semantic-white mb-1.5 font-medium">
                    New Password
                  </label>
                  <div className="relative">
                    <input
                      id="new-password"
                      type={showPw ? 'text' : 'password'}
                      className="input-dark pr-10"
                      placeholder="At least 8 characters"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      autoComplete="new-password"
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
                  {/* Strength bar */}
                  {passwordStrength && (
                    <div className="mt-2">
                      <div className="h-1 rounded-full bg-white/10 overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all duration-300"
                          style={{ width: passwordStrength.width, backgroundColor: passwordStrength.color }}
                        />
                      </div>
                      <p className="text-xs mt-1" style={{ color: passwordStrength.color }}>
                        {passwordStrength.label}
                      </p>
                    </div>
                  )}
                </div>

                {/* Confirm Password */}
                <div>
                  <label htmlFor="confirm-password" className="block text-sm text-semantic-white mb-1.5 font-medium">
                    Confirm New Password
                  </label>
                  <div className="relative">
                    <input
                      id="confirm-password"
                      type={showConfirm ? 'text' : 'password'}
                      className="input-dark pr-10"
                      placeholder="Repeat your password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      autoComplete="new-password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirm(!showConfirm)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-semantic-textSecondary hover:text-semantic-white"
                    >
                      {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {/* Match indicator */}
                  {confirmPassword.length > 0 && (
                    <p className={`text-xs mt-1.5 ${password === confirmPassword ? 'text-green-400' : 'text-[#D32F2F]'}`}>
                      {password === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match'}
                    </p>
                  )}
                </div>

                <button
                  type="submit"
                  id="reset-password-submit-btn"
                  className="btn-primary w-full justify-center py-3 gap-2"
                  disabled={loading || (confirmPassword.length > 0 && password !== confirmPassword)}
                >
                  {loading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Resetting password…
                    </>
                  ) : (
                    'Reset Password'
                  )}
                </button>
              </form>

              <div className="mt-6 text-center">
                <Link
                  href="/forgot-password"
                  className="text-sm text-semantic-textSecondary hover:text-semantic-white transition-colors"
                >
                  Request a new reset link
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-[#8B5E3C]/30 border-t-[#8B5E3C] rounded-full animate-spin" />
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  )
}
