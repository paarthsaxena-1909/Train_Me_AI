import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { OverviewPage } from '../features/dashboard/OverviewPage'
import { AuthPage } from '../features/auth/AuthPage'
import { ProtectedRoute } from '../features/auth/ProtectedRoute'
import { PageState } from '../components/PageState'
import type { Role } from '../lib/types'
import { readAuthToken } from '../features/auth/authApi'
import { Provider } from 'react-redux'
import { store } from './store'
import { useDispatch, useSelector } from 'react-redux'
import { clearSession } from '../features/auth/authSlice'
import type { RootState, AppDispatch } from './store'
import { authExpiredEvent } from '../lib/api'
import { ProductsPage } from '../features/products/ProductsPage'
import { QAPage } from '../features/qa/QAPage'
import { AssignmentsPage } from '../features/assignments/AssignmentsPage'
import { EvaluationsPage } from '../features/evaluations/EvaluationsPage'

function homeDestination() { return readAuthToken() ? 'agent' : 'agent/login' }

function Placeholder({ title }: { title: string }) {
  return <div className="mx-auto max-w-[1200px] px-6 py-8 lg:px-10 lg:py-10"><PageState title={`${title} is taking shape`} description="This workspace area will be connected to your team’s data in the next release." /></div>
}

function Workspace({ role }: { role: Role }) {
  const { pathname } = useLocation()
  const section = pathname.split('/')[2]
  const page = section === 'products' ? <ProductsPage canCreate={role === 'admin'} /> : section === 'qa' && role === 'agent' ? <QAPage /> : section === 'assignments' && role === 'agent' ? <AssignmentsPage /> : section === 'evaluations' && role === 'agent' ? <EvaluationsPage /> : section ? <Placeholder title={section[0].toUpperCase() + section.slice(1)} /> : <OverviewPage role={role} />
  return <ProtectedRoute role={role}>{page}</ProtectedRoute>
}

function AuthExpiryRedirect() {
  const navigate = useNavigate()
  const location = useLocation()
  const dispatch = useDispatch<AppDispatch>()
  const accountRole = useSelector((state: RootState) => state.auth.account?.role)

  useEffect(() => {
    const handleExpired = (event: Event) => {
      const message = (event as CustomEvent<{ message?: string }>).detail?.message ?? 'Your session expired. Please sign in again.'
      const role = accountRole ?? (location.pathname.startsWith('/admin') ? 'admin' : 'agent')
      dispatch(clearSession())
      window.setTimeout(() => navigate(`/${role}/login`, { replace: true, state: { authNotice: message } }), 0)
    }
    window.addEventListener(authExpiredEvent, handleExpired)
    return () => window.removeEventListener(authExpiredEvent, handleExpired)
  }, [accountRole, dispatch, location.pathname, navigate])

  return null
}

function RoutesContent() {
  const { pathname } = useLocation()
  if (pathname === '/') return <Navigate replace to={`/${homeDestination()}`} />
  if (pathname === '/admin/login' || pathname === '/admin/signup') return <AuthPage mode={pathname.endsWith('signup') ? 'signup' : 'login'} role="admin" />
  if (pathname === '/agent/login' || pathname === '/agent/signup') return <AuthPage mode={pathname.endsWith('signup') ? 'signup' : 'login'} role="agent" />
  if (pathname === '/admin' || pathname.startsWith('/admin/')) return <Workspace role="admin" />
  if (pathname === '/agent' || pathname.startsWith('/agent/')) return <Workspace role="agent" />
  return <Navigate replace to={`/${homeDestination()}`} />
}

export function AppRoutes() {
  return <Provider store={store}><AuthExpiryRedirect /><RoutesContent /></Provider>
}

export function AppRouter() { return <AppRoutes /> }
