import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import {
  ApiError,
  getCareerSkillGap,
  getMySkillProfile,
  getSkillCatalog,
  saveMySkillProfile,
} from '../api/client'
import { Brand } from '../components/AuthComponents'
import { getAccessToken, useAuth } from '../context/AuthContext'

const PROFICIENCY_LEVELS = [
  { value: 0, label: 'Not familiar' },
  { value: 1, label: 'Beginner' },
  { value: 2, label: 'Intermediate' },
  { value: 3, label: 'Advanced' },
]

const GAP_GROUPS = [
  { key: 'strong', title: 'Strong skills', summary: 'At or above the target level' },
  { key: 'developing', title: 'Developing', summary: 'Skills to keep building' },
  { key: 'gap', title: 'Skills to learn', summary: 'Not yet in your profile' },
]

export default function SkillGapPage() {
  const { careerId } = useParams()
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [careerGap, setCareerGap] = useState(null)
  const [catalog, setCatalog] = useState([])
  const [profile, setProfile] = useState({})
  const [search, setSearch] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isEditorOpen, setIsEditorOpen] = useState(false)
  const [error, setError] = useState('')
  const [saveMessage, setSaveMessage] = useState('')

  useEffect(() => {
    let active = true
    const previousTitle = document.title
    document.title = 'Skill Gap Analysis | AI Career Mentor'

    Promise.all([
      getCareerSkillGap(careerId, getAccessToken()),
      getSkillCatalog(),
      getMySkillProfile(getAccessToken()),
    ])
      .then(([gap, skills, savedProfile]) => {
        if (!active) return
        setCareerGap(gap)
        setCatalog(skills)
        setProfile(Object.fromEntries(savedProfile.skills.map((skill) => [skill.skill_id, skill.proficiency_level])))
        setIsEditorOpen(savedProfile.count === 0)
      })
      .catch((requestError) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          logout()
          navigate('/login', { replace: true })
          return
        }
        setError(requestError.message || 'We could not load this career skill profile. Please try again.')
      })
      .finally(() => { if (active) setIsLoading(false) })

    return () => {
      active = false
      document.title = previousTitle
    }
  }, [careerId, logout, navigate])

  const selectedIds = useMemo(() => new Set(Object.keys(profile).map(Number)), [profile])
  const filteredSkills = useMemo(() => {
    const query = search.trim().toLocaleLowerCase()
    return catalog
      .filter((skill) => !selectedIds.has(skill.id))
      .filter((skill) => !query || `${skill.name} ${skill.category}`.toLocaleLowerCase().includes(query))
      .slice(0, 24)
  }, [catalog, search, selectedIds])
  const selectedSkills = useMemo(
    () => catalog.filter((skill) => selectedIds.has(skill.id)).sort((a, b) => a.name.localeCompare(b.name)),
    [catalog, selectedIds],
  )

  function addSkill(skillId) {
    setProfile((current) => ({ ...current, [skillId]: 1 }))
    setSaveMessage('')
    setSearch('')
  }

  function changeLevel(skillId, value) {
    setProfile((current) => ({ ...current, [skillId]: Number(value) }))
    setSaveMessage('')
  }

  function removeSkill(skillId) {
    setProfile((current) => {
      const next = { ...current }
      delete next[skillId]
      return next
    })
    setSaveMessage('')
  }

  async function saveProfile(event) {
    event.preventDefault()
    setIsSaving(true)
    setError('')
    setSaveMessage('')
    try {
      const skills = Object.entries(profile).map(([skillId, proficiencyLevel]) => ({
        skill_id: Number(skillId),
        proficiency_level: proficiencyLevel,
      }))
      const saved = await saveMySkillProfile(skills, getAccessToken())
      const updatedGap = await getCareerSkillGap(careerId, getAccessToken())
      setCareerGap(updatedGap)
      setProfile(Object.fromEntries(saved.skills.map((skill) => [skill.skill_id, skill.proficiency_level])))
      setSaveMessage('Your skill profile and this career comparison are up to date.')
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        logout()
        navigate('/login', { replace: true })
        return
      }
      setError(requestError.message || 'Your skill profile could not be saved. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="skill-gap-page">
      <header className="assessment-header">
        <div className="assessment-header-inner">
          <Brand to="/dashboard" />
          <div className="recommendation-header-links">
            <Link to="/recommendations" className="recommendation-header-link">Career matches</Link>
            <button type="button" className="assessment-logout" onClick={handleLogout}>Log out</button>
          </div>
        </div>
      </header>

      <main className="skill-gap-main">
        <Link to="/recommendations" className="skill-gap-back-link">← Back to your career matches</Link>
        {isLoading && <div className="skill-gap-state" role="status"><span className="loading-orbit" />Loading career skill profile…</div>}

        {!isLoading && error && !careerGap && (
          <section className="skill-gap-state skill-gap-error" role="alert">
            <span className="assessment-result-icon">!</span>
            <h1>We couldn’t open this career</h1>
            <p>{error}</p>
            <Link to="/recommendations" className="assessment-primary-button">Return to career matches</Link>
          </section>
        )}

        {!isLoading && careerGap && (
          <>
            <section className="skill-gap-hero">
              <span className="assessment-eyebrow">A CLEARER VIEW OF YOUR NEXT STEPS</span>
              <div className="skill-gap-heading-row">
                <div>
                  <span className="skill-gap-category">{careerGap.career.category}</span>
                  <h1>Your Skill Gap for <em>{careerGap.career.name}</em></h1>
                  <p>{careerGap.career.description}</p>
                </div>
                <span className="skill-gap-difficulty">{careerGap.career.difficulty_level} pathway</span>
              </div>
            </section>

            <section className="skill-readiness-card" aria-label="Skill readiness summary">
              <div className="skill-readiness-top">
                <div><span className="skill-gap-overline">CAREER SKILL READINESS</span><h2>{careerGap.readiness_percent}%</h2></div>
                <span className="skill-readiness-total">{careerGap.total_required} skills in this career profile</span>
              </div>
              <div className="skill-readiness-meter" role="progressbar" aria-label="Career skill readiness" aria-valuemin="0" aria-valuemax="100" aria-valuenow={careerGap.readiness_percent}>
                <span style={{ width: `${careerGap.readiness_percent}%` }} />
              </div>
              <div className="skill-readiness-counts">
                <span><b>{careerGap.strong_count}</b> Strong</span>
                <span><b>{careerGap.developing_count}</b> Developing</span>
                <span><b>{careerGap.gap_count}</b> To learn</span>
              </div>
              <p className="skill-readiness-note">{careerGap.readiness_note}</p>
            </section>

            <section className="skill-profile-editor" aria-labelledby="skill-profile-title">
              <div className="skill-profile-editor-heading">
                <div><span className="assessment-eyebrow">YOUR SIDE OF THE PICTURE</span><h2 id="skill-profile-title">Your Current Skills</h2><p>Add skills you have and choose a level. You can update this profile whenever you like.</p></div>
                {selectedSkills.length > 0 && <button type="button" className="skill-edit-toggle" onClick={() => setIsEditorOpen((open) => !open)}>{isEditorOpen ? 'Close editor' : 'Edit my skills'}</button>}
              </div>

              {selectedSkills.length === 0 && (
                <div className="skill-profile-empty" role="status">
                  <span aria-hidden="true">✦</span>
                  <div><h3>Start with what you already know</h3><p>Tell us what skills you have to calculate a more personal comparison for {careerGap.career.name}.</p></div>
                  <button type="button" className="assessment-primary-button" onClick={() => setIsEditorOpen(true)}>Add My Skills <span aria-hidden="true">→</span></button>
                </div>
              )}

              {isEditorOpen && (
                <form className="skill-profile-form" onSubmit={saveProfile}>
                  <label className="skill-search-label" htmlFor="skill-search">Find a skill in our catalog</label>
                  <input id="skill-search" className="skill-search-input" type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search 120 skills…" autoComplete="off" />
                  {filteredSkills.length > 0 && (
                    <div className="skill-search-results" aria-label="Available skills">
                      {filteredSkills.map((skill) => <button type="button" className="skill-search-result" key={skill.id} onClick={() => addSkill(skill.id)}><span><b>{skill.name}</b><small>{skill.category}</small></span><span aria-hidden="true">+ Add</span></button>)}
                    </div>
                  )}
                  {search && filteredSkills.length === 0 && <p className="skill-search-empty">No matching skills left to add. Try another search.</p>}

                  {selectedSkills.length > 0 && (
                    <div className="skill-profile-list">
                      <h3>Skills in your profile <span>{selectedSkills.length}</span></h3>
                      {selectedSkills.map((skill) => (
                        <div className="skill-profile-row" key={skill.id}>
                          <div className="skill-profile-name"><b>{skill.name}</b><small>{skill.category}</small></div>
                          <label htmlFor={`proficiency-${skill.id}`}>Your level</label>
                          <select id={`proficiency-${skill.id}`} value={profile[skill.id]} onChange={(event) => changeLevel(skill.id, event.target.value)}>
                            {PROFICIENCY_LEVELS.map((level) => <option key={level.value} value={level.value}>{level.label}</option>)}
                          </select>
                          <button type="button" className="skill-remove-button" onClick={() => removeSkill(skill.id)} aria-label={`Remove ${skill.name}`}>Remove</button>
                        </div>
                      ))}
                    </div>
                  )}

                  {error && <p className="skill-gap-inline-error" role="alert">{error}</p>}
                  {saveMessage && <p className="skill-gap-save-message" role="status">{saveMessage}</p>}
                  <div className="skill-profile-form-actions"><span>Levels are self-reported and can be changed later.</span><button type="submit" className="assessment-primary-button" disabled={isSaving}>{isSaving ? 'Saving your skills…' : 'Save My Skills'}</button></div>
                </form>
              )}

              {!isEditorOpen && saveMessage && <p className="skill-gap-save-message" role="status">{saveMessage}</p>}
              {!isEditorOpen && error && <p className="skill-gap-inline-error" role="alert">{error}</p>}
            </section>

            <section className="skill-gap-results" aria-label="Required career skills">
              <div className="skill-gap-results-heading"><div><span className="assessment-eyebrow">ROLE REQUIREMENTS</span><h2>Skills for this career</h2></div><span>Priority reflects the catalog’s career-specific skill order.</span></div>
              <div className="skill-gap-groups">
                {GAP_GROUPS.map((group) => {
                  const items = careerGap.skills.filter((skill) => skill.status === group.key)
                  return (
                    <section className={`skill-gap-group skill-gap-group-${group.key}`} key={group.key} aria-labelledby={`skill-group-${group.key}`}>
                      <div className="skill-gap-group-heading"><div><h3 id={`skill-group-${group.key}`}>{group.title}</h3><p>{group.summary}</p></div><span>{items.length}</span></div>
                      {items.length === 0 ? <p className="skill-gap-group-empty">No skills in this group right now.</p> : (
                        <ul>{items.map((skill) => (
                          <li key={skill.skill_id}>
                            <div className="skill-gap-skill-name"><b>{skill.name}</b><small>{skill.proficiency_label} <span aria-hidden="true">·</span> target: {skill.target_label}</small></div>
                            <span className={`skill-priority skill-priority-${skill.priority}`}>{skill.priority} priority</span>
                          </li>
                        ))}</ul>
                      )}
                    </section>
                  )
                })}
              </div>
            </section>
            <div className="skill-gap-footer-action"><Link to="/recommendations" className="assessment-back-link">Compare another career match</Link><Link to="/dashboard" className="assessment-primary-button">Back to Dashboard <span aria-hidden="true">→</span></Link></div>
          </>
        )}
      </main>
    </div>
  )
}
