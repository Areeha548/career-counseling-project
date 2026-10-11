const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '')
const USE_DEV_PROXY = import.meta.env.DEV

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function messageFromResponse(data, status) {
  if (status === 401) return 'Those sign-in details did not match. Check them and try again.'
  if (status === 409) return 'An account with this email already exists. Try signing in instead.'
  if (status === 422 && Array.isArray(data?.detail)) {
    return data.detail.map((issue) => issue.msg).join(' ')
  }
  if (typeof data?.detail === 'string') return data.detail
  return 'Something went wrong. Please try again in a moment.'
}

export async function apiRequest(path, { method = 'GET', body, token } = {}) {
  if (!USE_DEV_PROXY && !API_BASE_URL) {
    throw new ApiError('The API URL is not configured. Set VITE_API_BASE_URL in the frontend environment.')
  }

  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  let response
  try {
    const requestUrl = `${USE_DEV_PROXY ? '' : API_BASE_URL}${path}`
    response = await fetch(requestUrl, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError('We could not reach the server. Please check your connection and try again.')
  }

  const data = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(messageFromResponse(data, response.status), response.status)
  return data
}

export function registerAccount(details) {
  return apiRequest('/api/auth/register', { method: 'POST', body: details })
}

export function loginAccount(credentials) {
  return apiRequest('/api/auth/login', { method: 'POST', body: credentials })
}

export function getMyProfile(token) {
  return apiRequest('/api/auth/me', { token })
}

export function getAssessmentQuestions(token) {
  return apiRequest('/api/assessment/questions', { token })
}

export function getMyAssessmentResults(token) {
  return apiRequest('/api/assessment/my-results', { token })
}

export function submitAssessment(answers, token) {
  return apiRequest('/api/assessment/submit', {
    method: 'POST',
    body: { answers },
    token,
  })
}

export function getRecommendations(token) {
  return apiRequest('/api/recommendations', { token })
}

export function getSkillCatalog() {
  return apiRequest('/api/skills')
}

export function getMySkillProfile(token) {
  return apiRequest('/api/skills/me', { token })
}

export function saveMySkillProfile(skills, token) {
  return apiRequest('/api/skills/me', { method: 'PUT', body: { skills }, token })
}

export function getCareerSkillGap(careerId, token) {
  return apiRequest(`/api/careers/${careerId}/skill-gap`, { token })
}

export function getCareerCatalog() {
  return apiRequest('/api/careers')
}

export function getRoadmapTemplates() {
  return apiRequest('/api/roadmaps/templates')
}

export function getMyRoadmaps(token) {
  return apiRequest('/api/roadmaps/me', { token })
}

export function createOrResumeRoadmap(careerId, token) {
  return apiRequest('/api/roadmaps', {
    method: 'POST',
    body: { career_id: Number(careerId) },
    token,
  })
}

export function getRoadmap(roadmapId, token) {
  return apiRequest(`/api/roadmaps/${roadmapId}`, { token })
}

export function updateRoadmapStep(roadmapId, stepId, status, token) {
  return apiRequest(`/api/roadmaps/${roadmapId}/steps/${stepId}`, {
    method: 'PATCH',
    body: { status },
    token,
  })
}
