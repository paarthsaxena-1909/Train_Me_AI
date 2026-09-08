import { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { PageState } from '../../components/PageState'
import { AppShell } from '../../layouts/AppShell'
import type { AppDispatch, RootState } from '../../app/store'
import { hydrateToken, restoreSession } from './authSlice'
import { readAuthToken } from './authApi'
import type { Role } from '../../lib/types'

type ProtectedRouteProps = { role: Role; children: React.ReactNode }

export function ProtectedRoute({ role, children }: ProtectedRouteProps) {
  const dispatch = useDispatch<AppDispatch>()
  const location = useLocation()
  const { token, account, status, bootstrapped } = useSelector((state: RootState) => state.auth)
  const storedToken = readAuthToken()

  useEffect(() => {
    if (!token && storedToken) {
      dispatch(hydrateToken(storedToken))
    } else if (token && !account && !bootstrapped) {
      void dispatch(restoreSession())
    }
  }, [account, bootstrapped, dispatch, storedToken, token])

  if (storedToken && (!token || !bootstrapped)) return <PageState title="Restoring your session" description="Checking your workspace access…" />
  if (!token || status === 'error' || !account) return <Navigate replace to={`/${role}/login`} state={{ from: location.pathname }} />
  if (account.role !== role) return <Navigate replace to={`/${account.role}`} state={{ from: location.pathname }} />
  return <AppShell role={role}>{children}</AppShell>
}
