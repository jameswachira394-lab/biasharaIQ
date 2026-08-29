'use client'
import { useState, useEffect, useCallback } from 'react'
import { categoriesApi } from '@/utils/api'

export function useCategories(type = null) {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)

  const fetch = useCallback(async () => {
    try {
      const res = await categoriesApi.list(type)
      setCategories(res.data || [])
    } catch {}
    finally { setLoading(false) }
  }, [type])

  useEffect(() => { fetch() }, [fetch])

  const income = categories.filter(c => c.type === 'income')
  const expense = categories.filter(c => c.type === 'expense')

  return { categories, income, expense, loading, refetch: fetch }
}
