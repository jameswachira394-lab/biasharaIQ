'use client'
import { createContext, useContext, useState, useEffect } from 'react'
import { authApi, profileApi } from '@/utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem('biasharaiq_token')
      if (token) {
        try {
          const res = await profileApi.get()
          setUser(res.data)
          localStorage.setItem('biasharaiq_user', JSON.stringify(res.data))
        } catch (err) {
          console.error("Failed to fetch user profile", err)
          // If profile fetch fails (e.g. token expired), we might want to logout
          if (err.response?.status === 401) logout()
        }
      }
      setLoading(false)
    }
    fetchUser()
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

    // ✅ Only store token if provided (token comes after email verification)
    if (access_token) {
      localStorage.setItem('biasharaiq_token', access_token)
      localStorage.setItem('biasharaiq_user', JSON.stringify(userData))
      setUser(userData)
    }

    // Return user data regardless (needed for frontend to check is_verified)
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
