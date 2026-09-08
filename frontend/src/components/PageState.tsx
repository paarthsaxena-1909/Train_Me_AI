type PageStateProps = { title: string; description: string; actionLabel?: string; onAction?: () => void }

export function PageState({ title, description, actionLabel, onAction }: PageStateProps) {
  return (
    <section className="rounded-2xl border border-border bg-surface p-8 text-center">
      <div className="mx-auto mb-4 grid h-11 w-11 place-items-center rounded-xl bg-light-purple text-primary">✦</div>
      <h2 className="text-xl font-semibold tracking-[-0.03em] text-main-text">{title}</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-muted-text">{description}</p>
      {actionLabel && <button className="mt-6 rounded-xl bg-dark px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-primary" onClick={onAction} type="button">{actionLabel}</button>}
    </section>
  )
}
