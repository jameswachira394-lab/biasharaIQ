'use client'
import { useState, useEffect } from 'react'
import { paymentApi } from '@/utils/api'
import { useAuth } from '@/context/AuthContext'
import { X, Smartphone, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'

export default function UpgradeModal({ isOpen, onClose }) {
  const { user, updateUser } = useAuth()
  const [phone, setPhone] = useState(user?.phone || '')
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState('input') // input, pending, success, error
  const [checkoutId, setCheckoutId] = useState(null)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleInitiate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    // Clean phone number input
    let formattedPhone = phone.trim().replace(/\s+/g, '')
    if (!formattedPhone) {
      setError('Phone number is required')
      setLoading(false)
      return
    }

    try {
      const res = await paymentApi.initiate({ phone: formattedPhone, amount: 499 })
      setCheckoutId(res.data.checkout_id)
      setStep('pending')
      startPolling(res.data.checkout_id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initiate M-Pesa payment')
      setLoading(false)
    }
  }

  const startPolling = (id) => {
    let attempts = 0
    const interval = setInterval(async () => {
      attempts++
      if (attempts > 30) { // 2 minutes
        clearInterval(interval)
        setStep('error')
        setError('Payment verification timed out. Please check your phone or contact support.')
        return
      }

      try {
        const res = await paymentApi.status(id)
        if (res.data.status === 'completed') {
          clearInterval(interval)
          setStep('success')
          updateUser({ plan: 'PRO' })
        } else if (res.data.status === 'failed') {
          clearInterval(interval)
          setStep('error')
          setError('Transaction failed or was cancelled. Please try again.')
        }
      } catch (err) {
        // Keep polling
      }
    }, 4000)
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />
      
      <div className="card w-full max-w-md relative z-10 p-8 animate-fade-in border border-[#2E7D32]/20 shadow-[0_0_50px_-12px_rgba(46,125,50,0.15)] bg-gradient-to-b from-[#0A2540]/10 to-[#121821]">
        <button onClick={onClose} className="absolute top-4 right-4 text-semantic-textMuted hover:text-white transition-colors">
          <X size={20} />
        </button>

        {step === 'input' && (
          <form onSubmit={handleInitiate} className="text-center">
            <div className="w-16 h-16 rounded-full bg-[#2E7D32]/10 border border-[#2E7D32]/20 flex items-center justify-center mx-auto mb-6 shadow-[0_0_20px_rgba(46,125,50,0.1)]">
              <Smartphone className="text-[#2E7D32] animate-pulse" size={32} />
            </div>
            <h2 className="text-xl font-display font-bold text-semantic-white mb-2">Upgrade to Pro</h2>
            <p className="text-sm text-semantic-textSecondary mb-6">
              Enter your M-Pesa phone number below to initiate a secure instant payment.
            </p>

            <div className="text-left mb-6">
              <label className="block text-xs font-semibold text-semantic-textSecondary uppercase tracking-wider mb-2">
                M-Pesa Phone Number
              </label>
              <input
                type="tel"
                required
                className="input-dark text-lg py-3 tracking-widest text-center border-[#0A2540]/50 focus:border-[#2E7D32]/50"
                placeholder="e.g. 0712345678 or 2547XXXXXXXX"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
              <p className="text-[10px] text-semantic-textMuted mt-2 text-center">
                A prompt will appear on your phone asking for your M-Pesa PIN.
              </p>
            </div>

            {error && (
              <div className="mb-6 p-3 rounded-lg bg-semantic-error/10 border border-semantic-error/20 text-semantic-error text-xs flex items-center gap-2 text-left">
                <AlertCircle size={14} className="shrink-0" /> {error}
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading} 
              className="w-full py-4 rounded-lg font-bold text-white transition-all bg-[#2E7D32] hover:bg-[#1B5E20] hover:shadow-[0_0_20px_rgba(46,125,50,0.4)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <><Loader2 className="animate-spin" size={18} /> Sending Push Prompt...</>
              ) : (
                'Pay with M-Pesa'
              )}
            </button>
          </form>
        )}

        {step === 'pending' && (
          <div className="text-center py-6">
            <div className="relative w-24 h-24 mx-auto mb-8 flex items-center justify-center">
              <div className="absolute inset-0 border-4 border-[#2E7D32]/20 border-t-[#2E7D32] rounded-full animate-spin" />
              <Smartphone className="text-[#2E7D32]" size={36} />
            </div>
            <h2 className="text-xl font-display font-bold text-semantic-white mb-2">
              Awaiting Payment
            </h2>
            <p className="text-sm text-semantic-textSecondary px-2">
              Please check your phone for the M-Pesa prompt and enter your <strong>PIN</strong> to complete the upgrade.
            </p>
            <div className="mt-8 p-3 rounded-lg bg-[#2E7D32]/5 border border-[#2E7D32]/10 inline-block text-[11px] text-[#2E7D32] font-semibold animate-pulse">
              Waiting for Safaricom confirmation...
            </div>
          </div>
        )}

        {step === 'success' && (
          <div className="text-center py-6 animate-fade-in">
            <div className="w-16 h-16 rounded-full bg-[#2E7D32]/15 border border-[#2E7D32]/30 flex items-center justify-center mx-auto mb-6 shadow-[0_0_30px_rgba(46,125,50,0.2)]">
              <CheckCircle2 className="text-[#4CAF50]" size={40} />
            </div>
            <h2 className="text-2xl font-display font-bold text-semantic-white mb-2">Upgrade Successful!</h2>
            <p className="text-sm text-semantic-textSecondary mb-8">
              Welcome to <strong>BiasharaIQ Pro</strong>. Your advanced business intelligence dashboard is now active.
            </p>
            <button 
              onClick={onClose} 
              className="w-full py-3.5 rounded-lg font-bold text-white transition-all bg-[#2E7D32] hover:bg-[#1B5E20] shadow-[0_0_20px_rgba(46,125,50,0.3)] flex justify-center"
            >
              Go to Dashboard
            </button>
          </div>
        )}

        {step === 'error' && (
          <div className="text-center py-6 animate-fade-in">
            <div className="w-16 h-16 rounded-full bg-semantic-error/10 border border-semantic-error/20 flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="text-semantic-error" size={40} />
            </div>
            <h2 className="text-xl font-display font-bold text-semantic-white mb-2">Payment Failed</h2>
            <p className="text-sm text-semantic-textSecondary mb-8 px-4">{error}</p>
            <button 
              onClick={() => setStep('input')} 
              className="w-full py-3.5 rounded-lg font-bold text-white transition-all bg-white/10 hover:bg-white/20 border border-white/10 flex justify-center"
            >
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
