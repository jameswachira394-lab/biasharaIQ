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
  success: 'bg-[#2E7D32]/10 border-[#2E7D32]/25 text-[#2E7D32]',
  error: 'bg-[#D32F2F]/10 border-[#D32F2F]/25 text-[#D32F2F]',
  warning: 'bg-[#F9A825]/10 border-[#F9A825]/25 text-[#F9A825]',
  info: 'bg-[#1A1F71]/10 border-[#1A1F71]/25 text-[#1A1F71]',
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
  const error = useCallback((msg) => toast(msg, 'error', 5000), [toast])
  const warning = useCallback((msg) => toast(msg, 'warning'), [toast])
  const info = useCallback((msg) => toast(msg, 'info'), [toast])

  return { toasts, dismiss, toast, success, error, warning, info }
}

export default function SingleToast({ type, message, onClose }) {
  const Icon = ICONS[type] || Info
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      <div className={clsx(
        'flex items-center gap-3 px-4 py-3 rounded-xl border text-sm shadow-xl backdrop-blur pointer-events-auto animate-fade-in max-w-xs',
        STYLES[type] || STYLES.info
      )}>
        <Icon size={15} className="flex-shrink-0" />
        <span className="flex-1">{message}</span>
        <button onClick={onClose} className="opacity-60 hover:opacity-100 ml-1">
          <X size={13} />
        </button>
      </div>
    </div>
  )
}

