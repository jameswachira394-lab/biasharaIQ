'use client'
import { useState } from 'react'
import { transactionsApi, categoriesApi } from '@/utils/api'
import { TrendingUp, TrendingDown, Plus } from 'lucide-react'
import clsx from 'clsx'

export default function QuickAddTransaction({ onAdded, categories = [] }) {
  const [type, setType] = useState('income')
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const filteredCats = categories.filter(c => c.type === type)

  const submit = async (e) => {
    e.preventDefault()
    if (!amount || Number(amount) <= 0) { setError('Enter a valid amount'); return }
    if (!category) { setError('Pick a category'); return }
    setLoading(true)
    setError('')
    try {
      await transactionsApi.create({
        amount: Number(amount),
        type,
        category,
        date: new Date().toISOString(),
        description: description || undefined,
      })
      setAmount('')
      setCategory('')
      setDescription('')
      onAdded?.()
    } catch {
      setError('Failed to add. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card p-5">
      <h2 className="font-display font-semibold text-slate-200 text-sm uppercase tracking-wide mb-4">
        Quick Add Transaction
      </h2>

      {/* Type toggle */}
      <div className="grid grid-cols-2 gap-2 p-1 bg-[#0d1420] rounded-lg border border-[#1e2d3d] mb-4">
        {[
          { id: 'income',  label: 'Money In',  Icon: TrendingUp  },
          { id: 'expense', label: 'Money Out', Icon: TrendingDown },
        ].map(({ id, label, Icon }) => (
          <button key={id} type="button"
            onClick={() => { setType(id); setCategory('') }}
            className={clsx(
              'py-2 rounded-md text-sm font-medium transition-all flex items-center justify-center gap-2',
              type === id
                ? id === 'income' ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25' : 'bg-red-500/15 text-red-400 border border-red-500/25'
                : 'text-slate-500 hover:text-slate-300'
            )}>
            <Icon size={13} /> {label}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-3 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      <form onSubmit={submit} className="space-y-3">
        <div className="grid grid-cols-2 gap-2">
          <input
            className="input-dark"
            type="number"
            placeholder="Amount (KES)"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            min="1"
            step="1"
          />
          <select className="input-dark" value={category} onChange={e => setCategory(e.target.value)}>
            <option value="">Category...</option>
            {filteredCats.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
          </select>
        </div>
        <input
          className="input-dark"
          placeholder="Description (optional)"
          value={description}
          onChange={e => setDescription(e.target.value)}
        />
        <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
          {loading
            ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            : <><Plus size={15} /> Add Transaction</>
          }
        </button>
      </form>
    </div>
  )
}
