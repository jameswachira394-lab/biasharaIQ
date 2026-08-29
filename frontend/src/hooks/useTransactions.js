'use client'
import { useState, useEffect, useCallback } from 'react'
import { transactionsApi } from '@/utils/api'

export function useTransactions(initialFilters = {}) {
  const [transactions, setTransactions] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(0)
  const [filters, setFilters] = useState(initialFilters)
  const PAGE_SIZE = 20

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = { limit: PAGE_SIZE, offset: page * PAGE_SIZE }
      if (filters.type) params.type = filters.type
      if (filters.category) params.category = filters.category
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date
      const res = await transactionsApi.list(params)
      setTransactions(res.data.items || [])
      setTotal(res.data.total || 0)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load transactions')
    } finally {
      setLoading(false)
    }
  }, [page, filters])

  useEffect(() => { fetch() }, [fetch])

  const updateFilters = useCallback((newFilters) => {
    setFilters(f => ({ ...f, ...newFilters }))
    setPage(0)
  }, [])

  const clearFilters = useCallback(() => {
    setFilters({})
    setPage(0)
  }, [])

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return {
    transactions, total, loading, error,
    page, setPage, totalPages, PAGE_SIZE,
    filters, updateFilters, clearFilters,
    refetch: fetch
  }
}
