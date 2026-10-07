import { Navigate, useLocation } from 'react-router'
import { useAuth } from '../context/AuthContext'

export function ProtectedRoute({ children }) {
  const { user, isCheckingSession } = useAuth()
  const location = useLocation()

  if (isCheckingSession) {
    return <main className="route-loading" aria-live="polite"><span className="loading-orbit" />Checking your session…</main>
  }
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return children
}
