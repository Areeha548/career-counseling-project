import { useState } from 'react'
import { Link } from 'react-router'

export function Brand({ light = false, to = '/' }) {
  return (
    <Link className={`auth-brand${light ? ' auth-brand-light' : ''}`} to={to}>
      <span className="auth-brand-mark" aria-hidden="true">✦</span>
      <span>AI Career <b>Mentor</b></span>
    </Link>
  )
}

export function AuthShell({ children, mode = '' }) {
  return (
    <div className={`auth-shell ${mode}`}>
      <aside className="auth-visual">
        <div className="auth-visual-glow auth-glow-one" />
        <div className="auth-visual-glow auth-glow-two" />
        <div className="auth-visual-content">
          <Brand light />
          <div className="auth-visual-copy">
            <span className="auth-kicker"><i /> A clearer path starts here</span>
            <h1>Make your next<br />move <em>meaningful.</em></h1>
            <p>Find direction, build confidence, and take your career journey one thoughtful step at a time.</p>
            <div className="auth-benefits">
              <div><span className="benefit-check">✓</span><span>Discover your strengths<small>See what makes you, you</small></span></div>
              <div><span className="benefit-check">✓</span><span>Build your personalized roadmap<small>Turn ideas into practical steps</small></span></div>
              <div><span className="benefit-check">✓</span><span>Move confidently toward your career<small>Keep your next chapter in view</small></span></div>
            </div>
          </div>
          <div className="auth-visual-art" aria-hidden="true">
            <div className="auth-art-orbit auth-orbit-outer" />
            <div className="auth-art-orbit auth-orbit-inner" />
            <div className="auth-art-center"><span>✦</span><small>YOUR<br />POTENTIAL</small></div>
            <span className="auth-art-node node-top">✧</span><span className="auth-art-node node-right">↗</span>
            <span className="auth-art-node node-bottom">✳</span><span className="auth-art-node node-left">◎</span>
            <div className="auth-art-tag art-tag-one"><span>01</span> Discover</div>
            <div className="auth-art-tag art-tag-two"><span>02</span> Grow</div>
          </div>
          <div className="auth-visual-footer"><span>CAREER CLARITY, BUILT AROUND YOU</span><span>✦</span></div>
        </div>
      </aside>
      <main className="auth-main">
        <div className="auth-mobile-brand"><Brand /></div>
        <div className="auth-form-wrap">{children}</div>
        <p className="auth-legal">A thoughtful beginning to your next chapter.</p>
      </main>
    </div>
  )
}

export function TextField({ id, label, type = 'text', value, onChange, error, placeholder, autoComplete, required = false }) {
  const errorId = `${id}-error`
  return (
    <div className={`form-field${error ? ' form-field-error' : ''}`}>
      <label htmlFor={id}>{label}{required && <span className="required-mark"> *</span>}</label>
      <input id={id} name={id} type={type} value={value} onChange={onChange} placeholder={placeholder}
        autoComplete={autoComplete} required={required} aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined} />
      {error && <span className="field-error" id={errorId}>{error}</span>}
    </div>
  )
}

export function PasswordField({ id, label, value, onChange, error, autoComplete, required = true }) {
  const [visible, setVisible] = useState(false)
  const errorId = `${id}-error`
  return (
    <div className={`form-field${error ? ' form-field-error' : ''}`}>
      <label htmlFor={id}>{label}{required && <span className="required-mark"> *</span>}</label>
      <div className="password-input-wrap">
        <input id={id} name={id} type={visible ? 'text' : 'password'} value={value} onChange={onChange}
          autoComplete={autoComplete} required={required} aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined} />
        <button className="password-toggle" type="button" onClick={() => setVisible(!visible)}
          aria-label={visible ? 'Hide password' : 'Show password'}>{visible ? 'Hide' : 'Show'}</button>
      </div>
      {error && <span className="field-error" id={errorId}>{error}</span>}
    </div>
  )
}

export function SelectField({ id, label, value, onChange, options }) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label} <span className="optional-mark">Optional</span></label>
      <select id={id} name={id} value={value} onChange={onChange}>
        <option value="">Choose one</option>
        {options.map((option) => <option value={option} key={option}>{option}</option>)}
      </select>
    </div>
  )
}

export function FormAlert({ children, success = false }) {
  if (!children) return null
  return <div className={`form-alert${success ? ' form-alert-success' : ''}`} role={success ? 'status' : 'alert'}>{children}</div>
}

export function SubmitButton({ children, loading }) {
  return <button className="auth-submit" type="submit" disabled={loading}>
    {loading ? <><span className="button-spinner" aria-hidden="true" /> Please wait…</> : <>{children}<span aria-hidden="true">→</span></>}
  </button>
}
