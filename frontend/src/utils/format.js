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
    case 'safe': return 'text-[#2E7D32]'
    case 'warning': return 'text-[#F9A825]'
    case 'critical': return 'text-[#D32F2F]'
    default: return 'text-[#1E1E1E]'
  }
}

export const getRiskBg = (level) => {
  switch (level) {
    case 'safe': return 'bg-[#2E7D32]/10 border-[#2E7D32]/20'
    case 'warning': return 'bg-[#F9A825]/10 border-[#F9A825]/20'
    case 'critical': return 'bg-[#D32F2F]/10 border-[#D32F2F]/20'
    default: return 'bg-[#F5F5F5]/10 border-[#F5F5F5]/20'
  }
}

export const getSeverityColor = (severity) => {
  switch (severity) {
    case 'critical': return 'text-[#D32F2F] bg-[#D32F2F]/10 border-[#D32F2F]/20'
    case 'warning': return 'text-[#F9A825] bg-[#F9A825]/10 border-[#F9A825]/20'
    case 'success': return 'text-[#2E7D32] bg-[#2E7D32]/10 border-[#2E7D32]/20'
    default: return 'text-[#1A1F71] bg-[#1A1F71]/10 border-[#1A1F71]/20'
  }
}
