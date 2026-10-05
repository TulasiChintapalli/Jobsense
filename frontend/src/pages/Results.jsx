import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Copy, Check } from 'lucide-react'
import { Api } from '../services/api'
import { useApp } from '../context/AppContext'
import { Spinner } from '../components/Shell'
import { fmt } from './Dashboard'

const Chips = ({ items, cls }) =>
  items?.length ? (
    <div className="chips">
      {items.map(s => (
        <span key={s} className={`chip ${cls || ''}`}>
          {s}
        </span>
      ))}
    </div>
  ) : (
    <p className="muted">Not specified.</p>
  )

const List = ({ items }) =>
  items?.length ? (
    <ul className="plain checks">
      {items.map(s => (
        <li key={s}>
          <Check size={16} />
          {s}
        </li>
      ))}
    </ul>
  ) : (
    <p className="muted">Not specified.</p>
  )

export default function Results() {
  const { id } = useParams()
  const [a, setA] = useState(null)
  const [err, setErr] = useState('')
  const { toast } = useApp()

  useEffect(() => {
    Api.get(id)
      .then(setA)
      .catch(e => setErr(e.userMessage))
  }, [id])

  if (err)
    return (
      <div className="card">
        <h2>{err}</h2>
        <Link to="/history">Back to history</Link>
      </div>
    )

  if (!a) return <Spinner label="Loading results…" />

  const r = a.result

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(r.keywords.join(', '))
      toast('Keywords copied.')
    } catch {
      toast('Could not copy keywords.', 'error')
    }
  }

  return (
    <>
      <Link to="/history" className="muted">
        ← Back to history
      </Link>

      <h1>{a.title}</h1>

      <p className="muted">
        {a.company_name && a.company_name !== 'Not specified'
          ? a.company_name + ' · '
          : ''}
        Analyzed {fmt(a.created_at)}
        {a.file_name && ` · ${a.file_name}`}
      </p>

      <div className="grid2">

        {/* ML JOB ROLE PREDICTION */}
        <section className="card ml">
          <h2>ML job role prediction</h2>

          {a.ml_prediction ? (
            <>
              <p className="big">{a.ml_prediction}</p>

              <p>
                Model confidence:{' '}
                <strong>
                  {Math.round(a.ml_confidence * 100)}%
                </strong>
              </p>

              <p className="muted">
                Powered by TF-IDF + Logistic Regression.
                A prediction, not a guarantee.
              </p>
            </>
          ) : (
            <p className="muted">
              ML prediction is unavailable because the model has not been
              trained yet.
            </p>
          )}
        </section>

        {/* AI ANALYSIS SCORE */}
        <section className="card ai">
          <h2>AI analysis score</h2>

          {r ? (
            <>
              <p className="big">
                {a.overall_score?? 0}%
              </p>

              <p className="muted">
                AI-generated analysis score. It is not an official hiring
                score.
              </p>
            </>
          ) : (
            <p className="muted">
              AI analysis is unavailable because the Gemini API key has not
              been configured.
            </p>
          )}
        </section>

      </div>

      {r ? (
        <>
          {/* SUMMARY */}
          <section className="card">
            <h2>Summary</h2>
            <p>{r.summary}</p>
          </section>

          {/* SKILLS / EXPERIENCE / EDUCATION */}
          <div className="grid2">

            <section className="card">
              <h2>Technical skills</h2>
              <Chips items={r.technical_skills} />
            </section>

            <section className="card">
              <h2>Soft skills</h2>
              <Chips items={r.soft_skills} cls="soft" />
            </section>

            <section className="card">
              <h2>Experience</h2>
              <List items={r.experience} />
            </section>

            <section className="card">
              <h2>Education</h2>
              <List items={r.education} />
            </section>

          </div>

          {/* RESPONSIBILITIES */}
          <section className="card">
            <h2>Responsibilities</h2>
            <List items={r.responsibilities} />
          </section>

          {/* KEYWORDS */}
          <section className="card">
            <div className="between">
              <h2>Keywords</h2>

              <button
                className="btn ghost sm"
                onClick={copy}
              >
                <Copy size={14} />
                Copy keywords
              </button>
            </div>

            <Chips items={r.keywords} />
          </section>

          {/* SKILL GAPS */}
          <section className="card">
            <h2>Potential skill gaps</h2>

            <p className="muted">
              AI-generated potential gaps based on the job description.
              Review them against your own background.
            </p>

            <Chips
              items={r.missing_skills}
              cls="gap"
            />
          </section>

          {/* RECOMMENDED SKILLS */}
          <section className="card">
            <h2>What should I learn?</h2>

            {r.recommended_skills?.length ? (
              <div className="grid2">

                {r.recommended_skills.map(s => (
                  <div
                    key={s.skill}
                    className="rec"
                  >
                    <strong>{s.skill}</strong>

                    <p className="muted">
                      {s.reason || 'No reason given.'}
                    </p>

                    <span
                      className={`chip pri ${(s.priority || '').toLowerCase()}`}
                    >
                      Priority: {s.priority}
                    </span>
                  </div>
                ))}

              </div>
            ) : (
              <p className="muted">
                No recommendations.
              </p>
            )}
          </section>
        </>
      ) : null}
    </>
  )
}