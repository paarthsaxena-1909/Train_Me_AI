import { beforeEach, describe, expect, test, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QAPage } from './QAPage'

describe('QA page', () => {
  beforeEach(() => vi.restoreAllMocks())

  test('asks one product question and renders the returned answer', async () => {
    const fetchSpy = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([{ id: 4, name: 'Phone', description: null, variants: [] }]), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: 8, product_id: 4, query: 'How fast?', response: 'Mock answer' }), { status: 201 }))
    vi.stubGlobal('fetch', fetchSpy)
    const user = userEvent.setup()

    render(<MemoryRouter><QAPage /></MemoryRouter>)
    await user.selectOptions(await screen.findByLabelText('Product'), '4')
    await user.type(screen.getByLabelText('Question'), 'How fast?')
    await user.click(screen.getByRole('button', { name: /ask question/i }))

    expect(await screen.findByText('Mock answer')).toBeInTheDocument()
    expect(screen.queryByText(/conversation history/i)).not.toBeInTheDocument()
    expect(fetchSpy.mock.calls[1][0]).toContain('/api/v1/queries')
  })
})
