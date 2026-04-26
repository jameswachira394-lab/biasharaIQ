'use client'
import { useState, useEffect } from 'react'
import { insightsApi } from '@/utils/api'
import { getSeverityColor } from '@/utils/format'
import AppLayout from '@/components/ui/AppLayout'
import { RefreshCw, Lightbulb } from 'lucide-react'

export default function InsightsPage() {
  const [insights, setInsights] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const load = async (refresh = false) => {
    if (refresh) setRefreshing(true)
    try {
      const res = await insightsApi.get()
      setInsights(res.data || [])
    } catch {}
    finally { setLoading(false); setRefreshing(false) }
  }

  useEffect(() => { load() }, [])

  const bySeverity = {
    critical: insights.filter(i => i.severity === 'critical'),
    warning: insights.filter(i => i.severity === 'warning'),
    info: insights.filter(i => i.severity === 'info' || i.severity === 'success'),
  }

  const Section = ({ title, items, color }) => items.length > 0 && (
    <div className="space-y-3">
      <h2 className={`font-display font-semibold text-sm uppercase tracking-wide ${color}`}>{title}</h2>
      {items.map((ins, i) => (
        <div key={i} className={`flex items-start gap-3 p-4 rounded-xl border text-sm animate-fade-in ${getSeverityColor(ins.severity)}`}>
          <span className="text-xl flex-shrink-0">{ins.icon}</span>
          <div>
            <p className="font-medium leading-relaxed">{ins.message}</p>
            <span className="text-xs opacity-60 mt-1 block">{ins.type?.replace(/_/g, ' ')}</span>
          </div>
        </div>
      ))}
    </div>
  )

  return (
    <AppLayout>
      <div className="space-y-6 stagger-children">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display font-bold text-2xl text-slate-100">Financial Insights</h1>
            <p className="text-slate-500 text-sm mt-0.5">Rule-based analysis of your business health</p>
          </div>
          <button onClick={() => load(true)} disabled={refreshing} className="btn-secondary p-2">
            <RefreshCw size={15} className={refreshing ? 'animate-spin' : ''} />
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
            <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mr-2" /> Analyzing your finances...
          </div>
        ) : insights.length === 0 ? (
          <div className="card p-12 text-center">
            <Lightbulb size={32} className="text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400 font-medium">No insights yet</p>
            <p className="text-slate-600 text-sm mt-1">Add transactions to start receiving financial insights</p>
          </div>
        ) : (
          <div className="space-y-6">
            <Section title="⚠ Critical Issues" items={bySeverity.critical} color="text-red-400" />
            <Section title="⚡ Warnings" items={bySeverity.warning} color="text-amber-400" />
            <Section title="ℹ Information" items={bySeverity.info} color="text-blue-400" />
          </div>
        )}

        <div className="card p-4 border-dashed border-[#1e2d3d]">
          <p className="text-xs text-slate-600 text-center">
            Insights are generated from your actual transaction data using rule-based analysis.
            For AI-powered advice, visit the <a href="/ai" className="text-emerald-500 hover:text-emerald-400">AI Advisor</a>.
          </p>
        </div>
      </div>
    </AppLayout>
  )
}
