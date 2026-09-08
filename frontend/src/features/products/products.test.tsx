import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, test, vi } from 'vitest'
import { ProductsPage } from './ProductsPage'

const apiRequest = vi.fn()
vi.mock('../../lib/api', async (original) => {
  const actual = await original<typeof import('../../lib/api')>()
  return { ...actual, apiRequest: (...args: unknown[]) => apiRequest(...args) }
})

describe('ProductsPage', () => {
  beforeEach(() => apiRequest.mockReset())

  test('shows an empty catalogue and admin creation form', async () => {
    apiRequest.mockResolvedValueOnce([])
    render(<ProductsPage canCreate />)
    expect(await screen.findByText('No products yet')).toBeInTheDocument()
    expect(screen.getByRole('form', { name: 'Create product' })).toBeInTheDocument()
  })

  test('keeps creation controls hidden from agents', async () => {
    apiRequest.mockResolvedValueOnce([{ id: 1, name: 'Phone', description: null, variants: [] }])
    render(<ProductsPage canCreate={false} />)
    expect(await screen.findByText('Phone')).toBeInTheDocument()
    expect(screen.queryByRole('form', { name: 'Create product' })).not.toBeInTheDocument()
  })

  test('creates a product and reloads', async () => {
    apiRequest.mockResolvedValueOnce([]).mockResolvedValueOnce({ id: 1 }).mockResolvedValueOnce([])
    render(<ProductsPage canCreate />)
    await screen.findByText('No products yet')
    await userEvent.type(screen.getByLabelText('Product name'), 'Phone')
    await userEvent.type(screen.getByLabelText('First variant name'), 'Base')
    await userEvent.type(screen.getByLabelText('First variant specs'), '128 GB')
    await userEvent.click(screen.getByRole('button', { name: 'Add product' }))
    await waitFor(() => expect(apiRequest).toHaveBeenCalledWith('/api/v1/products', expect.objectContaining({ method: 'POST' })))
  })

  test('creates a variant for its product', async () => {
    const product = { id: 7, name: 'Phone', description: null, variants: [] }
    apiRequest.mockResolvedValueOnce([product]).mockResolvedValueOnce({ id: 2 }).mockResolvedValueOnce([product])
    render(<ProductsPage canCreate />)
    await userEvent.type(await screen.findByLabelText('Variant name for Phone'), 'Pro')
    await userEvent.type(screen.getByLabelText('Variant specs for Phone'), '256 GB')
    await userEvent.click(screen.getByRole('button', { name: 'Add variant' }))
    await waitFor(() => expect(apiRequest).toHaveBeenCalledWith('/api/v1/products/7/variants', expect.objectContaining({ method: 'POST' })))
  })
})
