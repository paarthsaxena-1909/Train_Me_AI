import { beforeEach, describe, expect, test, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EvaluationsPage } from './EvaluationsPage'

const apiRequest = vi.fn()
const start = vi.fn()
const stop = vi.fn()
const repeat = vi.fn()

vi.mock('../../lib/api', async (original) => ({ ...(await original<typeof import('../../lib/api')>()), apiRequest: (...args: unknown[]) => apiRequest(...args) }))
vi.mock('@heygen/liveavatar-web-sdk', () => ({
  SessionEvent: { SESSION_STREAM_READY: 'session.stream_ready', SESSION_DISCONNECTED: 'session.disconnected' },
  LiveAvatarSession: class {
    start = start
    stop = stop
    repeat = repeat
    on = vi.fn()
    attach = vi.fn()
  },
}))

describe('EvaluationsPage', () => {
  beforeEach(() => {
    apiRequest.mockReset()
    start.mockReset()
    stop.mockReset()
    repeat.mockReset()
    start.mockResolvedValue(undefined)
    stop.mockResolvedValue(undefined)
  })

  test('starts an avatar session and sends a transcript to the mocked response pipeline', async () => {
    apiRequest
      .mockResolvedValueOnce({ session_token: 'temporary-token', session_id: 'session-1', api_url: 'https://api.liveavatar.com' })
      .mockResolvedValueOnce({ response_text: 'A mocked avatar response.' })
    const user = userEvent.setup()

    render(<EvaluationsPage />)
    await user.click(screen.getByRole('button', { name: /start avatar/i }))
    await user.type(screen.getByRole('textbox', { name: /message/i }), 'Hello avatar')
    await user.click(screen.getByRole('button', { name: /^speak$/i }))

    await waitFor(() => expect(apiRequest).toHaveBeenCalledWith('/api/v1/evaluations/avatar-session', { method: 'POST' }))
    await waitFor(() => expect(apiRequest).toHaveBeenCalledWith('/api/v1/evaluations/message', { method: 'POST', body: { message: 'Hello avatar' } }))
    expect(await screen.findByText('A mocked avatar response.')).toBeInTheDocument()
    expect(repeat).toHaveBeenCalledWith('A mocked avatar response.')
  })

  test('ends the locally owned avatar session', async () => {
    apiRequest.mockResolvedValueOnce({ session_token: 'temporary-token', session_id: 'session-1', api_url: 'https://api.liveavatar.com' })
    const user = userEvent.setup()

    render(<EvaluationsPage />)
    await user.click(screen.getByRole('button', { name: /start avatar/i }))
    await user.click(await screen.findByRole('button', { name: /end session/i }))

    expect(stop).toHaveBeenCalledOnce()
  })
})
