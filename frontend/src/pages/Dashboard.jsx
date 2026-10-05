import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { Api } from '../services/api'
import { useApp } from '../context/AppContext'
import { Spinner } from '../components/Shell'
export const fmt = d => new Date(d + 'Z').toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
export default function Dashboard() {
  const { user, toast } = useApp(); const [s, setS] = useState(null); const [ml, setMl] = useState(null)
  useEffect(() => { Api.stats().then(setS).catch(e => toast(e.userMessage, 'error')); Api.mlInfo().then(setMl).catch(() => {}) }, [])
  if (!s) return <Spinner label="Loading your dashboard…" />
  const m = ml?.metrics
  return <><h1>Welcome back, {user.full_name.split(' ')[0]} 👋</h1>
    <div className="grid4">{[['Total analyses', s.total], ['Average analysis score', s.average_score != null ? s.average_score + '%' : '—'], ['Skills identified', s.skills_identified]].map(([l, v]) => <div className="card stat" key={l}><span className="muted">{l}</span><strong>{v}</strong></div>)}
      <Link to="/analyze" className="card stat cta"><span>Quick action</span><strong>Analyze new job description</strong></Link></div>
    <div className="grid2">
      <section className="card"><h2>Score over time</h2>{s.score_series.length >= 2 ? <ResponsiveContainer width="100%" height={220}><LineChart data={s.score_series}><CartesianGrid strokeDasharray="3 3" stroke="#e5e7f0" /><XAxis dataKey="date" fontSize={12} /><YAxis domain={[0, 100]} fontSize={12} /><Tooltip /><Line dataKey="score" stroke="#4f46e5" strokeWidth={2} /></LineChart></ResponsiveContainer> : <p className="muted">Run at least two AI analyses to see a trend.</p>}</section>
      <section className="card"><h2>ML model</h2><p><strong>TF-IDF + Logistic Regression</strong></p><p className="muted">Purpose: job role classification</p>
        {m ? <ul className="plain"><li>Accuracy: {(m.accuracy * 100).toFixed(1)}%</li><li>Macro F1: {(m.macro_f1 * 100).toFixed(1)}%</li><li>Weighted F1: {(m.weighted_f1 * 100).toFixed(1)}%</li><li>Precision / recall (macro): {(m.macro_precision * 100).toFixed(1)}% / {(m.macro_recall * 100).toFixed(1)}%</li><li>{m.train_samples} train · {m.test_samples} test · {m.num_classes} classes</li></ul> : <p className="muted">Not trained yet. Add a dataset and run <code>python -m app.ml.train_model</code>.</p>}</section></div>
    <section className="card"><h2>Recent analyses</h2>{s.recent.length ? <div className="table-wrap"><table><thead><tr><th>Job title</th><th>Company</th><th>Score</th><th>ML prediction</th><th>Date</th><th></th></tr></thead><tbody>
      {s.recent.map(a => <tr key={a.id}><td>{a.title}</td><td>{a.company_name || '—'}</td><td>{a.overall_score != null ? a.overall_score + '%' : '—'}</td><td>{a.ml_prediction || '—'}</td><td>{fmt(a.created_at)}</td><td><Link className="btn ghost sm" to={`/results/${a.id}`}>View</Link></td></tr>)}</tbody></table></div>
      : <p className="muted">No analyses yet. <Link to="/analyze">Analyze your first job description.</Link></p>}</section></>
}
