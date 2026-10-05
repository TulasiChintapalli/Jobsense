import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Trash2 } from 'lucide-react'
import { Api } from '../services/api'
import { useApp } from '../context/AppContext'
import { Spinner } from '../components/Shell'
import { fmt } from './Dashboard'
export default function History() {
  const [items, setItems] = useState(null); const [q, setQ] = useState(''); const [sort, setSort] = useState('date:desc'); const [del, setDel] = useState(null); const { toast } = useApp()
  useEffect(() => { const [s, o] = sort.split(':'); const t = setTimeout(() => Api.list({ search: q, sort: s, order: o }).then(d => setItems(d.analyses)).catch(e => toast(e.userMessage, 'error')), 250); return () => clearTimeout(t) }, [q, sort])
  async function confirmDel() { try { await Api.remove(del.id); setItems(i => i.filter(x => x.id !== del.id)); toast('Analysis deleted.') } catch (e) { toast(e.userMessage, 'error') } setDel(null) }
  return <><h1>History</h1>
    <div className="toolbar"><div className="search"><Search size={16} /><input aria-label="Search analyses" placeholder="Search by title, company or role" value={q} onChange={e => setQ(e.target.value)} /></div>
      <select aria-label="Sort" value={sort} onChange={e => setSort(e.target.value)}><option value="date:desc">Newest first</option><option value="date:asc">Oldest first</option><option value="score:desc">Highest score</option><option value="title:asc">Title A–Z</option></select></div>
    {!items ? <Spinner /> : !items.length ? <div className="card"><p className="muted">{q ? 'No analyses match your search.' : 'You have no saved analyses yet.'} <Link to="/analyze">Analyze a job description</Link></p></div> :
      <div className="card table-wrap"><table><thead><tr><th>Job title</th><th>Company</th><th>ML prediction</th><th>Score</th><th>Date</th><th></th></tr></thead><tbody>
        {items.map(a => <tr key={a.id}><td>{a.title}</td><td>{a.company_name || '—'}</td><td>{a.ml_prediction || '—'}</td><td>{a.overall_score != null ? a.overall_score + '%' : '—'}</td><td>{fmt(a.created_at)}</td>
          <td className="actions"><Link className="btn ghost sm" to={`/results/${a.id}`}>View</Link><button className="btn danger sm" aria-label={`Delete ${a.title}`} onClick={() => setDel(a)}><Trash2 size={14} /></button></td></tr>)}</tbody></table></div>}
    {del && <div className="modal" role="dialog" aria-modal="true"><div className="card"><h2>Delete this analysis?</h2><p className="muted">“{del.title}” will be permanently removed.</p><div className="row"><button className="btn ghost" onClick={() => setDel(null)}>Cancel</button><button className="btn danger" onClick={confirmDel}>Delete</button></div></div></div>}</>
}
