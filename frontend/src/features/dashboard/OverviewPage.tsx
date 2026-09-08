import { Icon } from '../../components/Icon'
import type { Role } from '../../lib/types'

export function OverviewPage({ role }: { role: Role }) {
  const admin = role === 'admin'
  const stats = admin
    ? [['Active agents', '24', '+12%'], ['Playbooks created', '86', '+8%'], ['Avg. quality score', '92%', '+4%']]
    : [['My conversations', '48', '+18%'], ['Playbooks completed', '17', '+6%'], ['Quality score', '94%', '+3%']]

  return (
    <div className="mx-auto max-w-[1200px] px-6 py-8 lg:px-10 lg:py-10">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div><p className="mb-2 text-sm font-medium text-primary">A clear view of the work ahead.</p><h2 className="text-3xl font-semibold tracking-[-0.05em]">Your workspace signal</h2></div>
        <button className="rounded-xl bg-dark px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-primary" type="button">Create playbook</button>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {stats.map(([label, value, change], index) => <section className="rounded-2xl border border-border bg-surface p-5" key={label}><div className="mb-5 flex items-center justify-between"><p className="text-sm text-muted-text">{label}</p><span className={`rounded-full px-2 py-1 text-xs font-semibold ${index === 1 ? 'bg-pink-accent text-dark' : 'bg-light-purple text-dark'}`}>{change}</span></div><p className="text-3xl font-semibold tracking-[-0.05em]">{value}</p><div className="mt-5 h-1.5 overflow-hidden rounded-full bg-background"><div className={`h-full rounded-full ${index === 1 ? 'bg-orange' : 'bg-primary'}`} style={{ width: String(70 + index * 9) + '%' }} /></div></section>)}
      </div>
      <div className="mt-8 grid gap-5 xl:grid-cols-[1.35fr_0.65fr]">
        <section className="rounded-2xl border border-border bg-surface p-6"><div className="mb-8"><h3 className="font-semibold">Activity overview</h3><p className="mt-1 text-sm text-muted-text">Workspace performance over the last 7 days</p></div><div className="flex h-48 items-end gap-3 sm:gap-5">{[42, 58, 46, 74, 62, 88, 72].map((height, index) => <div className="flex h-full flex-1 flex-col items-center justify-end gap-3" key={index}><div className={`w-full rounded-t-lg ${index === 5 ? 'bg-primary' : 'bg-light-purple'}`} style={{ height: String(height) + '%' }} /><span className="text-xs text-muted-text">{['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index]}</span></div>)}</div></section>
        <section className="rounded-2xl border border-border bg-dark p-6 text-white"><div className="mb-7 flex items-center justify-between"><h3 className="font-semibold">Quick start</h3><span className="rounded-full bg-orange px-2 py-1 text-[10px] font-semibold text-white">{role.toUpperCase()}</span></div><p className="max-w-[240px] text-2xl font-semibold leading-tight tracking-[-0.04em]">Keep the team moving forward.</p><p className="mt-3 text-sm leading-6 text-white/55">Pick up where you left off or create something new for your workspace.</p><button className="mt-8 flex items-center gap-2 text-sm font-semibold text-light-purple" type="button">Browse playbooks <Icon name="arrow" size={16} /></button></section>
      </div>
    </div>
  )
}
