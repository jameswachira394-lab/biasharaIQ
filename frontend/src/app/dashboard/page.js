'use client'
import { useState, useEffect } from 'react'
import { useDashboard } from '@/hooks/useDashboard'
import { useCategories } from '@/hooks/useCategories'
import { formatCurrency, getSeverityColor } from '@/utils/format'
import AppLayout from '@/components/ui/AppLayout'
import StatCard from '@/components/ui/StatCard'
import CashFlowIndicator from '@/components/dashboard/CashFlowIndicator'
import QuickAddTransaction from '@/components/dashboard/QuickAddTransaction'
import RecentTransactions from '@/components/transactions/RecentTransactions'
import { PageLoader } from '@/components/ui/Spinner'
import { useAuth } from '@/context/AuthContext'
import { transactionsApi } from '@/utils/api'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'
import { RefreshCw, TrendingUp, TrendingDown, DollarSign, Activity, AlertTriangle, Bot } from 'lucide-react'
import Link from 'next/link'


const COLORS = ['#22c55e','#06b6d4','#f59e0b','#8b5cf6','#ef4444','#ec4899']

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#111827] border border-[#1e2d3d] rounded-lg p-3 text-xs shadow-xl">
      <p className="text-slate-400 mb-2">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-slate-300">{p.name}:</span>
          <span className="font-mono font-semibold" style={{ color: p.color }}>
            KES {Number(p.value).toLocaleString()}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuth()
  const { data, loading, error, refetch } = useDashboard()
  const { categories } = useCategories()
  const [recentTxns, setRecentTxns] = useState([])
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    transactionsApi.list({ limit: 8 })
      .then(r => setRecentTxns(r.data.items || []))
      .catch(() => {})
  }, [data])

  const handleRefresh = async () => {
    setRefreshing(true)
    await refetch()
    setRefreshing(false)
  }

  const handleTransactionAdded = async () => {
    await refetch()
    const r = await transactionsApi.list({ limit: 8 })
    setRecentTxns(r.data.items || [])
  }

  if (loading) return <AppLayout><PageLoader message="Loading your financial data..." /></AppLayout>

  if (error) return (
    <AppLayout>
      <div className="flex flex-col items-center justify-center h-64 gap-3">
        <p className="text-red-400">{error}</p>
        <button onClick={handleRefresh} className="btn-secondary">Retry</button>
      </div>
    </AppLayout>
  )

  const { metrics, insights, weekly_trend } = data || {}
  const m = metrics || {}
  const risk = m.cash_flow?.risk_level || 'safe'
  const criticals = (insights || []).filter(i => i.severity === 'critical')

  return (
    <AppLayout>
      <div className="space-y-6 stagger-children">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-display font-bold text-2xl text-slate-100">
              {user?.business_name || 'Dashboard'}
            </h1>
            <p className="text-slate-500 text-sm mt-0.5">
              {new Date().toLocaleDateString('en-KE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleRefresh} disabled={refreshing}
              className="btn-secondary p-2.5" title="Refresh data">
              <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
            </button>
            <Link href="/transactions" className="btn-primary hidden sm:flex">
              + Add Transaction
            </Link>
          </div>
        </div>

        {/* Critical alerts banner */}
        {criticals.length > 0 && (
          <div className="space-y-2">
            {criticals.map((ins, idx) => (
              <div key={idx} className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/25 animate-fade-in">
                <AlertTriangle size={16} className="text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-red-300 font-medium">{ins.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* KPI Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Money In (Month)"
            value={formatCurrency(m.this_month?.income)}
            icon={<TrendingUp size={16} />}
            color="emerald"
          />
          <StatCard
            label="Money Out (Month)"
            value={formatCurrency(m.this_month?.expenses)}
            icon={<TrendingDown size={16} />}
            color="red"
          />
          <StatCard
            label="Profit (Month)"
            value={formatCurrency(m.this_month?.profit)}
            sub={`${m.this_month?.profit_margin || 0}% margin`}
            icon={<DollarSign size={16} />}
            color={(m.this_month?.profit || 0) >= 0 ? 'emerald' : 'red'}
          />
          <StatCard
            label="Cash Runway"
            value={m.cash_flow?.survival_days != null ? `${Math.round(m.cash_flow.survival_days)} days` : 'N/A'}
            sub={`KES ${(m.cash_flow?.daily_spending_rate || 0).toLocaleString()}/day avg`}
            icon={<Activity size={16} />}
            color={risk === 'safe' ? 'emerald' : risk === 'warning' ? 'amber' : 'red'}
          />
        </div>

        {/* Cash flow indicator */}
        {m.cash_flow && (
          <CashFlowIndicator
            survivalDays={m.cash_flow.survival_days}
            riskLevel={m.cash_flow.risk_level}
            dailyRate={m.cash_flow.daily_spending_rate}
            message={m.cash_flow.message}
          />
        )}

        {/* Charts + Quick Add */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trend chart */}
          <div className="card p-5 lg:col-span-2">
            <h2 className="font-display font-semibold text-slate-200 mb-4 text-sm uppercase tracking-wide">
              8-Week Income vs Expenses
            </h2>
            {weekly_trend?.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={weekly_trend} margin={{ top: 5, right: 5, bottom: 0, left: -10 }}>
                  <defs>
                    <linearGradient id="gIncome" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gExpense" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e2d3d" />
                  <XAxis dataKey="week" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v / 1000).toFixed(0)}K`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="income" name="Money In" stroke="#22c55e" strokeWidth={2} fill="url(#gIncome)" />
                  <Area type="monotone" dataKey="expenses" name="Money Out" stroke="#ef4444" strokeWidth={2} fill="url(#gExpense)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-52 flex flex-col items-center justify-center text-slate-600 text-sm gap-2">
                <p>No transaction data yet</p>
                <Link href="/transactions" className="text-emerald-500 hover:text-emerald-400 text-xs">
                  Add your first transaction →
                </Link>
              </div>
            )}
          </div>

          {/* Expense pie */}
          <div className="card p-5">
            <h2 className="font-display font-semibold text-slate-200 mb-4 text-sm uppercase tracking-wide">
              Expenses by Category
            </h2>
            {m.expense_breakdown?.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={140}>
                  <PieChart>
                    <Pie data={m.expense_breakdown} dataKey="amount" nameKey="category"
                      cx="50%" cy="50%" outerRadius={60} innerRadius={35}>
                      {m.expense_breakdown.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={v => [`KES ${v.toLocaleString()}`, '']}
                      contentStyle={{ background: '#111827', border: '1px solid #1e2d3d', borderRadius: 8, fontSize: 11 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                <div className="space-y-2 mt-2">
                  {m.expense_breakdown.slice(0, 5).map((item, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-1.5">
                        <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: COLORS[i % COLORS.length] }} />
                        <span className="text-slate-400 truncate max-w-[110px]">{item.category}</span>
                      </div>
                      <span className="text-slate-300 font-mono font-medium tabular-nums">{item.percentage}%</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-48 flex items-center justify-center text-slate-600 text-sm">No expense data yet</div>
            )}
          </div>
        </div>

        {/* Bottom row: Quick Add + Recent Transactions + Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick add */}
          <div className="lg:col-span-1">
            <QuickAddTransaction onAdded={handleTransactionAdded} categories={categories} />
          </div>

          {/* Recent transactions */}
          <div className="lg:col-span-2">
            <RecentTransactions transactions={recentTxns} />
          </div>
        </div>

        {/* Insights strip */}
        {insights?.length > 0 && (
          <div className="card p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display font-semibold text-slate-200 text-sm uppercase tracking-wide">
                System Insights
              </h2>
              <Link href="/insights" className="text-xs text-emerald-400 hover:text-emerald-300">
                View all →
              </Link>
            </div>
            <div className="grid sm:grid-cols-2 gap-3">
              {insights.slice(0, 4).map((ins, i) => (
                <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border text-sm ${getSeverityColor(ins.severity)}`}>
                  <span className="text-base flex-shrink-0">{ins.icon}</span>
                  <p className="leading-relaxed text-xs">{ins.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI CTA */}
        <div className="card p-5 border-dashed border-[#2d4a6a] bg-gradient-to-r from-blue-500/5 to-transparent">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
              <Bot size={18} className="text-blue-400" />
            </div>
            <div className="flex-1">
              <p className="font-display font-semibold text-slate-200 text-sm">Ask the AI Advisor</p>
              <p className="text-xs text-slate-500 mt-0.5">
                "Why am I losing money?" — Get answers based on your real data
              </p>
            </div>
            <Link href="/ai" className="btn-primary text-sm flex-shrink-0 hidden sm:flex">
              Open AI →
            </Link>
          </div>
        </div>

        {/* All-time totals */}
        <div className="card p-5">
          <h2 className="font-display font-semibold text-slate-200 text-sm uppercase tracking-wide mb-4">
            All-Time Summary
          </h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-slate-500 mb-1">Total Money In</p>
              <p className="font-display font-bold text-emerald-400">{formatCurrency(m.all_time?.income)}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Total Money Out</p>
              <p className="font-display font-bold text-red-400">{formatCurrency(m.all_time?.expenses)}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Net Profit</p>
              <p className={`font-display font-bold ${(m.all_time?.profit || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {formatCurrency(m.all_time?.profit)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
