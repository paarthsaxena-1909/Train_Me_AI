import { Navigate, useLocation } from 'react-router-dom'
import { OverviewPage } from '../features/dashboard/OverviewPage'
import { AuthPage } from '../features/auth/AuthPage'
import { ProtectedRoute } from '../features/auth/ProtectedRoute'
import { PageState } from '../components/PageState'
import type { Role } from '../lib/types'
import { readAuthToken } from '../features/auth/authApi'
import { Provider } from 'react-redux'
import { store } from './store'

function homeDestination() { return readAuthToken() ? 'agent' : 'agent/login' }

function Placeholder({ title }: { title: string }) {
  return <div className="mx-auto max-w-[1200px] px-6 py-8 lg:px-10 lg:py-10"><PageState title={`${title} is taking shape`} description="This workspace area will be connected to your team’s data in the next release." /></div>
}

function Workspace({ role }: { role: Role }) {
  const { pathname } = useLocation()
  const section = pathname.split('/')[2]
  const page = section ? <Placeholder title={section === 'playbooks' ? (role === 'agent' ? 'My playbooks' : 'Playbooks') : section[0].toUpperCase() + section.slice(1)} /> : <OverviewPage role={role} />
  return <ProtectedRoute role={role}>{page}</ProtectedRoute>
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
  return <Provider store={store}><RoutesContent /></Provider>
}

export function AppRouter() { return <AppRoutes /> }
