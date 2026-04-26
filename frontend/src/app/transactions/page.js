'use client'
import { useState, useEffect, useCallback } from 'react'
import { transactionsApi, categoriesApi } from '@/utils/api'
import { formatCurrency, formatDate, formatDateInput } from '@/utils/format'
import AppLayout from '@/components/ui/AppLayout'
import { Plus, Pencil, Trash2, Filter, Search, X, TrendingUp, TrendingDown, ChevronLeft, ChevronRight } from 'lucide-react'
import clsx from 'clsx'

const PAGE_SIZE = 20

function TransactionModal({ open, onClose, onSaved, categories, editData }) {
  const isEdit = !!editData
  const [form, setForm] = useState({ amount: '', type: 'income', category: '', date: formatDateInput(new Date()), description: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (editData) {
      setForm({
        amount: editData.amount,
        type: editData.type,
        category: editData.category,
        date: formatDateInput(editData.date),
        description: editData.description || ''
      })
    } else {
      setForm({ amount: '', type: 'income', category: '', date: formatDateInput(new Date()), description: '' })
    }
    setError('')
  }, [editData, open])

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const filteredCats = categories.filter(c => c.type === form.type)

  const submit = async (e) => {
    e.preventDefault()
    if (!form.amount || Number(form.amount) <= 0) { setError('Enter a valid amount'); return }
    if (!form.category) { setError('Select a category'); return }
    setLoading(true)
    try {
      const payload = { ...form, amount: Number(form.amount), date: new Date(form.date).toISOString() }
      if (isEdit) await transactionsApi.update(editData.id, payload)
      else await transactionsApi.create(payload)
      onSaved()
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save transaction')
    } finally {
      setLoading(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-md card p-6 animate-fade-in">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display font-semibold text-slate-200">{isEdit ? 'Edit Transaction' : 'Add Transaction'}</h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300 p-1"><X size={18} /></button>
        </div>

        {error && <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

        <form onSubmit={submit} className="space-y-4">
          {/* Type toggle */}
          <div className="grid grid-cols-2 gap-2 p-1 bg-[#0d1420] rounded-lg border border-[#1e2d3d]">
            {['income', 'expense'].map((t) => (
              <button key={t} type="button"
                onClick={() => setForm(f => ({ ...f, type: t, category: '' }))}
                className={clsx('py-2 rounded-md text-sm font-medium transition-all flex items-center justify-center gap-2',
                  form.type === t
                    ? t === 'income' ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25' : 'bg-red-500/15 text-red-400 border border-red-500/25'
                    : 'text-slate-500 hover:text-slate-300'
                )}>
                {t === 'income' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {t === 'income' ? 'Money In' : 'Money Out'}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Amount (KES) *</label>
              <input type="number" className="input-dark" placeholder="0" value={form.amount} onChange={set('amount')} min="1" step="0.01" required />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Date *</label>
              <input type="date" className="input-dark" value={form.date} onChange={set('date')} required />
            </div>
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Category *</label>
            <select className="input-dark" value={form.category} onChange={set('category')} required>
              <option value="">Select category...</option>
              {filteredCats.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Description (Optional)</label>
            <input className="input-dark" placeholder="What was this for?" value={form.description} onChange={set('description')} />
          </div>

          <div className="flex gap-3 pt-1">
            <button type="button" onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
            <button type="submit" className="btn-primary flex-1 justify-center" disabled={loading}>
              {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : isEdit ? 'Save Changes' : 'Add Transaction'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editData, setEditData] = useState(null)
  const [page, setPage] = useState(0)
  const [filters, setFilters] = useState({ type: '', category: '', search: '' })
  const [deleteId, setDeleteId] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = { limit: PAGE_SIZE, offset: page * PAGE_SIZE }
      if (filters.type) params.type = filters.type
      if (filters.category) params.category = filters.category
      const [txRes, catRes] = await Promise.all([transactionsApi.list(params), categoriesApi.list()])
      setTransactions(txRes.data.items || [])
      setTotal(txRes.data.total || 0)
      setCategories(catRes.data || [])
    } catch {}
    finally { setLoading(false) }
  }, [page, filters])

  useEffect(() => { load() }, [load])

  const handleDelete = async (id) => {
    try { await transactionsApi.delete(id); load() } catch {}
    setDeleteId(null)
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)
  const filtered = filters.search
    ? transactions.filter(t => t.description?.toLowerCase().includes(filters.search.toLowerCase()) || t.category.toLowerCase().includes(filters.search.toLowerCase()))
    : transactions

  return (
    <AppLayout>
      <div className="space-y-5 stagger-children">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display font-bold text-2xl text-slate-100">Transactions</h1>
            <p className="text-slate-500 text-sm mt-0.5">{total} total records</p>
          </div>
          <button onClick={() => { setEditData(null); setModalOpen(true) }} className="btn-primary">
            <Plus size={16} /> Add Transaction
          </button>
        </div>

        {/* Filters */}
        <div className="card p-4 flex flex-wrap gap-3">
          <div className="relative flex-1 min-w-[180px]">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input className="input-dark pl-8" placeholder="Search..." value={filters.search} onChange={e => setFilters(f => ({ ...f, search: e.target.value }))} />
          </div>
          <select className="input-dark w-auto min-w-[130px]" value={filters.type} onChange={e => { setFilters(f => ({ ...f, type: e.target.value, category: '' })); setPage(0) }}>
            <option value="">All Types</option>
            <option value="income">Money In</option>
            <option value="expense">Money Out</option>
          </select>
          <select className="input-dark w-auto min-w-[150px]" value={filters.category} onChange={e => { setFilters(f => ({ ...f, category: e.target.value })); setPage(0) }}>
            <option value="">All Categories</option>
            {categories.filter(c => !filters.type || c.type === filters.type).map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
          </select>
          {(filters.type || filters.category || filters.search) && (
            <button onClick={() => { setFilters({ type: '', category: '', search: '' }); setPage(0) }} className="btn-secondary px-3">
              <X size={14} /> Clear
            </button>
          )}
        </div>

        {/* Table */}
        <div className="card overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-40 text-slate-500 text-sm">
              <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin mr-2" /> Loading...
            </div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 text-slate-500 text-sm gap-3">
              <p>No transactions found</p>
              <button onClick={() => { setEditData(null); setModalOpen(true) }} className="btn-primary text-xs py-1.5 px-3">
                <Plus size={13} /> Add First Transaction
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[#1e2d3d]">
                    {['Date', 'Type', 'Category', 'Description', 'Amount', ''].map(h => (
                      <th key={h} className="px-4 py-3 text-left text-xs text-slate-500 font-medium uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((txn) => (
                    <tr key={txn.id} className="border-b border-[#1e2d3d] hover:bg-white/2 transition-colors">
                      <td className="px-4 py-3 text-slate-400 text-xs whitespace-nowrap">{formatDate(txn.date)}</td>
                      <td className="px-4 py-3">
                        <span className={clsx('text-xs px-2 py-0.5 rounded-full font-medium',
                          txn.type === 'income' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400')}>
                          {txn.type === 'income' ? '↑ In' : '↓ Out'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-300 text-xs">{txn.category}</td>
                      <td className="px-4 py-3 text-slate-500 text-xs max-w-[200px] truncate">{txn.description || '—'}</td>
                      <td className={clsx('px-4 py-3 font-mono font-semibold text-sm whitespace-nowrap',
                        txn.type === 'income' ? 'text-emerald-400' : 'text-red-400')}>
                        {txn.type === 'income' ? '+' : '-'}{formatCurrency(txn.amount)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <button onClick={() => { setEditData(txn); setModalOpen(true) }}
                            className="p-1 text-slate-500 hover:text-slate-300 transition-colors"><Pencil size={13} /></button>
                          {deleteId === txn.id ? (
                            <div className="flex items-center gap-1">
                              <button onClick={() => handleDelete(txn.id)} className="text-xs text-red-400 hover:text-red-300 px-1.5 py-0.5 border border-red-500/30 rounded">Yes</button>
                              <button onClick={() => setDeleteId(null)} className="text-xs text-slate-500 hover:text-slate-300">No</button>
                            </div>
                          ) : (
                            <button onClick={() => setDeleteId(txn.id)} className="p-1 text-slate-500 hover:text-red-400 transition-colors"><Trash2 size={13} /></button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-3">
            <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="btn-secondary p-2 disabled:opacity-40">
              <ChevronLeft size={16} />
            </button>
            <span className="text-sm text-slate-400">Page {page + 1} of {totalPages}</span>
            <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} className="btn-secondary p-2 disabled:opacity-40">
              <ChevronRight size={16} />
            </button>
          </div>
        )}
      </div>

      <TransactionModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSaved={load}
        categories={categories}
        editData={editData}
      />
    </AppLayout>
  )
}
