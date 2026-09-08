import { beforeEach, describe, expect, test, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { Provider } from 'react-redux'
import { AppRoutes } from '../../app/router'
import { store } from '../../app/store'

const account = {
  id: 7,
  role: 'agent' as const,
  email: 'asha@example.com',
  name: 'Asha',
  region: 'West',
  pincode: '012345',
}
const adminAccount = { id: 8, role: 'admin' as const, email: 'mira@example.com', name: 'Mira', region: null, pincode: null }

function renderAt(path: string) {
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
        <LocationProbe />
      </MemoryRouter>
    </Provider>,
  )
}

function LocationProbe() {
  return <output data-testid="route-location">{useLocation().pathname}</output>
}

describe('role-aware authentication', () => {
  beforeEach(() => {
    sessionStorage.clear()
    localStorage.clear()
    store.dispatch({ type: 'auth/clearSession' })
    vi.restoreAllMocks()
  })

  test('shows an agent pincode only on agent signup and rejects non-six-digit values', async () => {
    const user = userEvent.setup()
    renderAt('/agent/signup')

    expect(screen.getByRole('heading', { name: /create your account/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/six-digit pincode/i)).toBeInTheDocument()
    await user.type(screen.getByLabelText(/full name/i), 'Asha')
    await user.type(screen.getByLabelText(/work email/i), 'asha@example.com')
    await user.type(screen.getByLabelText(/password/i), 'secret')
    await user.type(screen.getByLabelText(/six-digit pincode/i), '12345')
    await user.click(screen.getByRole('button', { name: /create account/i }))
    expect(await screen.findByText(/pincode must be exactly six digits/i)).toBeInTheDocument()

    cleanup()
    renderAt('/admin/signup')
    expect(screen.queryByLabelText(/six-digit pincode/i)).not.toBeInTheDocument()
  })

  test('submits agent login, persists a versioned session token, and redirects by returned role', async () => {
    const user = userEvent.setup()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({
      access_token: 'jwt-agent',
      token_type: 'bearer',
      account,
    }), { status: 200 })))
    renderAt('/agent/login')
    await user.type(screen.getByLabelText(/work email/i), account.email)
    await user.type(screen.getByLabelText(/password/i), 'secret')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    await waitFor(() => expect(screen.getByRole('heading', { name: /your agent workspace/i })).toBeInTheDocument())
    expect(sessionStorage.getItem('train-me-auth-token-v1')).toBe('jwt-agent')
    expect(localStorage.getItem('train-me-token')).toBeNull()
    expect(screen.getByText(/asha/i)).toBeInTheDocument()
  })

  test('submits agent signup with pincode and admin signup without pincode', async () => {
    const user = userEvent.setup()
    const fetchSpy = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(account), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(adminAccount), { status: 201 }))
    vi.stubGlobal('fetch', fetchSpy)

    renderAt('/agent/signup')
    await user.type(screen.getByLabelText(/full name/i), 'Asha')
    await user.type(screen.getByLabelText(/work email/i), account.email)
    await user.type(screen.getByLabelText(/password/i), 'secret')
    await user.type(screen.getByLabelText(/six-digit pincode/i), account.pincode)
    await user.click(screen.getByRole('button', { name: /create account/i }))
    await waitFor(() => expect(fetchSpy).toHaveBeenCalledTimes(1))
    expect(fetchSpy.mock.calls[0][0]).toContain('/api/v1/auth/agents/signup')
    expect(JSON.parse(fetchSpy.mock.calls[0][1].body as string)).toMatchObject({ pincode: '012345' })

    cleanup()
    renderAt('/admin/signup')
    await user.type(screen.getByLabelText(/full name/i), 'Mira')
    await user.type(screen.getByLabelText(/work email/i), adminAccount.email)
    await user.type(screen.getByLabelText(/password/i), 'secret')
    await user.click(screen.getByRole('button', { name: /create account/i }))
    await waitFor(() => expect(fetchSpy).toHaveBeenCalledTimes(2))
    expect(fetchSpy.mock.calls[1][0]).toContain('/api/v1/auth/admins/signup')
    expect(JSON.parse(fetchSpy.mock.calls[1][1].body as string)).not.toHaveProperty('pincode')
  })

  test('submits admin login to the admin endpoint', async () => {
    const user = userEvent.setup()
    const fetchSpy = vi.fn().mockResolvedValue(new Response(JSON.stringify({ access_token: 'jwt-admin', token_type: 'bearer', account: adminAccount }), { status: 200 }))
    vi.stubGlobal('fetch', fetchSpy)
    renderAt('/admin/login')
    await user.type(screen.getByLabelText(/work email/i), adminAccount.email)
    await user.type(screen.getByLabelText(/password/i), 'secret')
    await user.click(screen.getByRole('button', { name: /sign in/i }))
    await waitFor(() => expect(screen.getByRole('heading', { name: /your admin workspace/i })).toBeInTheDocument())
    expect(fetchSpy.mock.calls[0][0]).toContain('/api/v1/auth/admins/login')
    expect(sessionStorage.getItem('train-me-auth-token-v1')).toBe('jwt-admin')
  })

  test('shows pending and normalized API errors during admin login', async () => {
    const user = userEvent.setup()
    let resolveRequest!: (value: Response) => void
    vi.stubGlobal('fetch', vi.fn().mockReturnValue(new Promise<Response>((resolve) => { resolveRequest = resolve })))
    renderAt('/admin/login')
    await user.type(screen.getByLabelText(/work email/i), 'admin@example.com')
    await user.type(screen.getByLabelText(/password/i), 'bad')
    await user.click(screen.getByRole('button', { name: /sign in/i }))
    expect(screen.getByRole('button', { name: /signing in/i })).toBeDisabled()
    resolveRequest(new Response(JSON.stringify({ detail: 'Incorrect email or password' }), { status: 401 }))
    expect(await screen.findByRole('alert')).toHaveTextContent(/incorrect email or password/i)
  })

  test('uses native required and email validation before submitting', async () => {
    const user = userEvent.setup()
    const fetchSpy = vi.fn()
    vi.stubGlobal('fetch', fetchSpy)
    renderAt('/admin/login')
    await user.type(screen.getByLabelText(/work email/i), 'not-an-email')
    await user.click(screen.getByRole('button', { name: /sign in/i }))
    expect(fetchSpy).not.toHaveBeenCalled()
    expect(screen.getByLabelText(/work email/i)).toBeInvalid()
  })

  test('restores an existing session through auth/me and clears it after a 401', async () => {
    sessionStorage.setItem('train-me-auth-token-v1', 'stale-token')
    const fetchSpy = vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'Invalid or expired access token' }), { status: 401 }))
    vi.stubGlobal('fetch', fetchSpy)
    renderAt('/agent')
    expect(await screen.findByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
    expect(sessionStorage.getItem('train-me-auth-token-v1')).toBeNull()
    expect(fetchSpy).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/me', expect.objectContaining({ method: 'GET' }))
    expect(new Headers(fetchSpy.mock.calls[0][1].headers).get('Authorization')).toBe('Bearer stale-token')
  })

  test('restores a valid session and logout clears the token', async () => {
    const user = userEvent.setup()
    sessionStorage.setItem('train-me-auth-token-v1', 'valid-token')
    const fetchSpy = vi.fn().mockResolvedValue(new Response(JSON.stringify(account), { status: 200 }))
    vi.stubGlobal('fetch', fetchSpy)
    renderAt('/agent')
    expect(await screen.findByRole('heading', { name: /your agent workspace/i })).toBeInTheDocument()
    expect(screen.getByText(/asha/i)).toBeInTheDocument()
    expect(fetchSpy).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/me', expect.objectContaining({ method: 'GET' }))
    expect(new Headers(fetchSpy.mock.calls[0][1].headers).get('Authorization')).toBe('Bearer valid-token')
    await user.click(screen.getAllByRole('button', { name: /log out/i })[0])
    expect(await screen.findByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
    expect(sessionStorage.getItem('train-me-auth-token-v1')).toBeNull()
  })

  test('redirects a signed-in user away from the other role workspace', async () => {
    sessionStorage.setItem('train-me-auth-token-v1', 'agent-token')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(account), { status: 200 })))
    renderAt('/admin')
    expect(await screen.findByRole('heading', { name: /your agent workspace/i })).toBeInTheDocument()
    expect(screen.getByTestId('route-location')).toHaveTextContent('/agent')
    expect(screen.queryByRole('link', { name: /team/i })).not.toBeInTheDocument()
  })

  test('redirects an admin session away from the agent workspace', async () => {
    sessionStorage.setItem('train-me-auth-token-v1', 'admin-token')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(adminAccount), { status: 200 })))
    renderAt('/agent')
    expect(await screen.findByRole('heading', { name: /your admin workspace/i })).toBeInTheDocument()
    expect(screen.getByTestId('route-location')).toHaveTextContent('/admin')
    expect(screen.queryByRole('link', { name: /my playbooks/i })).not.toBeInTheDocument()
  })

  test('restores an admin session through auth/me', async () => {
    sessionStorage.setItem('train-me-auth-token-v1', 'admin-token')
    const fetchSpy = vi.fn().mockResolvedValue(new Response(JSON.stringify(adminAccount), { status: 200 }))
    vi.stubGlobal('fetch', fetchSpy)
    renderAt('/admin')
    expect(await screen.findByRole('heading', { name: /your admin workspace/i })).toBeInTheDocument()
    expect(fetchSpy).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/me', expect.objectContaining({ method: 'GET' }))
    expect(new Headers(fetchSpy.mock.calls[0][1].headers).get('Authorization')).toBe('Bearer admin-token')
  })
})
