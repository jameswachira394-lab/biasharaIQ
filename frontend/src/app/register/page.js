'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/context/AuthContext'
import { TrendingUp, Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react'

const BUSINESS_TYPES = [
  'Retail Shop', 'Restaurant / Cafe', 'Salon / Barbershop', 'Agribusiness',
  'Wholesale', 'Transport / Logistics', 'Technology', 'Consulting', 'Other'
]

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: '', password: '', business_name: '', owner_name: '', phone: '', business_type: ''
  })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { register } = useAuth()
  const router = useRouter()

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) { setError('Password must be at least 8 characters'); return }
    setError('')
    setLoading(true)
    try {
      await register(form)
      router.push('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const benefits = ['Track all money in & out', 'Know your true profit', 'Get AI financial insights', 'Predict cash flow risks']

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10" style={{
      background: 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(34,197,94,0.08) 0%, transparent 60%), #0B0F14'
    }}>
      <div className="w-full max-w-lg animate-fade-in">
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
          <p className="text-semantic-textSecondary text-sm">Start tracking your business finances intelligently</p>
          <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 mt-3">
            {benefits.map((b) => (
              <span key={b} className="flex items-center gap-1 text-xs text-semantic-textSecondary">
                <CheckCircle size={11} className="text-[#2E7D32]" /> {b}
              </span>
            ))}
          </div>
        </div>

        {/* Card */}
        <div className="card p-8">
          {error && (
            <div className="mb-5 flex items-center gap-2 p-3 rounded-lg bg-[#D32F2F]/10 border border-[#D32F2F]/20 text-[#D32F2F] text-sm">
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-semantic-white mb-1.5 font-medium">Business Name *</label>
                <input className="input-dark" placeholder="Mama Jane's Shop" value={form.business_name} onChange={set('business_name')} required />
              </div>
              <div>
                <label className="block text-sm text-semantic-white mb-1.5 font-medium">Your Name</label>
                <input className="input-dark" placeholder="Jane Wanjiku" value={form.owner_name} onChange={set('owner_name')} />
              </div>
            </div>

            <div>
              <label className="block text-sm text-semantic-white mb-1.5 font-medium">Business Type</label>
              <select className="input-dark" value={form.business_type} onChange={set('business_type')}>
                <option value="">Select type...</option>
                {BUSINESS_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm text-semantic-white mb-1.5 font-medium">Email *</label>
              <input type="email" className="input-dark" placeholder="you@business.com" value={form.email} onChange={set('email')} required />
            </div>

            <div>
              <label className="block text-sm text-semantic-white mb-1.5 font-medium">Phone (Optional)</label>
              <input className="input-dark" placeholder="+254 7XX XXX XXX" value={form.phone} onChange={set('phone')} />
            </div>

            <div>
              <label className="block text-sm text-semantic-white mb-1.5 font-medium">Password *</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  className="input-dark pr-10"
                  placeholder="Min. 8 characters"
                  value={form.password}
                  onChange={set('password')}
                  required
                />
                <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-semantic-textSecondary hover:text-semantic-white">
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button type="submit" className="btn-primary w-full justify-center py-3 mt-2" disabled={loading}>
              {loading
                ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Creating account...</>
                : 'Create Free Account'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-[#9CA3AF]">
            Already have an account?{' '}
            <Link href="/login" className="text-[#2E7D32] hover:text-[#2E7D32] font-medium">Sign in</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
