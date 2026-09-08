import { apiRequest } from '../../lib/api'
import type { Role } from '../../lib/types'

export type Account = {
  id: number
  role: Role
  email: string
  name: string
  region?: string | null
  pincode?: string | null
}

export type LoginCredentials = { email: string; password: string }
export type AgentSignupValues = LoginCredentials & { name: string; region: string; pincode: string }
export type AdminSignupValues = LoginCredentials & { name: string }
export type TokenResponse = { access_token: string; token_type: 'bearer'; account: Account }

export const authTokenKey = 'train-me-auth-token-v1'

function rolePath(role: Role) {
  return role === 'agent' ? 'agents' : 'admins'
}

export function login(role: Role, credentials: LoginCredentials) {
  return apiRequest<TokenResponse>(`/api/v1/auth/${rolePath(role)}/login`, {
    method: 'POST',
    body: credentials,
  })
}

export function signup(role: Role, values: AgentSignupValues | AdminSignupValues) {
  return apiRequest<Account>(`/api/v1/auth/${rolePath(role)}/signup`, {
    method: 'POST',
    body: values,
  })
}

export function getCurrentAccount(token: string) {
  return apiRequest<Account>('/api/v1/auth/me', { method: 'GET', token })
}

export function readAuthToken() {
  if (typeof window === 'undefined') return null
  return window.sessionStorage.getItem(authTokenKey)
}

export function writeAuthToken(token: string) {
  if (typeof window !== 'undefined') window.sessionStorage.setItem(authTokenKey, token)
}

export function clearAuthToken() {
  if (typeof window !== 'undefined') window.sessionStorage.removeItem(authTokenKey)
}
