import { useQuery } from '@tanstack/react-query'
import { useDispatch, useSelector } from 'react-redux'
import type { AppDispatch, RootState } from './app/store'
import { decrement, increment } from './features/counter/counterSlice'

const loadStarterMessage = async () => 'TanStack Query is connected.'

function App() {
  const dispatch = useDispatch<AppDispatch>()
  const count = useSelector((state: RootState) => state.counter.value)
  const { data: queryMessage, isLoading } = useQuery({
    queryKey: ['starter-message'],
    queryFn: loadStarterMessage,
  })

  return (
    <main className="min-h-screen bg-mist px-6 py-12 text-ink">
      <div className="mx-auto max-w-4xl">
        <div className="mb-10 max-w-2xl">
          <p className="mb-3 text-sm font-semibold uppercase tracking-[0.24em] text-coral">
            Frontend foundation
          </p>
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
            Train Me AI starts here.
          </h1>
          <p className="mt-5 text-lg leading-8 text-slate-600">
            React, Redux Toolkit, TanStack Query, and Tailwind CSS are ready for the next feature.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          <section className="rounded-3xl bg-white p-7 shadow-xl shadow-slate-200/60 ring-1 ring-slate-200">
            <p className="text-sm font-medium text-slate-500">Redux Toolkit</p>
            <h2 className="mt-2 text-2xl font-semibold">Local state counter</h2>
            <p className="mt-3 text-5xl font-bold text-coral">{count}</p>
            <div className="mt-6 flex gap-3">
              <button
                className="rounded-xl bg-ink px-4 py-2 font-semibold text-white transition hover:bg-slate-700"
                onClick={() => dispatch(decrement())}
                type="button"
              >
                − Decrement
              </button>
              <button
                className="rounded-xl bg-coral px-4 py-2 font-semibold text-white transition hover:bg-red-500"
                onClick={() => dispatch(increment())}
                type="button"
              >
                + Increment
              </button>
            </div>
          </section>

          <section className="rounded-3xl bg-ink p-7 text-white shadow-xl shadow-slate-300/50">
            <p className="text-sm font-medium text-slate-300">TanStack Query</p>
            <h2 className="mt-2 text-2xl font-semibold">Server state boundary</h2>
            <p className="mt-6 rounded-2xl bg-white/10 p-4 text-slate-200">
              {isLoading ? 'Loading starter query…' : queryMessage}
            </p>
          </section>
        </div>
      </div>
    </main>
  )
}

export default App
