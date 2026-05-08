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
    try {
      const res = await paymentApi.initiate({ phone, amount: 499 })
      setCheckoutId(res.data.checkout_id)
      setStep('pending')
      startPolling(res.data.checkout_id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initiate payment')
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
        setError('Payment verification timed out. Please check your M-Pesa or contact support.')
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
          setError('Transaction failed. Please try again.')
        }
      } catch (err) {
        // Continue polling
      }
    }, 4000)
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />
      
      <div className="card w-full max-w-md relative z-10 p-8 animate-fade-in">
        <button onClick={onClose} className="absolute top-4 right-4 text-semantic-textMuted hover:text-white">
          <X size={20} />
        </button>

        {step === 'input' && (
          <form onSubmit={handleInitiate} className="text-center">
            <div className="w-16 h-16 rounded-full bg-semantic-accentBlue/10 flex items-center justify-center mx-auto mb-6">
              <Smartphone className="text-semantic-accentBlue" size={32} />
            </div>
            <h2 className="text-xl font-display font-bold text-semantic-white mb-2">Upgrade to Pro</h2>
            <p className="text-sm text-semantic-textSecondary mb-8">
              Confirm your M-Pesa number to receive a payment prompt for <strong>KES 499</strong>.
            </p>

            <div className="text-left mb-6">
              <label className="block text-xs font-semibold text-semantic-textSecondary uppercase tracking-wider mb-2">
                M-Pesa Phone Number
              </label>
              <input
                type="tel"
                required
                className="input-dark text-lg py-3"
                placeholder="e.g. 0712345678"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>

            {error && (
              <div className="mb-6 p-3 rounded-lg bg-semantic-error/10 border border-semantic-error/20 text-semantic-error text-xs flex items-center gap-2">
                <AlertCircle size={14} /> {error}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full py-3.5 justify-center text-base">
              {loading ? <><Loader2 className="animate-spin" size={18} /> Sending Prompt...</> : 'Send STK Push'}
            </button>
          </form>
        )}

        {step === 'pending' && (
          <div className="text-center py-6">
            <div className="w-20 h-20 border-4 border-semantic-accentBlue/20 border-t-semantic-accentBlue rounded-full animate-spin mx-auto mb-8" />
            <h2 className="text-xl font-display font-bold text-semantic-white mb-2">Awaiting Payment</h2>
            <p className="text-sm text-semantic-textSecondary">
              Please check your phone for the M-Pesa prompt and enter your PIN to complete the payment.
            </p>
            <p className="mt-8 text-xs text-semantic-textMuted italic">
              Verification may take up to 30 seconds...
            </p>
          </div>
        )}

        {step === 'success' && (
          <div className="text-center py-6">
            <div className="w-16 h-16 rounded-full bg-semantic-success/10 flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="text-semantic-success" size={40} />
            </div>
            <h2 className="text-xl font-display font-bold text-semantic-white mb-2">Payment Successful!</h2>
            <p className="text-sm text-semantic-textSecondary mb-8">
              Welcome to <strong>BiasharaIQ Pro</strong>. Your advanced financial intelligence features are now active.
            </p>
            <button onClick={onClose} className="btn-primary w-full py-3 justify-center">
              Go to Dashboard
            </button>
          </div>
        )}

        {step === 'error' && (
          <div className="text-center py-6">
            <div className="w-16 h-16 rounded-full bg-semantic-error/10 flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="text-semantic-error" size={40} />
            </div>
            <h2 className="text-xl font-display font-bold text-semantic-white mb-2">Payment Error</h2>
            <p className="text-sm text-semantic-textSecondary mb-8">{error}</p>
            <button onClick={() => setStep('input')} className="btn-secondary w-full py-3 justify-center">
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
