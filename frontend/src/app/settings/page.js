'use client'
import { useState, useEffect } from 'react'
import { profileApi, categoriesApi } from '@/utils/api'
import AppLayout from '@/components/ui/AppLayout'
import { useAuth } from '@/context/AuthContext'
import { User, Tag, Plus, Trash2, CheckCircle, AlertCircle } from 'lucide-react'
import clsx from 'clsx'

export default function SettingsPage() {
  const { user, updateUser } = useAuth()
  const [profile, setProfile] = useState({ business_name: '', owner_name: '', phone: '', business_type: '' })
  const [categories, setCategories] = useState([])
  const [newCat, setNewCat] = useState({ name: '', type: 'expense' })
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)
  const [tab, setTab] = useState('profile')

  useEffect(() => {
    profileApi.get().then(r => setProfile(r.data)).catch(() => {})
    categoriesApi.list().then(r => setCategories(r.data || [])).catch(() => {})
  }, [])

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  const saveProfile = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await profileApi.update(profile)
      updateUser({ business_name: profile.business_name, owner_name: profile.owner_name })
      showToast('Profile saved successfully')
    } catch { showToast('Failed to save profile', 'error') }
    finally { setSaving(false) }
  }

  const addCategory = async (e) => {
    e.preventDefault()
    if (!newCat.name.trim()) return
    try {
      await categoriesApi.create({ name: newCat.name.trim(), type: newCat.type })
      const r = await categoriesApi.list()
      setCategories(r.data || [])
      setNewCat({ name: '', type: 'expense' })
      showToast('Category added')
    } catch { showToast('Failed to add category', 'error') }
  }

  const deleteCategory = async (id) => {
    try {
      await categoriesApi.delete(id)
      setCategories(c => c.filter(x => x.id !== id))
      showToast('Category deleted')
    } catch { showToast('Cannot delete this category', 'error') }
  }

  const TABS = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'categories', label: 'Categories', icon: Tag },
  ]

  return (
    <AppLayout>
      <div className="space-y-6 stagger-children max-w-2xl">
        <div>
          <h1 className="font-display font-bold text-2xl text-slate-100">Settings</h1>
          <p className="text-slate-500 text-sm mt-0.5">Manage your business profile and categories</p>
        </div>

        {toast && (
          <div className={clsx('flex items-center gap-2 p-3 rounded-lg border text-sm animate-fade-in',
            toast.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400')}>
            {toast.type === 'success' ? <CheckCircle size={15} /> : <AlertCircle size={15} />}
            {toast.msg}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1 p-1 bg-[#0d1420] rounded-lg border border-[#1e2d3d] w-fit">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setTab(id)}
              className={clsx('flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all',
                tab === id ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'text-slate-500 hover:text-slate-300')}>
              <Icon size={14} /> {label}
            </button>
          ))}
        </div>

        {tab === 'profile' && (
          <div className="card p-6">
            <h2 className="font-display font-semibold text-slate-200 mb-5">Business Profile</h2>
            <form onSubmit={saveProfile} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Business Name</label>
                  <input className="input-dark" value={profile.business_name || ''} onChange={e => setProfile(p => ({ ...p, business_name: e.target.value }))} />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Owner Name</label>
                  <input className="input-dark" value={profile.owner_name || ''} onChange={e => setProfile(p => ({ ...p, owner_name: e.target.value }))} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Phone</label>
                  <input className="input-dark" value={profile.phone || ''} onChange={e => setProfile(p => ({ ...p, phone: e.target.value }))} placeholder="+254..." />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1.5">Business Type</label>
                  <input className="input-dark" value={profile.business_type || ''} onChange={e => setProfile(p => ({ ...p, business_type: e.target.value }))} placeholder="e.g. Retail" />
                </div>
              </div>
              <div className="pt-1">
                <label className="block text-xs text-slate-500 mb-1">Email (read-only)</label>
                <input className="input-dark opacity-50" value={user?.email || ''} disabled />
              </div>
              <button type="submit" className="btn-primary" disabled={saving}>
                {saving ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Saving...</> : 'Save Profile'}
              </button>
            </form>
          </div>
        )}

        {tab === 'categories' && (
          <div className="card p-6">
            <h2 className="font-display font-semibold text-slate-200 mb-5">Categories</h2>

            {/* Add category */}
            <form onSubmit={addCategory} className="flex gap-2 mb-5">
              <input className="input-dark flex-1" placeholder="New category name..." value={newCat.name} onChange={e => setNewCat(n => ({ ...n, name: e.target.value }))} />
              <select className="input-dark w-auto" value={newCat.type} onChange={e => setNewCat(n => ({ ...n, type: e.target.value }))}>
                <option value="income">Money In</option>
                <option value="expense">Money Out</option>
              </select>
              <button type="submit" className="btn-primary px-3"><Plus size={16} /></button>
            </form>

            {/* Income categories */}
            {['income', 'expense'].map(type => (
              <div key={type} className="mb-4">
                <h3 className={clsx('text-xs font-semibold uppercase tracking-wide mb-2', type === 'income' ? 'text-emerald-400' : 'text-red-400')}>
                  {type === 'income' ? '↑ Money In' : '↓ Money Out'} Categories
                </h3>
                <div className="flex flex-wrap gap-2">
                  {categories.filter(c => c.type === type).map(cat => (
                    <div key={cat.id} className={clsx('flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs border',
                      type === 'income' ? 'bg-emerald-500/5 border-emerald-500/15 text-emerald-300' : 'bg-red-500/5 border-red-500/15 text-red-300')}>
                      {cat.name}
                      {!cat.is_default && (
                        <button onClick={() => deleteCategory(cat.id)} className="hover:text-red-400 ml-1 opacity-60 hover:opacity-100">
                          <Trash2 size={10} />
                        </button>
                      )}
                    </div>
                  ))}
                  {categories.filter(c => c.type === type).length === 0 && (
                    <span className="text-xs text-slate-600">None yet</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
