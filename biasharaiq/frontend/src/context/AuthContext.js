'use client'
import { createContext, useContext, useState, useEffect } from 'react'
import { authApi } from '@/utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('biasharaiq_user')
    const token = localStorage.getItem('biasharaiq_token')
    if (stored && token) {
      try { setUser(JSON.parse(stored)) } catch {}
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const res = await authApi.login({ email, password })
    const { access_token, user: userData } = res.data
    localStorage.setItem('biasharaiq_token', access_token)
    localStorage.setItem('biasharaiq_user', JSON.stringify(userData))
    setUser(userData)
    return userData
  }

  const register = async (data) => {
    const res = await authApi.register(data)
    const { access_token, user: userData } = res.data
    localStorage.setItem('biasharaiq_token', access_token)
    localStorage.setItem('biasharaiq_user', JSON.stringify(userData))
    setUser(userData)
    return userData
  }

  const logout = () => {
    localStorage.removeItem('biasharaiq_token')
    localStorage.removeItem('biasharaiq_user')
    setUser(null)
    window.location.href = '/login'
  }

  const updateUser = (data) => {
    const updated = { ...user, ...data }
    setUser(updated)
    localStorage.setItem('biasharaiq_user', JSON.stringify(updated))
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
