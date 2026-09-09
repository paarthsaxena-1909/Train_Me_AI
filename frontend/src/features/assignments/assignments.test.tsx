import { describe, expect, test, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AssignmentsPage } from './AssignmentsPage'

const apiRequest = vi.fn()
vi.mock('../../lib/api', async (original) => ({ ...(await original<typeof import('../../lib/api')>()), apiRequest: (...args: unknown[]) => apiRequest(...args) }))

describe('AssignmentsPage', () => {
  beforeEach(() => apiRequest.mockReset())
  test('creates an assignment for the selected lineup and submits all answers once', async () => {
    const assignment = { id: 4, product_lineup_id: 2, lineup_identifier: 'Phone', status: null, questions: [{ id: 11, question_number: 1, question: 'Explain value', answer: null, evaluation: null }] }
    apiRequest.mockResolvedValueOnce([{ id: 2, lineup_identifier: 'Phone', product_count: 1 }]).mockResolvedValueOnce([]).mockResolvedValueOnce(assignment).mockResolvedValueOnce(assignment).mockResolvedValueOnce({ ...assignment, status: 'completed', questions: [{ ...assignment.questions[0], answer: 'It helps customers.', evaluation: 'Mock feedback' }] }).mockResolvedValueOnce([{ ...assignment, status: 'completed' }])
    const user = userEvent.setup()
    render(<AssignmentsPage />)
    await screen.findByRole('button', { name: /create assignment/i })
    await user.click(screen.getByRole('button', { name: /create assignment/i }))
    await user.click(await screen.findByRole('button', { name: /start assignment/i }))
    await user.type(await screen.findByLabelText('Answer 1'), 'It helps customers.')
    await user.click(screen.getByRole('button', { name: /submit assignment/i }))
    await waitFor(() => expect(apiRequest).toHaveBeenCalledWith('/api/v1/assignments/4/submit', expect.objectContaining({ method: 'POST', body: { answers: [{ question_id: 11, answer: 'It helps customers.' }] } })))
    expect(await screen.findByText('Question evaluation')).toBeInTheDocument()
    expect(screen.queryByText(/deadline|draft|save/i)).not.toBeInTheDocument()
  })
})
