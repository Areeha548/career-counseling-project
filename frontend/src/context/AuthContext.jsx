import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { getMyProfile, loginAccount } from '../api/client'

const TOKEN_KEY = 'career_mentor_access_token'
const AuthContext = createContext(null)

export function getAccessToken() {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isCheckingSession, setIsCheckingSession] = useState(true)

  useEffect(() => {
    let isActive = true
    const token = sessionStorage.getItem(TOKEN_KEY)

    if (!token) {
      setIsCheckingSession(false)
      return () => { isActive = false }
    }

    getMyProfile(token)
      .then((profile) => { if (isActive) setUser(profile) })
      .catch(() => {
        sessionStorage.removeItem(TOKEN_KEY)
        if (isActive) setUser(null)
      })
      .finally(() => { if (isActive) setIsCheckingSession(false) })

    return () => { isActive = false }
  }, [])

  async function login(credentials) {
    const result = await loginAccount(credentials)
    sessionStorage.setItem(TOKEN_KEY, result.access_token)

    try {
      const profile = await getMyProfile(result.access_token)
      setUser(profile)
      return profile
    } catch (error) {
      sessionStorage.removeItem(TOKEN_KEY)
      setUser(null)
      throw error
    }
  }

  function logout() {
    sessionStorage.removeItem(TOKEN_KEY)
    setUser(null)
  }

  const value = useMemo(() => ({ user, isCheckingSession, login, logout }), [user, isCheckingSession])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider.')
  return context
}
