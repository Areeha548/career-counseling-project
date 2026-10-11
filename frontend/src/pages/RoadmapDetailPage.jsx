import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { ApiError, createOrResumeRoadmap, updateRoadmapStep } from '../api/client'
import { Brand } from '../components/AuthComponents'
import { getAccessToken, useAuth } from '../context/AuthContext'

const LEVEL_LABELS = ['Not familiar', 'Beginner', 'Intermediate', 'Advanced']

function ProgressMeter({ value, label }) {
  return <div className="roadmap-meter" role="progressbar" aria-label={label} aria-valuemin="0" aria-valuemax="100" aria-valuenow={value}><span style={{ width: `${value}%` }} /></div>
}

function StepCard({ step, isBusy, onUpdate }) {
  return (
    <article className={`roadmap-step-card roadmap-step-${step.status}${step.is_optional ? ' roadmap-step-optional' : ''}`}>
      <div className="roadmap-step-marker" aria-hidden="true">{step.status === 'completed' ? '✓' : String(step.order).padStart(2, '0')}</div>
      <div className="roadmap-step-content">
        <div className="roadmap-step-heading"><div><span className="roadmap-step-state">{step.is_optional ? 'OPTIONAL REVIEW' : step.status.replace('_', ' ').toUpperCase()}</span><h4>{step.title}</h4></div>{step.skill_name && <span className="roadmap-skill-chip">{step.skill_name}</span>}</div>
        {step.skill_name && <p className="roadmap-step-level">Your level when this plan was created: <b>{LEVEL_LABELS[step.proficiency_level_at_creation ?? 0]}</b>{step.target_level ? ` · target: ${LEVEL_LABELS[step.target_level]}` : ''}{step.priority ? ` · ${step.priority} priority` : ''}</p>}
        {step.estimated_minutes != null && <p className="roadmap-step-time">Estimated time: {step.estimated_minutes >= 60 ? `${Math.round(step.estimated_minutes / 60 * 10) / 10} hours` : `${step.estimated_minutes} minutes`}</p>}
        {step.prerequisites && <p className="roadmap-step-prerequisite"><b>Prerequisite:</b> {step.prerequisites}</p>}
        <p>{step.instructions}</p>
        <div className="roadmap-completion-criteria"><span>DONE WHEN</span><p>{step.completion_criteria}</p></div>
        {step.resource_url && <a className="roadmap-resource-link" href={step.resource_url} target="_blank" rel="noreferrer">{step.resource_title || 'Open learning resource'} <span aria-hidden="true">↗</span></a>}
        {!step.resource_url && step.resource_search && <p className="roadmap-resource-search"><b>Resource search suggestion:</b> {step.resource_search}</p>}
        <div className="roadmap-step-actions">
          {step.status === 'not_started' && <button type="button" onClick={() => onUpdate(step.id, 'in_progress')} disabled={isBusy}>Start this step</button>}
          {step.status === 'in_progress' && <><button type="button" className="roadmap-step-complete" onClick={() => onUpdate(step.id, 'completed')} disabled={isBusy}>Mark complete</button><button type="button" className="roadmap-step-secondary" onClick={() => onUpdate(step.id, 'not_started')} disabled={isBusy}>Reset</button></>}
          {step.status === 'completed' && <button type="button" className="roadmap-step-secondary" onClick={() => onUpdate(step.id, 'in_progress')} disabled={isBusy}>Reopen step</button>}
          {isBusy && <span role="status">Saving…</span>}
        </div>
      </div>
    </article>
  )
}

