import { beforeEach, describe, expect, test, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, useLocation } from 'react-router-dom'
import userEvent from '@testing-library/user-event'
import { AppRoutes } from './router'
import { ApiError, apiRequest } from '../lib/api'
import { OverviewPage } from '../features/dashboard/OverviewPage'
import { setSession } from '../features/auth/authSlice'
import { store } from './store'

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AppRoutes />
      <LocationProbe />
    </MemoryRouter>,
  )
}

function LocationProbe() {
  return <output data-testid="route-location">{useLocation().pathname}</output>
}

describe('application shell routing', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    store.dispatch({ type: 'auth/clearSession' })
  })

  test('redirects the root to the agent sign-in when no session exists', async () => {
    renderAt('/')
    expect(await screen.findByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
    expect(screen.getByText(/for agents/i)).toBeInTheDocument()
  })

  test('falls back to the agent sign-in for an unknown route', async () => {
    renderAt('/wherever')
    expect(await screen.findByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
    expect(screen.getByText(/for agents/i)).toBeInTheDocument()
  })

  test('shows role-specific navigation labels for an admin session', async () => {
    store.dispatch(setSession({ token: 'admin-token', account: { id: 1, email: 'admin@timesinternet.in', name: 'Admin', role: 'admin' } }))
    renderAt('/admin')
    expect(await screen.findByRole('navigation', { name: /workspace/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /overview/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /products/i })).toBeInTheDocument()
  })

  test('shows the agent navigation without admin-only team controls', async () => {
    store.dispatch(setSession({ token: 'agent-token', account: { id: 2, email: 'agent@timesinternet.in', name: 'Agent', role: 'agent' } }))
    renderAt('/agent')
    expect(await screen.findByRole('navigation', { name: /workspace/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /overview/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /products/i })).toBeInTheDocument()
  })

  test('opens and closes the responsive navigation menu', async () => {
    store.dispatch(setSession({ token: 'agent-token', account: { id: 2, email: 'agent@timesinternet.in', name: 'Agent', role: 'agent' } }))
    const user = userEvent.setup()
    renderAt('/agent')
    const toggle = await screen.findByRole('button', { name: /open navigation/i })
    await user.click(toggle)
    expect(screen.getByRole('navigation', { name: /workspace/i })).toBeVisible()
    await user.click(screen.getByRole('button', { name: /close navigation/i }))
    expect(screen.getByRole('navigation', { name: /workspace/i })).toHaveAttribute('data-menu-visible', 'false')
  })

  test('renders a minimal overview without fake metrics', () => {
    render(<OverviewPage role="agent" />)
    expect(screen.getByRole('heading', { name: /your agent workspace/i })).toBeInTheDocument()
    expect(screen.queryByText('+18%')).not.toBeInTheDocument()
  })

  test('redirects an authenticated user to login with a notice after a protected request returns 401', async () => {
    const user = userEvent.setup()
    store.dispatch(setSession({ token: 'expired-token', account: { id: 2, email: 'agent@timesinternet.in', name: 'Agent', role: 'agent' } }))
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'Invalid or expired access token' }), { status: 401 })))
    renderAt('/agent/evaluations')

    await user.click(await screen.findByRole('button', { name: /start avatar/i }))

    expect(await screen.findByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
    expect(screen.getByText(/your session expired/i)).toBeInTheDocument()
    expect(screen.getByTestId('route-location')).toHaveTextContent('/agent/login')
    expect(sessionStorage.getItem('train-me-auth-token-v1')).toBeNull()
  })
})

