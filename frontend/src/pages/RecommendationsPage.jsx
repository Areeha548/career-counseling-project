import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { ApiError, getRecommendations } from '../api/client'
import { Brand } from '../components/AuthComponents'
import { getAccessToken, useAuth } from '../context/AuthContext'

function MatchCard({ recommendation }) {
  const [showDetails, setShowDetails] = useState(false)

  return (
    <article className="recommendation-card">
      <div className="recommendation-card-heading">
        <span className="recommendation-rank">MATCH {String(recommendation.ranking).padStart(2, '0')}</span>
        <span className="recommendation-category">{recommendation.category}</span>
      </div>
      <div className="recommendation-title-row">
        <h2>{recommendation.career_title}</h2>
        <strong className="recommendation-score">{Math.round(recommendation.match_score)}<small>%</small></strong>
      </div>
      <div className="recommendation-meter" role="img" aria-label={`${Math.round(recommendation.match_score)} percent match`}>
        <span style={{ width: `${recommendation.match_score}%` }} />
      </div>
      <p className="recommendation-explanation">{recommendation.explanation}</p>
      <div className="recommendation-skills">
        <span className="recommendation-skills-label">RELATED SKILLS</span>
        <div>{recommendation.skills.slice(0, 7).map((skill) => <span key={skill}>{skill}</span>)}</div>
      </div>
      <div className="recommendation-card-actions">
        <button
          type="button"
          className="recommendation-details-toggle"
          aria-expanded={showDetails}
          aria-controls={`career-details-${recommendation.career_id}`}
          onClick={() => setShowDetails((visible) => !visible)}
        >
          {showDetails ? 'Hide Career Details' : 'View Career Details'}
          <span aria-hidden="true">{showDetails ? '−' : '+'}</span>
        </button>
        <Link className="recommendation-skill-gap-link" to={`/careers/${recommendation.career_id}/skill-gap`}>
          Explore Career <span aria-hidden="true">→</span>
        </Link>
      </div>
      {showDetails && (
        <div className="recommendation-details" id={`career-details-${recommendation.career_id}`}>
          <p>{recommendation.description}</p>
          <span>Career difficulty: <b>{recommendation.difficulty_level}</b></span>
        </div>
      )}
    </article>
  )
}

export default function RecommendationsPage() {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [assessmentMissing, setAssessmentMissing] = useState(false)

  useEffect(() => {
    let active = true
    const previousTitle = document.title
    document.title = 'Your Career Matches | AI Career Mentor'
    getRecommendations(getAccessToken())
      .then((result) => { if (active) setData(result) })
      .catch((requestError) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          logout()
          navigate('/login', { replace: true })
          return
        }
        if (requestError instanceof ApiError && requestError.status === 409) {
          setAssessmentMissing(true)
          return
        }
        setError(requestError.message || 'Your career matches could not be loaded. Please try again.')
      })
      .finally(() => { if (active) setIsLoading(false) })
    return () => {
      active = false
      document.title = previousTitle
    }
  }, [logout, navigate])

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="recommendations-page">
      <header className="assessment-header">
        <div className="assessment-header-inner">
          <Brand to="/dashboard" />
          <div className="recommendation-header-links">
            <Link to="/assessment" className="recommendation-header-link">Retake Assessment</Link>
            <button type="button" className="assessment-logout" onClick={handleLogout}>Log out</button>
          </div>
        </div>
      </header>
      <main className="recommendations-main">
        <div className="recommendations-intro">
          <span className="assessment-eyebrow">A DIRECTION TO EXPLORE</span>
          <h1>Your Career <em>Matches</em></h1>
          <p>These paths are ranked from your assessment answers. Match percentages show profile similarity, not a prediction or guarantee of career success.</p>
        </div>

        {isLoading && <div className="recommendations-loading" role="status"><span className="loading-orbit" />Finding your strongest career matches…</div>}

        {!isLoading && assessmentMissing && (
          <section className="recommendations-state-card">
            <span className="assessment-result-icon" aria-hidden="true">◎</span>
            <h2>Your assessment is the first step</h2>
            <p>Complete the 20-question career assessment and we’ll use your answers to find relevant career paths.</p>
            <Link to="/assessment" className="assessment-primary-button">Start Career Assessment <span aria-hidden="true">→</span></Link>
          </section>
        )}

        {!isLoading && error && (
          <section className="recommendations-state-card" role="alert">
            <span className="assessment-result-icon">!</span>
            <h2>We couldn’t load your career matches</h2>
            <p>{error}</p>
            <button type="button" className="assessment-primary-button" onClick={() => window.location.reload()}>Try again</button>
          </section>
        )}

        {!isLoading && data && (
          <>
            <div className="recommendations-summary"><span><b>{data.recommendations.length}</b> personalized paths</span><span>Scores reflect your assessment signals</span></div>
            <section className="recommendation-grid" aria-label="Ranked career recommendations">
              {data.recommendations.map((recommendation) => <MatchCard key={recommendation.career_id} recommendation={recommendation} />)}
            </section>
            <div className="recommendations-bottom-actions">
              <Link to="/assessment" className="assessment-back-link">Retake assessment to refresh your matches</Link>
              <Link to="/dashboard" className="assessment-primary-button">Back to your career space <span aria-hidden="true">→</span></Link>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
