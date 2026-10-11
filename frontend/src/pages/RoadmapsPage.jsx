import { useEffect, useMemo, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'
import { ApiError, createOrResumeRoadmap, getCareerCatalog, getMyRoadmaps, getRoadmapTemplates } from '../api/client'
import { Brand } from '../components/AuthComponents'
import { getAccessToken, useAuth } from '../context/AuthContext'

function ProgressMeter({ value, label }) {
  return (
    <div className="roadmap-meter" role="progressbar" aria-label={label} aria-valuemin="0" aria-valuemax="100" aria-valuenow={value}>
      <span style={{ width: `${value}%` }} />
    </div>
  )
}

export default function RoadmapsPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { logout } = useAuth()
  const [careers, setCareers] = useState([])
  const [templates, setTemplates] = useState([])
  const [roadmaps, setRoadmaps] = useState([])
  const [selectedCareerId, setSelectedCareerId] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    const previousTitle = document.title
    document.title = 'Your Roadmaps | AI Career Mentor'
    Promise.all([getCareerCatalog(), getRoadmapTemplates(), getMyRoadmaps(getAccessToken())])
      .then(([careerRows, templateRows, roadmapRows]) => {
        if (!active) return
        setCareers(careerRows)
        setTemplates(templateRows)
        setRoadmaps(roadmapRows)
        const requested = location.state?.careerId
        const firstChoice = templateRows.find((item) => item.career_id === Number(requested)) || templateRows[0]
        setSelectedCareerId(firstChoice ? String(firstChoice.career_id) : '')
      })
      .catch((requestError) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          logout()
          navigate('/login', { replace: true })
          return
        }
        setError(requestError.message || 'Roadmaps could not be loaded. Please try again.')
      })
      .finally(() => { if (active) setIsLoading(false) })
    return () => { active = false; document.title = previousTitle }
  }, [location.state, logout, navigate])

  const templateByCareer = useMemo(
    () => new Map(templates.map((template) => [template.career_id, template])),
    [templates],
  )
  const sortedCareers = useMemo(() => [...careers].sort((a, b) => a.name.localeCompare(b.name)), [careers])

  async function startRoadmap(event) {
    event.preventDefault()
    if (!selectedCareerId) return
    setIsCreating(true)
    setError('')
    try {
      const roadmap = await createOrResumeRoadmap(selectedCareerId, getAccessToken())
      navigate(`/careers/${roadmap.career_id}/roadmap`)
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        logout()
        navigate('/login', { replace: true })
        return
      }
      setError(requestError.message || 'This roadmap could not be opened. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="roadmaps-page">
      <header className="assessment-header"><div className="assessment-header-inner">
        <Brand to="/dashboard" />
        <div className="recommendation-header-links"><Link to="/dashboard" className="recommendation-header-link">Dashboard</Link><button type="button" className="assessment-logout" onClick={handleLogout}>Log out</button></div>
      </div></header>
      <main className="roadmaps-main">
        <section className="roadmaps-hero">
          <span className="assessment-eyebrow">A PRACTICAL PLAN FOR YOUR NEXT STEP</span>
          <h1>Your Career <em>Roadmaps</em></h1>
          <p>Choose a career to get an ordered learning plan based on its skill requirements and your saved skill profile. Your progress is private and saved to your account.</p>
        </section>

        {isLoading && <div className="roadmap-state" role="status"><span className="loading-orbit" />Loading your roadmaps and career catalog…</div>}
        {!isLoading && error && <section className="roadmap-state roadmap-state-error" role="alert"><h2>We couldn’t load your roadmaps</h2><p>{error}</p><button type="button" className="assessment-primary-button" onClick={() => window.location.reload()}>Try again</button></section>}

        {!isLoading && !error && (
          <>
            <section className="roadmap-picker-card" aria-labelledby="roadmap-picker-heading">
              <div className="roadmap-picker-art" aria-hidden="true"><span>01</span><i /><i /><i /></div>
              <div className="roadmap-picker-copy">
                <span className="roadmap-overline">START OR RESUME</span>
                <h2 id="roadmap-picker-heading">Choose a career path</h2>
                <p>Choose from all careers in our catalog. Every career has an ordered plan based on its real skill requirements; an assessment is not required.</p>
                <form className="roadmap-picker-form" onSubmit={startRoadmap}>
                  <label htmlFor="roadmap-career-select">Career</label>
                  <select id="roadmap-career-select" value={selectedCareerId} onChange={(event) => setSelectedCareerId(event.target.value)} required>
                    <option value="" disabled>Select a career</option>
                    {sortedCareers.map((career) => {
                      const template = templateByCareer.get(career.id)
                      return <option key={career.id} value={career.id} disabled={!template}>{career.name}{template ? '' : ' — roadmap coming soon'}</option>
                    })}
                  </select>
                  {selectedCareerId && templateByCareer.has(Number(selectedCareerId)) && <p className="roadmap-selected-summary">{templateByCareer.get(Number(selectedCareerId)).summary}</p>}
                  {error && <p className="roadmap-inline-error" role="alert">{error}</p>}
                  <button type="submit" className="assessment-primary-button" disabled={isCreating || !selectedCareerId}>
                    {isCreating ? 'Opening your roadmap…' : roadmaps.some((roadmap) => roadmap.career_id === Number(selectedCareerId)) ? 'Resume roadmap' : 'Build my roadmap'}
                    <span aria-hidden="true">→</span>
                  </button>
                </form>
              </div>
            </section>

            <section className="roadmap-list-section" aria-labelledby="roadmap-list-heading">
              <div className="roadmap-section-heading"><div><span className="assessment-eyebrow">YOUR SAVED PROGRESS</span><h2 id="roadmap-list-heading">Continue where you left off</h2></div><span>{roadmaps.length} {roadmaps.length === 1 ? 'roadmap' : 'roadmaps'}</span></div>
              {roadmaps.length === 0 ? (
                <div className="roadmap-empty-card"><span aria-hidden="true">✳</span><div><h3>Your learning progress will appear here</h3><p>Pick a career above to create your first roadmap. You can keep separate plans for different careers.</p></div></div>
              ) : (
                <div className="roadmap-summary-grid">
                  {roadmaps.map((roadmap) => (
                    <article className="roadmap-summary-card" key={roadmap.id}>
                      <div className="roadmap-summary-meta"><span>{roadmap.category}</span><span>Template v{roadmap.template_version}</span></div>
                      <h3>{roadmap.career_name}</h3>
                      <p>{roadmap.current_phase ? `Next up: ${roadmap.current_phase}` : 'All required steps are complete.'}</p>
                      <ProgressMeter value={roadmap.completion_percent} label={`${roadmap.career_name} completion`} />
                      <div className="roadmap-summary-progress"><b>{roadmap.completion_percent}%</b><span>{roadmap.completed_steps} of {roadmap.total_steps} required steps</span></div>
                      <Link to={`/careers/${roadmap.career_id}/roadmap`} className="roadmap-card-link">{roadmap.status === 'completed' ? 'Review roadmap' : 'Resume roadmap'} <span aria-hidden="true">→</span></Link>
                    </article>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
        <p className="roadmap-metric-note">Progress is a learning tracker for this project. It is not a guarantee of job readiness.</p>
      </main>
    </div>
  )
}
