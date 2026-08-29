'use client'
import { useState } from 'react'
import { AlertCircle, CheckCircle2, Mail, Loader2, Clock } from 'lucide-react'
import api from '@/utils/api'

export default function EmailVerificationForm({ email, onSuccess, showResendOption = true }) {
    const [code, setCode] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState(false)
    const [resendLoading, setResendLoading] = useState(false)
    const [resendCooldown, setResendCooldown] = useState(0)
    const [codeLength] = useState(6)

    // Auto-format code input (numbers only)
    const handleCodeChange = (e) => {
        const value = e.target.value.replace(/\D/g, '').slice(0, codeLength)
        setCode(value)
    }

    // Handle resend verification code
    const handleResendCode = async () => {
        setResendLoading(true)
        setError('')
        try {
            await api.post('/auth/send-verification', { email })
            setResendLoading(false)
            setResendCooldown(60)
            // Start countdown
            const interval = setInterval(() => {
                setResendCooldown((prev) => {
                    if (prev <= 1) {
                        clearInterval(interval)
                        return 0
                    }
                    return prev - 1
                })
            }, 1000)
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to resend code. Please try again.')
            setResendLoading(false)
        }
    }

    // Handle verify code submission
    const handleSubmit = async (e) => {
        e.preventDefault()
        if (code.length !== codeLength) {
            setError(`Please enter a ${codeLength}-digit code`)
            return
        }

        setLoading(true)
        setError('')
        try {
            await api.post('/auth/verify-email', { email, code })
            setSuccess(true)
            if (onSuccess) {
                setTimeout(onSuccess, 1500)
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Invalid or expired code. Please try again.')
            setCode('')
        } finally {
            setLoading(false)
        }
    }

    if (success) {
        return (
            <div className="text-center py-6">
                <div className="w-16 h-16 rounded-full bg-[#4CAF50]/10 flex items-center justify-center mx-auto mb-6">
                    <CheckCircle2 className="text-[#4CAF50]" size={40} />
                </div>
                <h2 className="text-xl font-display font-bold text-semantic-white mb-2">Email Verified! 🎉</h2>
                <p className="text-sm text-semantic-textSecondary">
                    Your account is now active.
                </p>
            </div>
        )
    }

    return (
        <>
            {/* Email Info */}
            <div className="mb-6 p-4 rounded-lg bg-[#8B5E3C]/5 border border-[#8B5E3C]/10">
                <div className="flex items-center gap-3">
                    <Mail size={18} className="text-[#8B5E3C]" />
                    <div className="text-sm">
                        <p className="text-semantic-textSecondary">Verification code sent to:</p>
                        <p className="text-semantic-white font-medium">{email}</p>
                    </div>
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="mb-5 flex items-center gap-2 p-3 rounded-lg bg-[#D32F2F]/10 border border-[#D32F2F]/20 text-[#D32F2F] text-sm">
                    <AlertCircle size={16} /> {error}
                </div>
            )}

            {/* Verification Code Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm text-semantic-white mb-2 font-medium">
                        Enter 6-Digit Code
                    </label>
                    <input
                        type="text"
                        inputMode="numeric"
                        maxLength={codeLength}
                        className="input-dark text-center text-2xl tracking-widest font-mono py-4"
                        placeholder="000000"
                        value={code}
                        onChange={handleCodeChange}
                        disabled={loading}
                        required
                    />
                    <p className="text-xs text-semantic-textSecondary mt-2">
                        Check your email for the code (also check spam folder)
                    </p>
                </div>

                <button
                    type="submit"
                    className="btn-primary w-full justify-center py-3"
                    disabled={loading || code.length !== codeLength}
                >
                    {loading ? (
                        <><Loader2 className="animate-spin" size={18} /> Verifying...</>
                    ) : (
                        'Verify Email'
                    )}
                </button>
            </form>

            {/* Resend Code */}
            {showResendOption && (
                <div className="mt-6 text-center">
                    <p className="text-sm text-semantic-textSecondary mb-3">Didn&apos;t receive the code?</p>
                    <button
                        onClick={handleResendCode}
                        disabled={resendLoading || resendCooldown > 0}
                        className="text-[#8B5E3C] hover:text-[#6F4A2D] font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                        {resendCooldown > 0 ? (
                            <>
                                <Clock size={14} />
                                Resend in {resendCooldown}s
                            </>
                        ) : resendLoading ? (
                            <>
                                <Loader2 className="animate-spin" size={14} />
                                Sending...
                            </>
                        ) : (
                            'Resend Code'
                        )}
                    </button>
                </div>
            )}
        </>
    )
}
