import { FormEvent, useCallback, useEffect, useState } from 'react'
import { PageState } from '../../components/PageState'
import { ApiError, apiRequest } from '../../lib/api'

type Lineup = { id: number; lineup_identifier: string; product_count: number }
type Question = { id: number; question_number: number; question: string; answer: string | null; evaluation: string | null }
type Assignment = { id: number; product_lineup_id: number; lineup_identifier: string; status: string | null; questions?: Question[] }

export function AssignmentsPage() {
  const [lineups, setLineups] = useState<Lineup[]>([])
  const [lineupId, setLineupId] = useState('')
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [active, setActive] = useState<Assignment>()
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string>()

  async function loadLineups() {
    try {
      const items = await apiRequest<Lineup[]>('/api/v1/product-lineups')
      setLineups(items); if (items[0]) setLineupId(String(items[0].id))
    } catch (caught) { setError(caught instanceof ApiError ? caught.message : 'Product lineups could not be loaded.') }
    finally { setLoading(false) }
  }
  const loadAssignments = useCallback(async (id = lineupId) => {
    if (!id) return
    try { setAssignments(await apiRequest<Assignment[]>(`/api/v1/assignments?product_lineup_id=${id}`)) }
    catch (caught) { setError(caught instanceof ApiError ? caught.message : 'Assignments could not be loaded.') }
  }, [lineupId])
  useEffect(() => { void loadLineups() }, [])
  useEffect(() => { if (lineupId) void loadAssignments() }, [lineupId, loadAssignments])

  async function createAssignment() {
    setBusy(true); setError(undefined)
    try { const created = await apiRequest<Assignment>('/api/v1/assignments', { method: 'POST', body: { product_lineup_id: Number(lineupId) } }); setAssignments((items) => [created, ...items]) }
    catch (caught) { setError(caught instanceof ApiError ? caught.message : 'Assignment could not be created.') }
    finally { setBusy(false) }
  }
  async function startAssignment(item: Assignment) {
    setBusy(true); setError(undefined)
    try { const detail = await apiRequest<Assignment>(`/api/v1/assignments/${item.id}`); setActive(detail); setAnswers(Object.fromEntries((detail.questions ?? []).map((question) => [question.id, '']))) }
    catch (caught) { setError(caught instanceof ApiError ? caught.message : 'Assignment could not be opened.') }
    finally { setBusy(false) }
  }
  async function submit(event: FormEvent) {
    event.preventDefault(); if (!active) return
    setBusy(true); setError(undefined)
    try { const result = await apiRequest<Assignment>(`/api/v1/assignments/${active.id}/submit`, { method: 'POST', body: { answers: (active.questions ?? []).map((q) => ({ question_id: q.id, answer: answers[q.id] ?? '' })) } }); setActive(result); await loadAssignments() }
    catch (caught) { setError(caught instanceof ApiError ? caught.message : 'Assignment could not be submitted.') }
    finally { setBusy(false) }
  }
  if (loading) return <div className="mx-auto max-w-[1000px] px-6 py-8 lg:px-10"><PageState title="Loading assignments" description="Preparing your product lineups." /></div>
  if (!lineups.length) return <div className="mx-auto max-w-[1000px] px-6 py-8 lg:px-10"><PageState title="No product lineups available" description="Ask an administrator to add a product lineup first." /></div>
  return <div className="mx-auto max-w-[1000px] px-6 py-8 lg:px-10">
    <p className="text-sm font-medium text-primary">Knowledge check</p><h2 className="mt-2 text-3xl font-semibold tracking-[-0.05em]">Assignments</h2><p className="mt-2 max-w-xl text-sm leading-6 text-muted-text">Choose a product lineup and complete a generated knowledge check in one session.</p>
    <section className="mt-6 grid gap-3 rounded-2xl border border-border bg-surface p-5 sm:grid-cols-[1fr_auto] sm:items-end"><label className="grid gap-1 text-sm font-medium">Product lineup<select aria-label="Product lineup" className="rounded-xl border border-border bg-surface p-3 font-normal" value={lineupId} onChange={(e) => { setLineupId(e.target.value); setActive(undefined) }}>{lineups.map((lineup) => <option key={lineup.id} value={lineup.id}>{lineup.lineup_identifier} ({lineup.product_count} products)</option>)}</select></label><button className="rounded-xl bg-primary px-4 py-3 font-semibold text-white disabled:opacity-60" disabled={busy} onClick={() => void createAssignment()} type="button">Create assignment</button></section>
    {error && <p className="mt-4 text-sm text-red-700" role="alert">{error}</p>}
    {!active && <section className="mt-6 grid gap-3">{assignments.length ? assignments.map((item) => <article className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-surface p-5" key={item.id}><div><h3 className="font-semibold">{item.lineup_identifier} assignment</h3><p className="mt-1 text-sm text-muted-text">{item.status === 'completed' ? 'Completed' : 'Ready to start'}</p></div>{item.status !== 'completed' && <button className="rounded-xl bg-dark px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60" disabled={busy} onClick={() => void startAssignment(item)} type="button">Start assignment</button>}{item.status === 'completed' && <button className="rounded-xl border border-border px-4 py-2.5 text-sm font-semibold" disabled={busy} onClick={() => void startAssignment(item)} type="button">View evaluation</button>}</article>) : <PageState title="No assignments for this lineup" description="Create an assignment to generate a fresh knowledge check." />}</section>}
    {active && active.status !== 'completed' && <form aria-label="Assignment session" className="mt-6 grid gap-5" onSubmit={submit}><div className="rounded-2xl border border-light-purple bg-light-purple/40 p-5"><p className="text-xs font-semibold uppercase tracking-[0.08em] text-primary">Mock-generated questions</p><p className="mt-2 text-sm text-muted-text">PENDING AI REPLACEMENT: questions are generated from the selected lineup for now.</p></div>{(active.questions ?? []).map((question) => <label className="grid gap-2 rounded-2xl border border-border bg-surface p-5 text-sm font-medium" key={question.id}><span>{question.question_number}. {question.question}</span><textarea aria-label={`Answer ${question.question_number}`} className="min-h-28 rounded-xl border border-border p-3 font-normal" required value={answers[question.id] ?? ''} onChange={(e) => setAnswers((current) => ({ ...current, [question.id]: e.target.value }))} /></label>)}<button className="w-fit rounded-xl bg-primary px-5 py-3 font-semibold text-white disabled:opacity-60" disabled={busy} type="submit">{busy ? 'Evaluating…' : 'Submit assignment'}</button></form>}
    {active?.status === 'completed' && <section aria-label="Assignment evaluation" className="mt-6 grid gap-4"><div className="rounded-2xl border border-light-purple bg-light-purple/40 p-5"><p className="text-xs font-semibold uppercase tracking-[0.08em] text-primary">Question evaluation</p><p className="mt-2 text-sm text-muted-text">PENDING AI REPLACEMENT: feedback is mocked and subjective for now.</p></div>{(active.questions ?? []).map((question) => <article className="rounded-2xl border border-border bg-surface p-5" key={question.id}><h3 className="font-semibold">{question.question_number}. {question.question}</h3><p className="mt-2 text-sm text-muted-text">Your answer: {question.answer}</p><p className="mt-3 text-sm"><strong>Feedback:</strong> {question.evaluation}</p></article>)}</section>}
  </div>
}