describe('apiRequest', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  test('serializes JSON and injects a bearer token', async () => {
    const fetchSpy = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({ ok: true }), { status: 200 })))
    vi.stubGlobal('fetch', fetchSpy)

    await apiRequest<{ ok: boolean }>('/api/check', {
      method: 'POST',
      body: { title: 'Hello' },
      token: 'secret-token',
    })

    const [, init] = fetchSpy.mock.calls[0]
    const headers = new Headers(init.headers)
    expect(headers.get('Accept')).toBe('application/json')
    expect(headers.get('Content-Type')).toBe('application/json')
    expect(headers.get('Authorization')).toBe('Bearer secret-token')
    expect(init.body).toBe(JSON.stringify({ title: 'Hello' }))
  })

  test('uses the configurable backend base URL while preserving absolute URLs', async () => {
    const fetchSpy = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({ ok: true }), { status: 200 })))
    vi.stubGlobal('fetch', fetchSpy)
    vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:8000')

    await apiRequest('/api/check')
    await apiRequest('https://example.test/api/check')

    expect(fetchSpy.mock.calls[0][0]).toBe('http://localhost:8000/api/check')
    expect(fetchSpy.mock.calls[1][0]).toBe('https://example.test/api/check')
  })

  test('attaches the stored session token only to the configured API origin', async () => {
    const fetchSpy = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({ ok: true }), { status: 200 })))
    vi.stubGlobal('fetch', fetchSpy)
    sessionStorage.setItem('train-me-auth-token-v1', 'session-secret')
    vi.stubEnv('VITE_API_BASE_URL', 'http://localhost:8000')

    await apiRequest('/api/check')
    await apiRequest('https://external.example/api/check')

    expect(new Headers(fetchSpy.mock.calls[0][1].headers).get('Authorization')).toBe('Bearer session-secret')
    expect(new Headers(fetchSpy.mock.calls[1][1].headers).get('Authorization')).toBeNull()
  })

  test('allows an explicit token for an external absolute URL', async () => {
    const fetchSpy = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ok: true }), { status: 200 }))
    vi.stubGlobal('fetch', fetchSpy)
    sessionStorage.setItem('train-me-auth-token-v1', 'session-secret')

    await apiRequest('https://external.example/api/check', { token: 'explicit-secret' })

    expect(new Headers(fetchSpy.mock.calls[0][1].headers).get('Authorization')).toBe('Bearer explicit-secret')
  })

  test('passes FormData through without forcing a content type', async () => {
    const fetchSpy = vi.fn().mockResolvedValue(new Response(JSON.stringify({ uploaded: true }), { status: 200 }))
    vi.stubGlobal('fetch', fetchSpy)
    const form = new FormData()
    form.append('file', 'contents')

    await apiRequest('/api/upload', { method: 'POST', body: form })

    const [, init] = fetchSpy.mock.calls[0]
    expect(init.body).toBe(form)
    const headers = new Headers(init.headers)
    expect(headers.get('Accept')).toBe('application/json')
    expect(headers.get('Content-Type')).toBeNull()
  })

  test('returns undefined for a successful 204 response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(null, { status: 204 })))
    await expect(apiRequest('/api/empty')).resolves.toBeUndefined()
  })

  test('normalizes API errors into an ApiError with status and message', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Title is required', code: 'validation_error' }), {
        status: 422,
        headers: { 'Content-Type': 'application/json' },
      }),
    ))

    const request = apiRequest('/api/playbooks', { method: 'POST', body: {} })
    await expect(request).rejects.toBeInstanceOf(ApiError)
    await expect(request).rejects.toMatchObject({
      status: 422,
      message: 'Title is required',
      code: 'validation_error',
    })
  })

  test('emits an auth-expired event only for 401 responses carrying a bearer token', async () => {
    const handler = vi.fn()
    window.addEventListener('train-me-auth-expired', handler)
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({ detail: 'Expired' }), { status: 401 }))))
    await expect(apiRequest('/api/protected', { token: 'expired-token' })).rejects.toMatchObject({ status: 401 })
    sessionStorage.clear()
    await expect(apiRequest('/api/login', { method: 'POST', body: {} })).rejects.toMatchObject({ status: 401 })
    expect(handler).toHaveBeenCalledTimes(1)
    window.removeEventListener('train-me-auth-expired', handler)
  })

  test('turns validation detail arrays into actionable messages without leaking locations', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: [
        { loc: ['body', 'email'], msg: 'value is not a valid email', type: 'value_error' },
        { loc: ['body', 'password'], msg: 'field required', type: 'missing' },
      ] }), { status: 422 }),
    ))

    await expect(apiRequest('/api/v1/auth/agents/signup', { method: 'POST', body: {} })).rejects.toMatchObject({
      status: 422,
      message: 'value is not a valid email; field required',
    })
  })
})
