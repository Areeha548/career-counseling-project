import { Link, useNavigate } from 'react-router'
import { Brand } from '../components/AuthComponents'
import { getAccessToken, useAuth } from '../context/AuthContext'
import { useEffect, useState } from 'react'
import { ApiError, getMyAssessmentResults, getRecommendations } from '../api/client'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [assessmentResults, setAssessmentResults] = useState(null)
  const [hasRecommendations, setHasRecommendations] = useState(false)
  const [assessmentError, setAssessmentError] = useState('')
  const [recommendationError, setRecommendationError] = useState('')

  useEffect(() => {
    let active = true
    getMyAssessmentResults(getAccessToken())
      .then((results) => {
        if (!active) return
        setAssessmentResults(results)
        if (results.completed) {
          setHasRecommendations(true)
          getRecommendations(getAccessToken()).catch((error) => {
            if (!active) return
            if (error instanceof ApiError && error.status === 401) {
              logout()
              navigate('/login', { replace: true })
              return
            }
            setRecommendationError('Your assessment is saved, but career matches could not be checked just now.')
          })
        }
      })
      .catch((error) => {
        if (!active) return
        if (error instanceof ApiError && error.status === 401) {
          logout()
          navigate('/login', { replace: true })
          return
        }
        setAssessmentResults(null)
        setAssessmentError('Assessment status is temporarily unavailable. You can still open the assessment below.')
      })

    return () => { active = false }
  }, [logout, navigate])

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  const initials = (user?.full_name || 'Career Mentor')
    .split(' ')
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="dashboard-nav">
          <Brand />
          <div className="dashboard-nav-right">
            <Link to="/" className="dashboard-home-link">Explore the site</Link>
            <div className="dashboard-user-chip"><span>{initials}</span><b>{user?.full_name}</b></div>
            <button className="logout-button" onClick={handleLogout}>Log out <span aria-hidden="true">↗</span></button>
          </div>
        </div>
      </header>
      <main className="dashboard-main">
        <section className="dashboard-welcome">
          <div>
            <span className="form-eyebrow">YOUR CAREER SPACE</span>
            <h1>Welcome, {user?.full_name?.split(' ')[0] || 'there'} <span>✦</span></h1>
            <p>Your next chapter starts with a little curiosity. This is your space to explore what could be next.</p>
          </div>
          <div className="welcome-spark" aria-hidden="true">✳</div>
        </section>
        <section className="dashboard-assessment-spotlight" aria-labelledby="dashboard-assessment-title">
          <div className="dashboard-assessment-copy">
            <span className="dashboard-assessment-eyebrow">A THOUGHTFUL PLACE TO START</span>
            <h2 id="dashboard-assessment-title">Career Assessment</h2>
            <p>Answer a few questions to discover which career paths may suit you.</p>
            <div className="dashboard-assessment-meta">
              <span aria-hidden="true">✦</span>
              {assessmentResults?.completed ? 'Assessment Completed' : '20 questions · About 5 minutes'}
            </div>
            {hasRecommendations && <Link to="/recommendations" className="dashboard-match-link">View your career matches <span aria-hidden="true">→</span></Link>}
            {assessmentError && <p className="dashboard-data-error" role="alert">{assessmentError}</p>}
            {recommendationError && <p className="dashboard-data-error" role="status">{recommendationError}</p>}
          </div>
          <Link to="/assessment" className="dashboard-assessment-button">
            {assessmentResults?.completed ? 'Retake Assessment' : 'Start Career Assessment'}
            <span aria-hidden="true">→</span>
          </Link>
          <div className="dashboard-assessment-art" aria-hidden="true"><i /><i /><i /></div>
        </section>
        <section className="profile-overview">
          <div className="profile-card">
            <span className="profile-card-icon">◎</span>
            <div><span className="card-overline">YOUR PROFILE</span><h2>A strong start</h2><p>Your account is ready for the next step in your career journey.</p></div>
            <div className="profile-detail"><span>NAME</span><b>{user?.full_name}</b></div>
            <div className="profile-detail"><span>EMAIL</span><b>{user?.email}</b></div>
          </div>
          <aside className="dashboard-note-card">
            <div className="note-spark">✦</div>
            <span className="card-overline">A NOTE FOR YOUR JOURNEY</span>
            <h2>Every great direction begins with a question.</h2>
            <p>Take your time. Your career path is yours to shape.</p>
            <div className="note-decoration" aria-hidden="true"><i /><i /><i /></div>
          </aside>
        </section>
        <section className="dashboard-next">
          <div className="dashboard-section-heading"><div><span className="form-eyebrow">WHEN YOU’RE READY</span><h2>Your career journey</h2></div><span className="coming-soon-label">MORE TO COME</span></div>
          <div className="journey-preview-grid">
            <article className="journey-preview-card journey-assessment-card"><span className="journey-number">01</span><span className="journey-icon">⌕</span><h3>Discover your strengths</h3><p>Find the interests and abilities that make your path your own.</p><Link to="/assessment" className="journey-action">Start or retake assessment <span aria-hidden="true">→</span></Link></article>
            <article className="journey-preview-card"><span className="journey-number">02</span><span className="journey-icon">↗</span><h3>Explore career paths</h3><p>Review your assessment-based matches and explore promising roles.</p>{hasRecommendations ? <Link to="/recommendations" className="journey-action">View career matches <span aria-hidden="true">→</span></Link> : <span className="journey-status">Complete your assessment first</span>}</article>
            <article className="journey-preview-card"><span className="journey-number">03</span><span className="journey-icon">✳</span><h3>Plan your next steps</h3><p>Turn a career choice into practical learning phases and saved progress.</p><Link to="/roadmaps" className="journey-action">Explore career roadmaps <span aria-hidden="true">→</span></Link></article>
          </div>
        </section>
      </main>
      <footer className="dashboard-footer"><Brand /><span>Thoughtfully built for your next chapter.</span></footer>
    </div>
  )
}
