import { Link } from 'react-router-dom'
import { Brain, Sparkles, ListChecks, Tags, Target, GraduationCap } from 'lucide-react'
import { Logo } from '../components/Shell'
import { useApp } from '../context/AppContext'
const F = [[Brain, 'ML Job Role Prediction', 'A TF-IDF + Logistic Regression model trained on real job descriptions predicts the likely role.'],
  [Sparkles, 'AI Job Description Analysis', 'Gemini reads the posting and returns a structured breakdown.'], [ListChecks, 'Skill Extraction', 'Technical and soft skills, education and experience, pulled from the text.'],
  [Tags, 'Keyword Detection', 'Copy the terms recruiters and screening tools look for.'], [Target, 'Skill Gap Analysis', 'See which requirements may be missing from your profile.'], [GraduationCap, 'Learning Recommendations', 'Know what to learn first, with a reason and priority.']]
const S = ['Paste or upload a JD', 'ML + AI analysis', 'Understand requirements', 'Identify skill gaps', 'Prepare better']
export default function Landing() {
  const { user } = useApp(); const go = user ? '/analyze' : '/signup'
  return <div className="landing">
    <header className="topbar dark"><Logo />
      <nav className="open-desktop"><a href="#features">Features</a><a href="#how">How it works</a><a href="#about">About</a>
        {user ? <Link className="btn primary sm" to="/dashboard">Dashboard</Link> : <><Link to="/login">Login</Link><Link className="btn primary sm" to="/signup">Get started</Link></>}</nav></header>
    <section className="hero"><p className="tagline">Understand. Analyze. Prepare.</p><h1>Understand any job description in seconds</h1>
      <p className="lead">Analyze job requirements, discover important skills, identify potential skill gaps, and understand what you should learn before applying.</p>
      <div className="row"><Link className="btn primary" to={go}>Analyze a job description</Link><Link className="btn light" to={user ? '/dashboard' : '/signup'}>Get started</Link></div></section>
    <section id="features" className="section"><h2>Everything you need before you apply</h2>
      <div className="grid3">{F.map(([I, t, d]) => <article className="card" key={t}><I className="accent" /><h3>{t}</h3><p className="muted">{d}</p></article>)}</div></section>
    <section id="how" className="section alt"><h2>How it works</h2><ol className="steps">{S.map(s => <li key={s}>{s}</li>)}</ol></section>
    <section id="about" className="section"><h2>About</h2><p className="muted narrow">JobSense AI keeps two technologies separate on purpose: a trained machine-learning model predicts the job role, and Gemini reads and explains the description. Scores and predictions are guidance, not guarantees.</p></section>
    <footer className="footer">© {new Date().getFullYear()} JobSense AI · Understand. Analyze. Prepare.</footer></div>
}
