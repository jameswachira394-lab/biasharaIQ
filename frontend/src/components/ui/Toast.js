'use client'
import { useState, useCallback } from 'react'
import { CheckCircle, AlertCircle, X, Info, AlertTriangle } from 'lucide-react'
import clsx from 'clsx'

const ICONS = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
}

const STYLES = {
  success: 'bg-[#0F6B4F]/10 border-[#0F6B4F]/25 text-[#10B981]',
  error:   'bg-red-500/10 border-red-500/25 text-red-300',
  warning: 'bg-amber-500/10 border-amber-500/25 text-amber-300',
  info:    'bg-blue-500/10 border-blue-500/25 text-blue-300',
}

export function Toast({ toasts, dismiss }) {
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map(t => {
        const Icon = ICONS[t.type] || Info
        return (
          <div key={t.id}
            className={clsx(
              'flex items-center gap-3 px-4 py-3 rounded-xl border text-sm shadow-xl backdrop-blur pointer-events-auto animate-fade-in max-w-xs',
              STYLES[t.type] || STYLES.info
            )}>
            <Icon size={15} className="flex-shrink-0" />
            <span className="flex-1">{t.message}</span>
            <button onClick={() => dismiss(t.id)} className="opacity-60 hover:opacity-100 ml-1">
              <X size={13} />
            </button>
          </div>
        )
      })}
    </div>
  )
}

let _id = 0
export function useToast() {
  const [toasts, setToasts] = useState([])

  const dismiss = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const toast = useCallback((message, type = 'info', duration = 3500) => {
    const id = ++_id
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => dismiss(id), duration)
  }, [dismiss])

  const success = useCallback((msg) => toast(msg, 'success'), [toast])
  const error   = useCallback((msg) => toast(msg, 'error', 5000), [toast])
  const warning = useCallback((msg) => toast(msg, 'warning'), [toast])
  const info    = useCallback((msg) => toast(msg, 'info'), [toast])

  return { toasts, dismiss, toast, success, error, warning, info }
}
