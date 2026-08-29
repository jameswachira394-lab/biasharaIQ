import { formatCurrency } from '@/utils/format'
import clsx from 'clsx'

export default function ReportSummaryCard({ label, value, isKES = true, color = 'emerald', subtext = '' }) {
  const colors = {
    emerald: 'text-[#2E7D32]',
    red: 'text-[#D32F2F]',
    amber: 'text-[#F9A825]',
    cyan: 'text-[#1A1F71]',
    blue: 'text-[#0A2540]',
  }

  const displayValue = isKES ? formatCurrency(value) : value

  return (
    <div className="card p-5 text-center">
      <p className="text-xs text-semantic-textSecondary uppercase tracking-wide mb-2 font-medium">{label}</p>
      <p className={clsx('font-display font-bold text-2xl', colors[color] || colors.emerald)}>
        {displayValue}
      </p>
      {subtext && <p className="text-xs text-semantic-textSecondary mt-1">{subtext}</p>}
    </div>
  )
}
