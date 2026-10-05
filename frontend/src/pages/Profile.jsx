import { useState } from 'react'
import { Api } from '../services/api'
import { useApp } from '../context/AppContext'
import { fmt } from './Dashboard'
export default function Profile() {
  const { user, setUser, toast } = useApp(); const [name, setName] = useState(user.full_name); const [busy, setBusy] = useState(false)
  async function save(e) { e.preventDefault(); setBusy(true); try { const d = await Api.updateProfile({ full_name: name }); setUser(d.user); toast('Profile updated.') } catch (x) { toast(x.userMessage, 'error') } finally { setBusy(false) } }
  return <><h1>Profile</h1><form className="card narrow-form" onSubmit={save}>
    <div className="field"><label htmlFor="n">Full name</label><input id="n" value={name} onChange={e => setName(e.target.value)} /></div>
    <div className="field"><label htmlFor="e">Email</label><input id="e" value={user.email} disabled /></div>
    <p className="muted">Member since {fmt(user.created_at)}</p><button className="btn primary" disabled={busy || !name.trim()}>{busy ? 'Saving…' : 'Save changes'}</button></form></>
}