export default function RoadmapDetailPage() {
  const { careerId } = useParams()
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [roadmap, setRoadmap] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [busyStep, setBusyStep] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    const previousTitle = document.title
    document.title = 'Career Roadmap | AI Career Mentor'
    createOrResumeRoadmap(careerId, getAccessToken())
      .then((result) => { if (active) setRoadmap(result) })
      .catch((requestError) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          logout()
          navigate('/login', { replace: true })
          return
        }
        setError(requestError.message || 'This roadmap could not be opened. Please return to your roadmap list.')
      })
      .finally(() => { if (active) setIsLoading(false) })
    return () => { active = false; document.title = previousTitle }
  }, [careerId, logout, navigate])

  async function changeStep(stepId, status) {
    setBusyStep(stepId)
    setError('')
    try {
      const updated = await updateRoadmapStep(roadmap.id, stepId, status, getAccessToken())
      setRoadmap(updated)
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        logout()
        navigate('/login', { replace: true })
        return
      }
      setError(requestError.message || 'Your progress could not be saved. Please try again.')
    } finally {
      setBusyStep(null)
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
        <div className="recommendation-header-links"><Link to="/roadmaps" className="recommendation-header-link">All roadmaps</Link><button type="button" className="assessment-logout" onClick={handleLogout}>Log out</button></div>
      </div></header>
      <main className="roadmap-detail-main">
        <Link to="/roadmaps" className="roadmap-back-link">← Your roadmaps</Link>
        {isLoading && <div className="roadmap-state" role="status"><span className="loading-orbit" />Preparing your personalized roadmap…</div>}
        {!isLoading && error && !roadmap && <section className="roadmap-state roadmap-state-error" role="alert"><h1>Roadmap unavailable</h1><p>{error}</p><Link to="/roadmaps" className="assessment-primary-button">Choose another career</Link></section>}

        {!isLoading && roadmap && (
          <>
            <section className="roadmap-detail-hero">
              <span className="assessment-eyebrow">{roadmap.category.toUpperCase()} · ROADMAP V{roadmap.template_version}</span>
              <h1>Your path to <em>{roadmap.career_name}</em></h1>
              <p className="roadmap-career-description">{roadmap.career_description}</p>
              <p className="roadmap-template-summary">{roadmap.summary}</p>
              <div className="roadmap-progress-card">
                <div className="roadmap-progress-heading"><div><span>YOUR LEARNING PROGRESS</span><strong>{roadmap.completion_percent}%</strong></div><span>{roadmap.completed_steps} of {roadmap.total_steps} required steps</span></div>
                <ProgressMeter value={roadmap.completion_percent} label="Overall roadmap completion" />
                <div className="roadmap-resume-note">{roadmap.status === 'completed' ? 'All required steps are complete. You can revisit any step below.' : `Resume at: ${roadmap.current_phase || 'the next step'}`}</div>
              </div>
              <p className="roadmap-personalization-note" role="note">{roadmap.personalization_note}</p>
              {roadmap.skill_profile_was_empty && <Link to={`/careers/${roadmap.career_id}/skill-gap`} className="roadmap-skill-profile-cta">Add your current skills for more tailored future planning <span aria-hidden="true">→</span></Link>}
            </section>

            {error && <p className="roadmap-inline-error" role="alert">{error}</p>}
            {roadmap.status === 'completed' && <section className="roadmap-complete-banner" role="status"><span aria-hidden="true">✓</span><div><h2>Roadmap complete</h2><p>You have marked every required step complete. Keep your project examples ready to share.</p></div></section>}

            <section className="roadmap-phases" aria-label="Roadmap phases">
              {roadmap.phases.map((phase) => (
                <article className="roadmap-phase-card" key={phase.id}>
                  <header className="roadmap-phase-header"><div className="roadmap-phase-number">{String(phase.order).padStart(2, '0')}</div><div className="roadmap-phase-copy"><span>PHASE {phase.order}</span><h2>{phase.title}</h2><p>{phase.objective}</p></div><div className="roadmap-phase-progress"><strong>{phase.completion_percent}%</strong><span>{phase.completed_steps}/{phase.total_steps} required</span></div></header>
                  <p className="roadmap-phase-description">{phase.description}</p>
                  {phase.steps.length === 0 ? <p className="roadmap-no-steps">No individual skill steps are needed in this phase. Continue to the practical work.</p> : <div className="roadmap-step-list">{phase.steps.map((step) => <StepCard key={step.id} step={step} isBusy={busyStep === step.id} onUpdate={changeStep} />)}</div>}
                </article>
              ))}
            </section>
            <div className="roadmap-bottom-links"><Link to={`/careers/${roadmap.career_id}/skill-gap`}>Review your skill gap</Link><Link to="/roadmaps" className="assessment-primary-button">Manage roadmaps <span aria-hidden="true">→</span></Link></div>
            <p className="roadmap-metric-note">Completion is self-reported learning progress, not a guarantee of job readiness.</p>
          </>
        )}
      </main>
    </div>
  )
}
