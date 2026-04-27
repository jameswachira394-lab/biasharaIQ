import { formatCurrency } from '@/utils/format'
import clsx from 'clsx'

export default function ReportSummaryCard({ label, value, isKES = true, color = 'emerald', subtext = '' }) {
  const colors = {
    emerald: 'text-[#10B981]',
    red: 'text-red-400',
    amber: 'text-amber-400',
    cyan: 'text-cyan-400',
    blue: 'text-blue-400',
  }

  const displayValue = isKES ? formatCurrency(value) : value

  return (
    <div className="card p-5 text-center">
      <p className="text-xs text-[#9CA3AF] uppercase tracking-wide mb-2 font-medium">{label}</p>
      <p className={clsx('font-display font-bold text-2xl', colors[color] || colors.emerald)}>
        {displayValue}
      </p>
      {subtext && <p className="text-xs text-[#4B5563] mt-1">{subtext}</p>}
    </div>
  )
}
