'use client'
import clsx from 'clsx'

const LEVELS = {
  safe:     { label: 'Safe',     bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', text: 'text-emerald-400', bar: 'bg-emerald-500', dot: 'bg-emerald-400' },
  warning:  { label: 'Warning',  bg: 'bg-amber-500/10',   border: 'border-amber-500/25',   text: 'text-amber-400',   bar: 'bg-amber-500',   dot: 'bg-amber-400' },
  critical: { label: 'Critical', bg: 'bg-red-500/10',     border: 'border-red-500/25',     text: 'text-red-400',     bar: 'bg-red-500',     dot: 'bg-red-400' },
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
