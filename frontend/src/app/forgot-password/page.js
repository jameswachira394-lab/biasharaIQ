'use client'
import { useState } from 'react'
import Link from 'next/link'
import { TrendingUp, Mail, ArrowLeft, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { authApi } from '@/utils/api'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Basic format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address.')
      return
    }

    setLoading(true)
    try {
      await authApi.forgotPassword(email.trim().toLowerCase())
      setSubmitted(true)
    } catch (err) {
      // Show generic error only for network/server issues — never reveal user existence
      if (!err.response || err.response.status >= 500) {
        setError('Something went wrong. Please try again in a moment.')
      } else {
        // Treat 4xx the same as success to avoid enumeration
        setSubmitted(true)
      }
    } finally {
      setLoading(false)
    }
  }

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

          {submitted ? (
            /* ── Success State ── */
            <div className="text-center py-4">
              <div className="w-16 h-16 rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center mx-auto mb-5">
                <CheckCircle size={32} className="text-green-400" />
              </div>
              <h1 className="font-display font-bold text-xl text-semantic-white mb-3">Check your email</h1>
              <p className="text-semantic-textSecondary text-sm leading-relaxed mb-6">
                If an account exists with <span className="text-[#8B5E3C] font-medium">{email}</span>,
                you will receive a password reset link shortly.
                The link will expire in <strong>15 minutes</strong>.
              </p>
              <p className="text-semantic-textSecondary text-xs mb-6">
                Didn&apos;t receive an email? Check your spam folder, or try again.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-sm text-[#8B5E3C] hover:text-[#6F4A2D] font-medium transition-colors"
              >
                <ArrowLeft size={15} />
                Back to Login
              </Link>
            </div>
          ) : (
            /* ── Form State ── */
            <>
              <div className="mb-7">
                <div className="w-12 h-12 rounded-xl bg-[#8B5E3C]/10 border border-[#8B5E3C]/30 flex items-center justify-center mb-4">
                  <Mail size={22} className="text-[#8B5E3C]" />
                </div>
                <h1 className="font-display font-bold text-xl text-semantic-white mb-2">Forgot your password?</h1>
                <p className="text-semantic-textSecondary text-sm leading-relaxed">
                  Enter the email address associated with your account and we&apos;ll send you a password reset link.
                </p>
              </div>

              {error && (
                <div className="mb-5 flex items-center gap-2 p-3 rounded-lg bg-[#D32F2F]/10 border border-[#D32F2F]/20 text-[#D32F2F] text-sm">
                  <AlertCircle size={16} className="flex-shrink-0" />
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label htmlFor="reset-email" className="block text-sm text-semantic-white mb-1.5 font-medium">
                    Email address
                  </label>
                  <input
                    id="reset-email"
                    type="email"
                    className="input-dark"
                    placeholder="you@business.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    autoComplete="email"
                    required
                  />
                </div>

                <button
                  type="submit"
                  id="send-reset-link-btn"
                  className="btn-primary w-full justify-center py-3 gap-2"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Sending reset link...
                    </>
                  ) : (
                    'Send Reset Link'
                  )}
                </button>
              </form>

              <div className="mt-6 text-center">
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 text-sm text-semantic-textSecondary hover:text-semantic-white transition-colors"
                >
                  <ArrowLeft size={15} />
                  Back to Login
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
