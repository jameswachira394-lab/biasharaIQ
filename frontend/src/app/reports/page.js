'use client'
import { useState, useEffect } from 'react'
import { reportsApi } from '@/utils/api'
import { formatCurrency } from '@/utils/format'
import AppLayout from '@/components/ui/AppLayout'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, LineChart, Line, Legend
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#121821] border border-[#0A2540]/30 rounded-lg p-3 text-xs shadow-xl">
      <p className="text-semantic-textSecondary mb-2">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-semantic-white">{p.name}:</span>
          <span className="font-mono font-semibold" style={{ color: p.color }}>KES {Number(p.value).toLocaleString()}</span>
        </div>
      ))}
    </div>
  )
}

export default function ReportsPage() {
  const [monthly, setMonthly] = useState(null)
  const [trend, setTrend] = useState([])
  const [loading, setLoading] = useState(true)
  const [weeks, setWeeks] = useState(8)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [mRes, tRes] = await Promise.all([reportsApi.monthly(), reportsApi.weeklyTrend(weeks)])
        setMonthly(mRes.data)
        setTrend(tRes.data || [])
      } catch { }
      finally { setLoading(false) }
    }
    load()
  }, [weeks])

  if (loading) return (
    <AppLayout>
      <div className="flex items-center justify-center h-64 text-[#9CA3AF] text-sm">
        <div className="w-4 h-4 border-2 border-[#2E7D32] border-t-transparent rounded-full animate-spin mr-2" /> Generating reports...
      </div>
    </AppLayout>
  )

  const s = monthly?.summary || {}

  return (
    <AppLayout>
      <div className="space-y-6 stagger-children">
        <div>
          <h1 className="font-display font-bold text-2xl text-semantic-white">Reports</h1>
          <p className="text-semantic-textSecondary text-sm mt-0.5">{s.month} financial summary</p>
        </div>

        {/* Monthly summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Money In', value: formatCurrency(s.income), color: 'text-[#2E7D32]' },
            { label: 'Money Out', value: formatCurrency(s.expenses), color: 'text-[#D32F2F]' },
            { label: 'Profit', value: formatCurrency(s.profit), color: s.profit >= 0 ? 'text-[#2E7D32]' : 'text-[#D32F2F]' },
            { label: 'Profit Margin', value: `${s.profit_margin || 0}%`, color: (s.profit_margin || 0) > 15 ? 'text-[#2E7D32]' : 'text-[#F9A825]' },
          ].map(({ label, value, color }) => (
            <div key={label} className="card p-4 text-center">
              <p className="text-xs text-semantic-textSecondary uppercase tracking-wide mb-1">{label}</p>
              <p className={`font-display font-bold text-xl ${color}`}>{value}</p>
            </div>
          ))}
        </div>

        {/* Trend chart */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display font-semibold text-semantic-white text-sm uppercase tracking-wide">Income vs Expenses Trend</h2>
            <select className="input-dark w-auto text-xs py-1.5 px-3" value={weeks} onChange={e => setWeeks(Number(e.target.value))}>
              <option value={4}>4 weeks</option>
              <option value={8}>8 weeks</option>
              <option value={12}>12 weeks</option>
              <option value={26}>26 weeks</option>
            </select>
          </div>
          {trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={trend} margin={{ top: 5, right: 5, bottom: 0, left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#0A2540" />
                <XAxis dataKey="week" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v / 1000).toFixed(0)}K`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend formatter={v => <span style={{ color: '#94a3b8', fontSize: 11 }}>{v}</span>} />
                <Bar dataKey="income" name="Money In" fill="#2E7D32" radius={[4, 4, 0, 0]} fillOpacity={0.8} />
                <Bar dataKey="expenses" name="Money Out" fill="#D32F2F" radius={[4, 4, 0, 0]} fillOpacity={0.8} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-48 flex items-center justify-center text-semantic-textMuted text-sm">No data available</div>
          )}
        </div>

        {/* Profit trend */}
        <div className="card p-5">
          <h2 className="font-display font-semibold text-semantic-white text-sm uppercase tracking-wide mb-4">Profit Trend</h2>
          {trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={trend} margin={{ top: 5, right: 5, bottom: 0, left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#0A2540" />
                <XAxis dataKey="week" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v / 1000).toFixed(0)}K`} />
                <Tooltip content={<CustomTooltip />} />
                <Line type="monotone" dataKey="profit" name="Profit" stroke="#2E7D32" strokeWidth={2.5} dot={{ fill: '#2E7D32', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-40 flex items-center justify-center text-semantic-textMuted text-sm">No data available</div>
          )}
        </div>

        {/* Category breakdowns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { title: 'Expense Breakdown', data: monthly?.expense_breakdown, color: '#D32F2F' },
            { title: 'Income Breakdown', data: monthly?.income_breakdown, color: '#2E7D32' },
          ].map(({ title, data, color }) => (
            <div key={title} className="card p-5">
              <h2 className="font-display font-semibold text-semantic-white text-sm uppercase tracking-wide mb-4">{title}</h2>
              {data?.length > 0 ? (
                <div className="space-y-3">
                  {data.map((item, i) => (
                    <div key={i}>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-semantic-textSecondary">{item.category}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-semantic-white font-mono">{formatCurrency(item.amount)}</span>
                          <span className="text-semantic-textSecondary">{item.percentage}%</span>
                        </div>
                      </div>
                      <div className="h-1.5 bg-[#0A2540]/30 rounded-full overflow-hidden">
                        <div className="h-full rounded-full transition-all duration-500"
                          style={{ width: `${item.percentage}%`, background: color, opacity: 0.8 }} />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-32 flex items-center justify-center text-semantic-textMuted text-sm">No data this month</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  )
}
