'use client'
import { formatCurrency, formatDate } from '@/utils/format'
import Link from 'next/link'
import clsx from 'clsx'

export default function RecentTransactions({ transactions = [], loading = false }) {
  if (loading) {
    return (
      <div className="card p-5">
        <div className="h-4 bg-slate-800 rounded w-36 mb-4 animate-pulse" />
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex justify-between py-3 border-b border-[#0A2540]/30">
            <div className="h-3 bg-slate-800 rounded w-1/3 animate-pulse" />
            <div className="h-3 bg-slate-800 rounded w-20 animate-pulse" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display font-semibold text-semantic-white text-sm uppercase tracking-wide">
          Recent Transactions
        </h2>
        <Link href="/transactions" className="text-xs text-[#2E7D32] hover:text-[#2E7D32] transition-colors">
          View all →
        </Link>
      </div>

      {transactions.length === 0 ? (
        <div className="py-8 text-center">
          <p className="text-semantic-textMuted text-sm">No transactions yet</p>
          <Link href="/transactions" className="text-xs text-[#2E7D32] hover:text-[#2E7D32] mt-1 block">
            Add your first transaction →
          </Link>
        </div>
      ) : (
        <div className="space-y-0">
          {transactions.map((txn, i) => (
            <div key={txn.id || i}
              className="flex items-center justify-between py-2.5 border-b border-[#0A2540]/30 last:border-0 group">
              <div className="flex items-center gap-3 min-w-0">
                <div className={clsx(
                  'w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0',
                  txn.type === 'income'
                    ? 'bg-[#2E7D32]/10 text-[#2E7D32]'
                    : 'bg-[#D32F2F]/10 text-[#D32F2F]'
                )}>
                  {txn.type === 'income' ? '↑' : '↓'}
                </div>
                <div className="min-w-0">
                  <p className="text-sm text-semantic-white truncate">{txn.category}</p>
                  {txn.description && (
                    <p className="text-xs text-semantic-textMuted truncate">{txn.description}</p>
                  )}
                </div>
              </div>
              <div className="text-right flex-shrink-0 ml-3">
                <p className={clsx(
                  'text-sm font-mono font-semibold',
                  txn.type === 'income' ? 'text-[#2E7D32]' : 'text-[#D32F2F]'
                )}>
                  {txn.type === 'income' ? '+' : '-'}{formatCurrency(txn.amount)}
                </p>
                <p className="text-xs text-semantic-textMuted">{formatDate(txn.date)}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
