export const formatCurrency = (amount, currency = 'KES') => {
  if (amount === null || amount === undefined) return `${currency} 0`
  return `${currency} ${Number(amount).toLocaleString('en-KE', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  })}`
}

export const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-KE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export const formatDateInput = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toISOString().split('T')[0]
}

export const getRiskColor = (level) => {
  switch (level) {
    case 'safe': return 'text-emerald-400'
    case 'warning': return 'text-amber-400'
    case 'critical': return 'text-red-400'
    default: return 'text-slate-400'
  }
}

export const getRiskBg = (level) => {
  switch (level) {
    case 'safe': return 'bg-emerald-500/10 border-emerald-500/20'
    case 'warning': return 'bg-amber-500/10 border-amber-500/20'
    case 'critical': return 'bg-red-500/10 border-red-500/20'
    default: return 'bg-slate-500/10 border-slate-500/20'
  }
}

export const getSeverityColor = (severity) => {
  switch (severity) {
    case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/20'
    case 'warning': return 'text-amber-400 bg-amber-500/10 border-amber-500/20'
    case 'success': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
    default: return 'text-blue-400 bg-blue-500/10 border-blue-500/20'
  }
}
