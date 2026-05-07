'use client'
import clsx from 'clsx'

const LEVELS = {
  safe: { label: 'Safe', bg: 'bg-[#2E7D32]/10', border: 'border-[#2E7D32]/30', text: 'text-[#2E7D32]', bar: 'bg-[#2E7D32]', dot: 'bg-[#2E7D32]' },
  warning: { label: 'Warning', bg: 'bg-[#F9A825]/10', border: 'border-[#F9A825]/25', text: 'text-[#F9A825]', bar: 'bg-[#F9A825]', dot: 'bg-[#F9A825]' },
  critical: { label: 'Critical', bg: 'bg-[#D32F2F]/10', border: 'border-[#D32F2F]/25', text: 'text-[#D32F2F]', bar: 'bg-[#D32F2F]', dot: 'bg-[#D32F2F]' },
}

export default function CashFlowIndicator({ survivalDays, riskLevel, dailyRate, message }) {
  const level = LEVELS[riskLevel] || LEVELS.safe

  // Progress bar: 0 = critical (0 days), 100 = safe (90+ days)
  const progress = survivalDays !== null ? Math.min((survivalDays / 90) * 100, 100) : 100

  return (
    <div className={clsx('rounded-xl border p-4', level.bg, level.border)}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className={clsx('w-2 h-2 rounded-full animate-pulse-soft', level.dot)} />
          <span className={clsx('text-xs font-semibold uppercase tracking-wide', level.text)}>
            Cash Flow: {level.label}
          </span>
        </div>
        {survivalDays !== null && (
          <span className={clsx('font-display font-bold text-lg', level.text)}>
            {Math.round(survivalDays)} days
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="h-1.5 bg-black/20 rounded-full overflow-hidden mb-2">
        <div
          className={clsx('h-full rounded-full transition-all duration-700', level.bar)}
          style={{ width: `${progress}%`, opacity: 0.8 }}
        />
      </div>

      <p className={clsx('text-xs leading-relaxed', level.text, 'opacity-80')}>
        {message || `Burning KES ${dailyRate?.toLocaleString() || 0}/day`}
      </p>
    </div>
  )
}
