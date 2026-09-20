import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { api, clearToken, getToken, setToken, setUnauthorizedHandler } from './api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getToken()))
  const [connError, setConnError] = useState('')

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
    setConnError('')
  }, [])

  const checkSession = useCallback(() => {
    if (!getToken()) { setLoading(false); return }
    setLoading(true)
    setConnError('')
    api('/auth/me')
      .then((u) => setUser(u))
      .catch((e) => {
        // Sin conexión con el backend no sabemos si la sesión sigue siendo válida:
        // no cerramos sesión por eso, solo mostramos la pantalla de reintento.
        if (e.isConnectionError) setConnError(e.message)
        else logout()
      })
      .finally(() => setLoading(false))
  }, [logout])

  useEffect(() => {
    setUnauthorizedHandler(logout)
    checkSession()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [logout])

  const login = useCallback(async (username, password) => {
    const data = await api('/auth/login', { method: 'POST', body: { username, password } })
    setToken(data.token)
    setUser(data.user)
    setConnError('')
  }, [])

  const value = useMemo(
    () => ({ user, loading, connError, login, logout, retry: checkSession }),
    [user, loading, connError, login, logout, checkSession],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
