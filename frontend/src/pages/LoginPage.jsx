import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'
import { useAuth } from '../context/AuthContext'
import { AuthShell, FormAlert, PasswordField, SubmitButton, TextField } from '../components/AuthComponents'

function validate(form) {
  const errors = {}
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) errors.email = 'Enter a valid email address.'
  if (!form.password) errors.password = 'Enter your password to continue.'
  return errors
}

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const [form, setForm] = useState({ email: location.state?.email || '', password: '' })
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState('')
  const [loading, setLoading] = useState(false)
  const registered = Boolean(location.state?.registered)

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: '' }))
    setApiError('')
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextErrors = validate(form)
    setErrors(nextErrors)
    setApiError('')
    if (Object.keys(nextErrors).length) return

    setLoading(true)
    try {
      await login({ email: form.email.trim(), password: form.password })
      navigate('/dashboard', { replace: true })
    } catch (error) {
      setApiError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell mode="auth-login">
      <div className="auth-heading login-heading">
        <span className="form-eyebrow">WELCOME BACK</span>
        <h2>Good to see you again.</h2>
        <p>Sign in to pick up where your career journey left off.</p>
      </div>
      <FormAlert success={registered}>{registered ? 'Your account is ready. Sign in to continue.' : ''}</FormAlert>
      <FormAlert>{apiError}</FormAlert>
      <form className="auth-form login-form" onSubmit={handleSubmit} noValidate>
        <TextField id="email" label="Email address" type="email" value={form.email} onChange={(event) => update('email', event.target.value)} error={errors.email} placeholder="you@example.com" autoComplete="email" required />
        <PasswordField id="password" label="Password" value={form.password} onChange={(event) => update('password', event.target.value)} error={errors.password} autoComplete="current-password" />
        <SubmitButton loading={loading}>Sign in</SubmitButton>
      </form>
      <p className="auth-switch">New to AI Career Mentor? <Link to="/register">Create an account</Link></p>
      <div className="login-assurance"><span>✦</span> Your career journey is right where you left it.</div>
    </AuthShell>
  )
}
