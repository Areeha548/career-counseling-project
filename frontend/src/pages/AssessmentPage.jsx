import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { ApiError, getAssessmentQuestions, getMyAssessmentResults, submitAssessment } from '../api/client'
import { Brand } from '../components/AuthComponents'
import { getAccessToken, useAuth } from '../context/AuthContext'

function titleForCategory(category) {
  return category.replaceAll('_', ' ')
}

export default function AssessmentPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [step, setStep] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [answerError, setAnswerError] = useState('')
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    let active = true
    const previousTitle = document.title
    document.title = 'Career Assessment | AI Career Mentor'
    const token = getAccessToken()

    Promise.all([getAssessmentQuestions(token), getMyAssessmentResults(token)])
      .then(([questionList, results]) => {
        if (!active) return
        setQuestions(questionList)
        const previousAnswers = Object.fromEntries(
          results.responses.map((response) => [response.question_id, response.selected_option]),
        )
        setAnswers(previousAnswers)
      })
      .catch((requestError) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          logout()
          navigate('/login', { replace: true })
          return
        }
        setError(requestError.message || 'We could not load the assessment. Please try again.')
      })
      .finally(() => { if (active) setIsLoading(false) })

    return () => {
      active = false
      document.title = previousTitle
    }
  }, [logout, navigate])

  const question = questions[step]

  function chooseAnswer(value) {
    setAnswers((current) => ({ ...current, [question.id]: value }))
    setAnswerError('')
    setError('')
  }

  function goNext() {
    if (!answers[question.id]) {
      setAnswerError('Choose the option that feels closest to you to continue.')
      return
    }
    setAnswerError('')
    setStep((current) => Math.min(current + 1, questions.length - 1))
  }

  function goBack() {
    setAnswerError('')
    setStep((current) => Math.max(current - 1, 0))
  }

  async function handleSubmit() {
    if (!answers[question.id]) {
      setAnswerError('Choose an answer before saving your assessment.')
      return
    }

    setIsSubmitting(true)
    setError('')
    try {
      const payload = questions.map((item) => ({
        question_id: item.id,
        selected_option: answers[item.id],
      }))
      await submitAssessment(payload, getAccessToken())
      setIsComplete(true)
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        logout()
        navigate('/login', { replace: true })
        return
      }
      setError(requestError.message || 'Your answers could not be saved. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="assessment-page">
      <header className="assessment-header">
        <div className="assessment-header-inner">
          <Brand to="/dashboard" />
          <div className="assessment-header-actions">
            <span className="assessment-user-name">{user?.full_name}</span>
            <button type="button" className="assessment-logout" onClick={handleLogout}>Log out</button>
          </div>
        </div>
      </header>

      <main className="assessment-main">
        <div className="assessment-intro">
          <span className="assessment-eyebrow">YOUR 20-QUESTION CAREER ASSESSMENT</span>
          <h1>Career <em>Assessment</em></h1>
          <p>There are no right or wrong answers. Choose what feels most like you, and we’ll save your reflections for the next step.</p>
        </div>

        {isLoading && <div className="assessment-loading" role="status"><span className="loading-orbit" />Preparing your questions…</div>}

        {!isLoading && error && questions.length === 0 && (
          <section className="assessment-error-card" role="alert">
            <span className="assessment-result-icon">!</span>
            <h2>We couldn’t load your assessment</h2>
            <p>{error}</p>
            <button type="button" className="assessment-primary-button" onClick={() => window.location.reload()}>Try again</button>
          </section>
        )}

        {!isLoading && isComplete && (
          <section className="assessment-success-card" aria-live="polite">
            <span className="assessment-success-icon" aria-hidden="true">✓</span>
            <span className="assessment-eyebrow">A THOUGHTFUL FIRST STEP</span>
            <h2>Your reflections are saved.</h2>
            <p>You’ve completed your career check-in. Your answers are ready to inform the next part of your journey.</p>
            <Link to="/recommendations" className="assessment-primary-button">Continue to recommendations <span aria-hidden="true">→</span></Link>
            <Link to="/dashboard" className="assessment-back-link">Return to your career space</Link>
          </section>
        )}

        {!isLoading && !isComplete && question && (
          <section className="assessment-card" aria-labelledby="assessment-question-title">
            <div className="assessment-card-topline">
              <span>QUESTION <b>{String(step + 1).padStart(2, '0')}</b> <i>OF {String(questions.length).padStart(2, '0')}</i></span>
              <span className="assessment-category">{titleForCategory(question.category)}</span>
            </div>
            <div className="assessment-progress" role="progressbar" aria-label="Assessment progress" aria-valuemin="1" aria-valuemax={questions.length} aria-valuenow={step + 1}>
              <span style={{ width: `${((step + 1) / questions.length) * 100}%` }} />
            </div>

            <div className="assessment-question-content" key={question.id}>
              <h2 id="assessment-question-title">{question.question_text}</h2>
              <p className="assessment-select-hint">Choose the answer that feels closest to you.</p>
              <div className="assessment-options" role="radiogroup" aria-labelledby="assessment-question-title" aria-describedby={answerError ? 'assessment-answer-error' : undefined}>
                {question.options.map((option, index) => {
                  const selected = answers[question.id] === option.value
                  return (
                    <label key={option.value} className={`assessment-option${selected ? ' is-selected' : ''}`}>
                      <input
                        type="radio"
                        name={question.id}
                        value={option.value}
                        checked={selected}
                        onChange={() => chooseAnswer(option.value)}
                      />
                      <span className="assessment-option-letter" aria-hidden="true">{String.fromCharCode(65 + index)}</span>
                      <span className="assessment-option-label">{option.label}</span>
                      <span className="assessment-option-check" aria-hidden="true">✓</span>
                    </label>
                  )
                })}
              </div>
              {answerError && <p id="assessment-answer-error" className="assessment-answer-error" role="alert">{answerError}</p>}
              {error && <p className="assessment-submit-error" role="alert">{error}</p>}
            </div>

            <div className="assessment-controls">
              <button type="button" className="assessment-back-button" onClick={goBack} disabled={step === 0 || isSubmitting}>← <span>Back</span></button>
              <span className="assessment-saved-note"><span aria-hidden="true">✦</span> Your answers are saved when you submit</span>
              {step < questions.length - 1 ? (
                <button type="button" className="assessment-primary-button" onClick={goNext}>Next question <span aria-hidden="true">→</span></button>
              ) : (
                <button type="button" className="assessment-primary-button" onClick={handleSubmit} disabled={isSubmitting}>
                  {isSubmitting ? <><span className="assessment-spinner" /> Saving…</> : <>Save my assessment <span aria-hidden="true">→</span></>}
                </button>
              )}
            </div>
          </section>
        )}

        {!isLoading && !isComplete && question && (
          <div className="assessment-bottom-note"><span aria-hidden="true">◎</span> Your answers are private to your account and can be updated by retaking this assessment.</div>
        )}
      </main>
    </div>
  )
}
