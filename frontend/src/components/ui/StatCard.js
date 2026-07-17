import clsx from 'clsx'

export default function StatCard({ label, value, sub, icon, trend, color = 'emerald', className }) {
  const colors = {
    emerald: { text: 'text-semantic-success', bg: 'bg-semantic-success/10', border: 'border-semantic-success/20', line: '#4A7C59' },
    red: { text: 'text-semantic-error', bg: 'bg-semantic-error/10', border: 'border-semantic-error/20', line: '#C0392B' },
    amber: { text: 'text-semantic-accentGold', bg: 'bg-semantic-accentGold/10', border: 'border-semantic-accentGold/20', line: '#C4A484' },
    blue: { text: 'text-semantic-accentBlue', bg: 'bg-semantic-accentBlue/10', border: 'border-semantic-accentBlue/20', line: '#8B5E3C' },
    purple: { text: 'text-semantic-accentPurple', bg: 'bg-semantic-accentPurple/10', border: 'border-semantic-accentPurple/20', line: '#A67B5B' },
  }
  const c = colors[color] || colors.blue

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
        <div className={clsx('mt-2 text-xs font-medium', trend >= 0 ? 'text-semantic-success' : 'text-semantic-error')}>
          {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}% vs last month
        </div>
      )}
    </div>
  )
}
