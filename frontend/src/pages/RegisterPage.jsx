import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { registerAccount } from '../api/client'
import { AuthShell, FormAlert, PasswordField, SelectField, SubmitButton, TextField } from '../components/AuthComponents'

const experienceOptions = ['Student', 'Entry level', 'Some experience', 'Experienced']
const educationOptions = ['High school', 'Diploma', 'Bachelor’s degree', 'Master’s degree', 'Other']

function validate(form) {
  const errors = {}
  if (form.full_name.trim().length < 2) errors.full_name = 'Please enter your full name.'
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) errors.email = 'Enter a valid email address.'
  if (form.password.length < 8) errors.password = 'Use at least 8 characters for your password.'
  if (form.password.length > 128) errors.password = 'Use no more than 128 characters.'
  if (form.confirm_password !== form.password) errors.confirm_password = 'Your passwords do not match yet.'
  return errors
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name: '', email: '', password: '', confirm_password: '', education: '', experience_level: '' })
  const [errors, setErrors] = useState({})
  const [apiError, setApiError] = useState('')
  const [loading, setLoading] = useState(false)

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
      await registerAccount({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        password: form.password,
        education: form.education || null,
        experience_level: form.experience_level || null,
      })
      navigate('/login', { state: { registered: true, email: form.email.trim() } })
    } catch (error) {
      setApiError(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell mode="auth-register">
      <div className="auth-heading">
        <span className="form-eyebrow">START YOUR JOURNEY</span>
        <h2>Create your account</h2>
        <p>A little about you helps us make your next steps feel more personal.</p>
      </div>
      <FormAlert>{apiError}</FormAlert>
      <form className="auth-form register-form" onSubmit={handleSubmit} noValidate>
        <TextField id="full_name" label="Full name" value={form.full_name} onChange={(event) => update('full_name', event.target.value)} error={errors.full_name} placeholder="How should we call you?" autoComplete="name" required />
        <TextField id="email" label="Email address" type="email" value={form.email} onChange={(event) => update('email', event.target.value)} error={errors.email} placeholder="you@example.com" autoComplete="email" required />
        <div className="auth-field-row">
          <PasswordField id="password" label="Password" value={form.password} onChange={(event) => update('password', event.target.value)} error={errors.password} autoComplete="new-password" />
          <PasswordField id="confirm_password" label="Confirm password" value={form.confirm_password} onChange={(event) => update('confirm_password', event.target.value)} error={errors.confirm_password} autoComplete="new-password" />
        </div>
        <div className="auth-field-row">
          <SelectField id="education" label="Education" value={form.education} onChange={(event) => update('education', event.target.value)} options={educationOptions} />
          <SelectField id="experience_level" label="Experience level" value={form.experience_level} onChange={(event) => update('experience_level', event.target.value)} options={experienceOptions} />
        </div>
        <p className="form-hint"><span>✦</span> Your information stays private and is only used to personalize your experience.</p>
        <SubmitButton loading={loading}>Create account</SubmitButton>
      </form>
      <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
    </AuthShell>
  )
}
