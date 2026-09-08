import { FormEvent, useEffect, useState } from 'react'
import { PageState } from '../../components/PageState'
import { ApiError, apiRequest } from '../../lib/api'

type Product = { id: number; name: string; variants: { id: number; name: string }[] }
type Answer = { response: string }

export function QAPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [productId, setProductId] = useState('')
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState<string>()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string>()

  useEffect(() => {
    apiRequest<Product[]>('/api/v1/products')
      .then((items) => { setProducts(items); if (items[0]) setProductId(String(items[0].id)) })
      .catch((caught) => setError(caught instanceof ApiError ? caught.message : 'Products could not be loaded.'))
      .finally(() => setLoading(false))
  }, [])

  async function askQuestion(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setAnswer(undefined)
    setError(undefined)
    try {
      const result = await apiRequest<Answer>('/api/v1/queries', {
        method: 'POST',
        body: { product_id: Number(productId), query },
      })
      setAnswer(result.response)
      setQuery('')
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Your question could not be answered.')
    } finally {
      setSubmitting(false)
    }
  }

  return <div className="mx-auto max-w-[1000px] px-6 py-8 lg:px-10">
    <p className="text-sm font-medium text-primary">Product coach</p>
    <h2 className="mt-2 text-3xl font-semibold tracking-[-0.05em]">Ask a product question</h2>
    <p className="mt-2 max-w-xl text-sm leading-6 text-muted-text">Choose a product and ask one question. You’ll get a concise answer for this interaction.</p>
    {loading && <div className="mt-6"><PageState title="Loading products" description="Preparing the product context." /></div>}
    {!loading && error && !products.length && <div className="mt-6"><PageState title="Could not load products" description={error} /></div>}
    {!loading && products.length === 0 && !error && <div className="mt-6"><PageState title="No products available" description="Ask an administrator to add a product first." /></div>}
    {!loading && products.length > 0 && <form aria-label="Ask product question" className="mt-6 grid gap-4 rounded-2xl border border-border bg-surface p-5" onSubmit={askQuestion}>
      <label className="grid gap-1 text-sm font-medium">Product<select aria-label="Product" className="rounded-xl border border-border bg-surface p-3 font-normal" required value={productId} onChange={(event) => setProductId(event.target.value)}>{products.map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}</select></label>
      <label className="grid gap-1 text-sm font-medium">Your question<textarea aria-label="Question" className="min-h-28 rounded-xl border border-border p-3 font-normal" maxLength={4000} placeholder="What should I know about this product?" required value={query} onChange={(event) => setQuery(event.target.value)} /></label>
      <button className="w-fit rounded-xl bg-primary px-5 py-3 font-semibold text-white disabled:opacity-60" disabled={submitting} type="submit">{submitting ? 'Thinking…' : 'Ask question'}</button>
    </form>}
    {error && products.length > 0 && <p className="mt-4 text-sm text-red-700" role="alert">{error}</p>}
    {answer && <section aria-label="Answer" className="mt-6 rounded-2xl border border-light-purple bg-light-purple/40 p-5"><p className="text-xs font-semibold uppercase tracking-[0.08em] text-primary">Answer</p><p className="mt-2 leading-7">{answer}</p><p className="mt-4 text-xs text-muted-text">AI responses are mocked for now and will be replaced by the analysis layer.</p></section>}
  </div>
}
