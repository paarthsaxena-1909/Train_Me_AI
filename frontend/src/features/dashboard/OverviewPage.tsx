import type { Role } from '../../lib/types'
export function OverviewPage({ role }: { role: Role }) {
  return <div className="mx-auto max-w-[1000px] px-6 py-10 lg:px-10"><p className="text-sm font-medium text-primary">Welcome back</p><h2 className="mt-2 text-3xl font-semibold tracking-[-0.05em]">Your {role} workspace</h2><p className="mt-3 max-w-xl text-muted-text">Use Products to manage the catalogue available to your team.</p></div>
}
