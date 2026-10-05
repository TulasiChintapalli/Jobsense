import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, ArrowLeft } from 'lucide-react'
import { Api } from '../services/api'
import { useApp } from '../context/AppContext'
import { Logo } from '../components/Shell'

const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

function Field({
  k,
  label,
  type = 'text',
  auto,
  f,
  setF,
  err,
  show,
  setShow
}) {
  return (
    <div className="field">
      <label htmlFor={k}>{label}</label>

      <div className="pw">
        <input
          id={k}
          type={
            k.includes('assword') || k === 'confirm'
              ? (show ? 'text' : 'password')
              : type
          }
          value={f[k]}
          onChange={(e) =>
            setF((prev) => ({
              ...prev,
              [k]: e.target.value
            }))
          }
          autoComplete={auto}
          aria-invalid={!!err[k]}
        />

        {k === 'password' && (
          <button
            type="button"
            className="icon-btn"
            aria-label={show ? 'Hide password' : 'Show password'}
            onClick={() => setShow((prev) => !prev)}
          >
            {show ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>

      {err[k] && <p className="error">{err[k]}</p>}
    </div>
  )
}

export default function Auth({ mode }) {
  const signup = mode === 'signup'
  const nav = useNavigate()
  const { signIn, toast } = useApp()

  const [f, setF] = useState({
    full_name: '',
    email: '',
    password: '',
    confirm: ''
  })

  const [show, setShow] = useState(false)
  const [err, setErr] = useState({})
  const [busy, setBusy] = useState(false)
  const [remember, setRemember] = useState(true)

  async function submit(e) {
    e.preventDefault()

    const v = {}

    if (signup && !f.full_name.trim()) {
      v.full_name = 'Enter your full name.'
    }

    if (!EMAIL.test(f.email)) {
      v.email = 'Enter a valid email address.'
    }

    if (!f.password) {
      v.password = 'Enter your password.'
    } else if (signup && f.password.length < 8) {
      v.password = 'Use at least 8 characters.'
    }

    if (signup && f.confirm !== f.password) {
      v.confirm = 'Passwords do not match.'
    }

    setErr(v)

    if (Object.keys(v).length) return

    setBusy(true)

    try {
      const d = signup
        ? await Api.register(f)
        : await Api.login(f)

      signIn(d)

      toast(
        signup
          ? 'Account created. Welcome!'
          : 'Logged in.'
      )

      nav('/dashboard')
    } catch (x) {
      setErr({
        form: x.userMessage
      })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth">
      <aside>
        <Logo />

        <h2>
          Your AI-powered job analysis partner
        </h2>

        <p>
          Understand job roles, identify key skills,
          and bridge your skill gaps.
        </p>
      </aside>

      <form onSubmit={submit} noValidate>
        <Link to="/" className="back">
          <ArrowLeft size={16} />
          Back to home
        </Link>

        <h1>
          {signup ? 'Create your account' : 'Welcome back'}
        </h1>

        {err.form && (
          <div className="alert" role="alert">
            {err.form}
          </div>
        )}

        {signup && (
          <Field
            k="full_name"
            label="Full name"
            auto="name"
            f={f}
            setF={setF}
            err={err}
            show={show}
            setShow={setShow}
          />
        )}

        <Field
          k="email"
          label="Email address"
          type="email"
          auto="email"
          f={f}
          setF={setF}
          err={err}
          show={show}
          setShow={setShow}
        />

        <Field
          k="password"
          label="Password"
          auto={signup ? 'new-password' : 'current-password'}
          f={f}
          setF={setF}
          err={err}
          show={show}
          setShow={setShow}
        />

        {signup && (
          <Field
            k="confirm"
            label="Confirm password"
            auto="new-password"
            f={f}
            setF={setF}
            err={err}
            show={show}
            setShow={setShow}
          />
        )}

        {!signup && (
          <label className="check">
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) =>
                setRemember(e.target.checked)
              }
            />
            Remember me
          </label>
        )}

        <button
          className="btn primary block"
          disabled={busy}
        >
          {busy
            ? 'Please wait…'
            : signup
              ? 'Create account'
              : 'Log in'}
        </button>

        <p className="muted center">
          {signup ? (
            <>
              Already registered?{' '}
              <Link to="/login">Log in</Link>
            </>
          ) : (
            <>
              New here?{' '}
              <Link to="/signup">
                Create an account
              </Link>
            </>
          )}
        </p>
      </form>
    </div>
  )
}
