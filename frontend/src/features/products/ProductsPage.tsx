import { FormEvent, useEffect, useState } from 'react'
import { PageState } from '../../components/PageState'
import { ApiError, apiRequest } from '../../lib/api'

type Variant = { id: number; name: string; specs: string }
type Product = { id: number; name: string; description?: string | null; variants: Variant[] }
type VariantDraft = { name: string; specs: string }

export function ProductsPage({ canCreate }: { canCreate: boolean }) {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>()
  const [mutationError, setMutationError] = useState<string>()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [initialVariant, setInitialVariant] = useState<VariantDraft>({ name: '', specs: '' })
  const [variantDrafts, setVariantDrafts] = useState<Record<number, VariantDraft>>({})

  async function load() {
    setLoading(true)
    setError(undefined)
    try {
      setProducts(await apiRequest<Product[]>('/api/v1/products'))
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Products could not be loaded.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [])

  async function createProduct(event: FormEvent) {
    event.preventDefault()
    setMutationError(undefined)
    try {
      await apiRequest('/api/v1/products', { method: 'POST', body: { name, description: description || null, variant: initialVariant } })
      setName('')
      setDescription('')
      setInitialVariant({ name: '', specs: '' })
      await load()
    } catch (caught) {
      setMutationError(caught instanceof ApiError ? caught.message : 'Product could not be created.')
    }
  }

  async function createVariant(event: FormEvent, productId: number) {
    event.preventDefault()
    setMutationError(undefined)
    try {
      await apiRequest(`/api/v1/products/${productId}/variants`, { method: 'POST', body: variantDrafts[productId] })
      setVariantDrafts((current) => ({ ...current, [productId]: { name: '', specs: '' } }))
      await load()
    } catch (caught) {
      setMutationError(caught instanceof ApiError ? caught.message : 'Variant could not be created.')
    }
  }

  function updateVariant(productId: number, field: keyof VariantDraft, value: string) {
    setVariantDrafts((current) => {
      const draft = current[productId] ?? { name: '', specs: '' }
      return { ...current, [productId]: { ...draft, [field]: value } }
    })
  }

  return <div className="mx-auto max-w-[1000px] px-6 py-8 lg:px-10">
    <h2 className="text-3xl font-semibold">Products</h2>
    <p className="mt-2 text-sm text-muted-text">A simple catalogue for the team to learn from.</p>
    {canCreate && <form aria-label="Create product" className="mt-6 grid gap-3 rounded-2xl border border-border bg-surface p-5" onSubmit={createProduct}>
      <h3 className="font-semibold">Add a product</h3>
      <label className="grid gap-1 text-sm font-medium">Product name<input className="rounded-xl border border-border p-3 font-normal" required value={name} onChange={(event) => setName(event.target.value)} /></label>
      <label className="grid gap-1 text-sm font-medium">Description <span className="font-normal text-muted-text">(optional)</span><input className="rounded-xl border border-border p-3 font-normal" value={description} onChange={(event) => setDescription(event.target.value)} /></label>
      <label className="grid gap-1 text-sm font-medium">First variant name<input className="rounded-xl border border-border p-3 font-normal" required value={initialVariant.name} onChange={(event) => setInitialVariant({ ...initialVariant, name: event.target.value })} /></label>
      <label className="grid gap-1 text-sm font-medium">First variant specs<input className="rounded-xl border border-border p-3 font-normal" required value={initialVariant.specs} onChange={(event) => setInitialVariant({ ...initialVariant, specs: event.target.value })} /></label>
      <button className="w-fit rounded-xl bg-primary px-4 py-3 font-semibold text-white">Add product</button>
    </form>}
    {mutationError && <p className="mt-4 text-sm text-red-700" role="alert">{mutationError}</p>}
    <div className="mt-6 grid gap-4">
      {loading && <PageState title="Loading products" description="Fetching the latest catalogue." />}
      {!loading && error && <PageState title="Could not load products" description={error} actionLabel="Try again" onAction={() => void load()} />}
      {!loading && !error && products.length === 0 && <PageState title="No products yet" description={canCreate ? 'Create the first product to start the catalogue.' : 'Your admin team has not added any products yet.'} />}
      {!loading && !error && products.map((product) => {
        const draft = variantDrafts[product.id] ?? { name: '', specs: '' }
        return <section className="rounded-2xl border border-border bg-surface p-5" key={product.id}>
          <h3 className="text-lg font-semibold">{product.name}</h3>
          {product.description && <p className="mt-1 text-sm text-muted-text">{product.description}</p>}
          <div className="mt-4 space-y-2">{product.variants.length ? product.variants.map((variant) => <div className="rounded-xl bg-background p-3" key={variant.id}><strong>{variant.name}</strong><span className="ml-2 text-sm text-muted-text">{variant.specs}</span></div>) : <p className="text-sm text-muted-text">No variants added yet.</p>}</div>
          {canCreate && <form aria-label={`Add variant to ${product.name}`} className="mt-4 grid gap-2 sm:grid-cols-[1fr_1.5fr_auto]" onSubmit={(event) => void createVariant(event, product.id)}>
            <input aria-label={`Variant name for ${product.name}`} className="rounded-xl border border-border p-3" placeholder="Variant name" required value={draft.name} onChange={(event) => updateVariant(product.id, 'name', event.target.value)} />
            <input aria-label={`Variant specs for ${product.name}`} className="rounded-xl border border-border p-3" placeholder="Specs" required value={draft.specs} onChange={(event) => updateVariant(product.id, 'specs', event.target.value)} />
            <button className="rounded-xl bg-dark px-4 py-3 font-semibold text-white">Add variant</button>
          </form>}
        </section>
      })}
    </div>
  </div>
}
