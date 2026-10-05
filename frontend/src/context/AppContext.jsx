import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { Api } from '../services/api'
const Ctx = createContext()
export const useApp = () => useContext(Ctx)
export function AppProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(!!localStorage.getItem('token'))
  const [toasts, setToasts] = useState([])
  const toast = useCallback((message, type = 'success') => {
    const id = Math.random(); setToasts(t => [...t, { id, message, type }]); setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 4000)
  }, [])
  useEffect(() => { if (localStorage.getItem('token')) Api.me().then(d => setUser(d.user)).catch(() => localStorage.removeItem('token')).finally(() => setLoading(false)) }, [])
  const signIn = d => { localStorage.setItem('token', d.token); setUser(d.user) }
  const signOut = () => { localStorage.removeItem('token'); setUser(null); toast('You have been logged out.') }
  return <Ctx.Provider value={{ user, setUser, loading, signIn, signOut, toast }}>
    {children}
    <div className="toasts" role="status" aria-live="polite">{toasts.map(t => <div key={t.id} className={`toast ${t.type}`}>{t.message}</div>)}</div>
  </Ctx.Provider>
}
