import clsx from 'clsx'

export default function StatCard({ label, value, sub, icon, trend, color = 'emerald', className }) {
  const colors = {
    emerald: { text: 'text-[#2E7D32]', bg: 'bg-[#2E7D32]/10', border: 'border-[#2E7D32]/25', line: '#2E7D32' },
    red:     { text: 'text-[#D32F2F]', bg: 'bg-[#D32F2F]/8',  border: 'border-[#D32F2F]/15', line: '#D32F2F' },
    amber:   { text: 'text-[#F9A825]', bg: 'bg-[#F9A825]/8',  border: 'border-[#F9A825]/15', line: '#F9A825' },
    blue:    { text: 'text-[#1A1F71]', bg: 'bg-[#1A1F71]/8',  border: 'border-[#1A1F71]/15', line: '#1A1F71' },
    cyan:    { text: 'text-[#0A2540]', bg: 'bg-[#0A2540]/8',  border: 'border-[#0A2540]/15', line: '#0A2540' },
  }
  const c = colors[color] || colors.emerald

  return (
    <div className={clsx('stat-card', c.text, className)} style={{ '--tw-shadow-color': c.line }}>
      <div className={clsx('absolute top-0 left-0 right-0 h-0.5 rounded-t-xl', c.bg)} style={{ background: `linear-gradient(90deg, transparent, ${c.line}60, transparent)` }} />
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-semantic-textSecondary font-medium uppercase tracking-wider mb-1">{label}</p>
          <p className={clsx('text-2xl font-display font-bold truncate', c.text)}>{value}</p>
          {sub && <p className="text-xs text-semantic-textSecondary mt-1 truncate">{sub}</p>}
        </div>
        {icon && (
          <div className={clsx('w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 ml-3', c.bg, 'border', c.border)}>
            <span className={clsx('text-base', c.text)}>{icon}</span>
          </div>
        )}
      </div>
      {trend !== undefined && (
        <div className={clsx('mt-2 text-xs font-medium', trend >= 0 ? 'text-[#2E7D32]' : 'text-[#D32F2F]')}>
          {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}% vs last month
        </div>
      )}
    </div>
  )
}
