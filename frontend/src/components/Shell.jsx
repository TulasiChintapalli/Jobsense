import { useState } from 'react'
import { NavLink, Link, useNavigate, Navigate, Outlet } from 'react-router-dom'
import { Brain, Menu, X, LogOut } from 'lucide-react'
import { useApp } from '../context/AppContext'

export const Logo = ({ to = '/' }) => <Link to={to} className="logo"><Brain size={24} />JobSense AI</Link>
export const Spinner = ({ label }) => <div className="center-pad"><div className="spinner" aria-hidden />{label && <p className="muted">{label}</p>}</div>

export function Protected() {
  const { user, loading } = useApp()
  if (loading) return <Spinner label="Loading…" />
  return user ? <AppLayout /> : <Navigate to="/login" replace />
}
export function GuestOnly({ children }) {
  const { user, loading } = useApp()
  if (loading) return <Spinner />
  return user ? <Navigate to="/dashboard" replace /> : children
}
function AppLayout() {
  const { user, signOut } = useApp(); const [open, setOpen] = useState(false); const nav = useNavigate()
  const links = [['/dashboard', 'Dashboard'], ['/analyze', 'Analyze JD'], ['/history', 'History'], ['/profile', 'Profile']]
  return <>
    <header className="topbar"><Logo to="/dashboard" />
      <button className="icon-btn menu" aria-label="Toggle menu" onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button>
      <nav className={open ? 'open' : ''} onClick={() => setOpen(false)}>
        {links.map(([to, l]) => <NavLink key={to} to={to}>{l}</NavLink>)}
        <span className="avatar" title={user.full_name}>{user.full_name[0].toUpperCase()}</span>
        <button className="btn ghost sm" onClick={() => { signOut(); nav('/') }}><LogOut size={16} />Logout</button>
      </nav></header>
    <main className="page"><Outlet /></main></>
}
