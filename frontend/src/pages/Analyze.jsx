import { useRef, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, X, FileText } from 'lucide-react'
import { Api } from '../services/api'
import { useApp } from '../context/AppContext'
const STEPS = ['Extracting requirements…', 'Running ML model…', 'Generating AI insights…', 'Preparing results…']
export default function Analyze() {
  const [text, setText] = useState(''); const [file, setFile] = useState(null); const [busy, setBusy] = useState(false); const [step, setStep] = useState(0)
  const [err, setErr] = useState(''); const ref = useRef(); const nav = useNavigate(); const { toast } = useApp()
  useEffect(() => { if (!busy) return; const t = setInterval(() => setStep(s => Math.min(s + 1, 3)), 2500); return () => clearInterval(t) }, [busy])
  function pick(f) {
    if (!f) return; const ok = /\.(pdf|docx|txt)$/i.test(f.name)
    if (!ok) return setErr('Only PDF, DOCX and TXT files are supported.')
    if (f.size > 5 * 1024 * 1024) return setErr('File is larger than 5 MB.')
    if (f.size === 0) return setErr('That file is empty.'); setErr(''); setFile(f)
  }
  async function run() {
    if (!file && text.trim().length < 50) return setErr('Paste a job description (at least 50 characters) or upload a file.')
    setErr(''); setStep(0); setBusy(true)
    try { const r = file ? await Api.upload(file) : await Api.analyze(text); toast('Analysis complete.'); r.warnings?.forEach(w => toast(w, 'error')); nav(`/results/${r.id}`) }
    catch (e) { setErr(e.userMessage); toast('Analysis failed.', 'error') } finally { setBusy(false) }
  }
  if (busy) return <div className="center-pad"><div className="spinner" /><h2>Analyzing your job description…</h2><ul className="plain progress">{STEPS.map((s, i) => <li key={s} className={i <= step ? 'on' : ''}>{s}</li>)}</ul></div>
  return <><h1>Analyze job description</h1><p className="muted">Paste text or upload a file. If you do both, the file is used.</p>
    <div className="card"><div className="drop" onDragOver={e => e.preventDefault()} onDrop={e => { e.preventDefault(); pick(e.dataTransfer.files[0]) }}>
      {file ? <div className="filechip"><FileText />{file.name} <span className="muted">({(file.size / 1024).toFixed(1)} KB · ready)</span><button className="icon-btn" aria-label="Remove file" onClick={() => setFile(null)}><X size={16} /></button></div>
        : <><UploadCloud size={32} className="accent" /><p>Drop a file here or <button className="link" onClick={() => ref.current.click()}>browse</button></p><p className="muted">PDF, DOCX, TXT · max 5 MB</p></>}
      <input ref={ref} type="file" hidden accept=".pdf,.docx,.txt" onChange={e => { pick(e.target.files[0]); e.target.value = '' }} /></div>
      <p className="muted center">or</p>
      <label htmlFor="jd" className="sr">Job description</label>
      <textarea id="jd" rows={10} placeholder="Paste the complete job description here..." value={text} onChange={e => setText(e.target.value)} />
      {err && <p className="error" role="alert">{err}</p>}
      <button className="btn primary block" onClick={run}>Analyze job description</button></div></>
}
