import clsx from 'clsx'

export default function StatCard({ label, value, sub, icon, trend, color = 'emerald', className }) {
  const colors = {
    emerald: { text: 'text-[#10B981]', bg: 'bg-[#0F6B4F]/10', border: 'border-[#0F6B4F]/25', line: '#10B981' },
    red:     { text: 'text-red-400',   bg: 'bg-red-500/8',    border: 'border-red-500/15',   line: '#ef4444' },
    amber:   { text: 'text-amber-400', bg: 'bg-amber-500/8',  border: 'border-amber-500/15', line: '#f59e0b' },
    blue:    { text: 'text-blue-400',  bg: 'bg-blue-500/8',   border: 'border-blue-500/15',  line: '#3b82f6' },
    cyan:    { text: 'text-cyan-400',  bg: 'bg-cyan-500/8',   border: 'border-cyan-500/15',  line: '#06b6d4' },
  }
  const c = colors[color] || colors.emerald

  return (
    <div className={clsx('stat-card', c.text, className)} style={{ '--tw-shadow-color': c.line }}>
      <div className={clsx('absolute top-0 left-0 right-0 h-0.5 rounded-t-xl', c.bg)} style={{ background: `linear-gradient(90deg, transparent, ${c.line}60, transparent)` }} />
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-[#9CA3AF] font-medium uppercase tracking-wider mb-1">{label}</p>
          <p className={clsx('text-2xl font-display font-bold truncate', c.text)}>{value}</p>
          {sub && <p className="text-xs text-[#9CA3AF] mt-1 truncate">{sub}</p>}
        </div>
        {icon && (
          <div className={clsx('w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ml-3', c.bg, 'border', c.border)}>
            <span className={clsx('text-base', c.text)}>{icon}</span>
          </div>
        )}
      </div>
      {trend !== undefined && (
        <div className={clsx('mt-2 text-xs font-medium', trend >= 0 ? 'text-[#10B981]' : 'text-red-400')}>
          {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}% vs last month
        </div>
      )}
    </div>
  )
}
